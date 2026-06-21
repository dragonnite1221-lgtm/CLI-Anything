# ruff: noqa: F403, F405, E501
from .runtime_base import *  # noqa: F403


@dataclass
class ExecutionResult:
    success: bool
    macro_name: str
    output: dict = field(default_factory=dict)
    error: str = ""
    step_results: list[StepResult] = field(default_factory=list)
    telemetry: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "macro_name": self.macro_name,
            "output": self.output,
            "error": self.error,
            "telemetry": self.telemetry,
            "steps": [s.to_dict() for s in self.step_results],
        }


def _check_condition(cond: MacroCondition, resolved_params: dict) -> Optional[str]:
    """Evaluate one condition.

    Returns None if the condition passes, or an error string if it fails.
    """
    ctype = cond.type
    args = substitute(cond.args, resolved_params)

    if ctype == "file_exists":
        path = str(args)
        if not os.path.exists(path):
            return f"file_exists: '{path}' not found."
        return None

    elif ctype == "file_size_gt":
        if not isinstance(args, (list, tuple)) or len(args) < 2:
            return f"file_size_gt: expected [path, min_bytes], got {args!r}"
        path, min_bytes = str(args[0]), int(args[1])
        if not os.path.exists(path):
            return f"file_size_gt: '{path}' not found."
        size = os.path.getsize(path)
        if size <= min_bytes:
            return f"file_size_gt: '{path}' is {size} bytes, expected > {min_bytes}."
        return None

    elif ctype == "process_running":
        name = str(args)
        # Try pgrep first, then psutil
        import shutil
        import subprocess

        if shutil.which("pgrep"):
            r = subprocess.run(["pgrep", "-x", name], capture_output=True)
            if r.returncode == 0:
                return None
            return f"process_running: '{name}' not found (pgrep)."
        try:
            import psutil

            for proc in psutil.process_iter(["name"]):
                if proc.info["name"] == name:
                    return None
            return f"process_running: '{name}' not found."
        except ImportError:
            # Can't verify — let it pass with a warning
            return None

    elif ctype == "env_var":
        name = str(args)
        if name not in os.environ:
            return f"env_var: '{name}' is not set in the environment."
        return None

    elif ctype == "always":
        if str(args).lower() in ("false", "0", "no"):
            return "always: false condition."
        return None

    else:
        # Unknown condition type — warn but don't block
        return None
