# ruff: noqa: F403, F405, E501
from .unrealinsights_backend_base import *  # noqa: F403

# fmt: off
from .unrealinsights_backend_p1 import _normalize_path, resolve_binary_from_engine_root, resolve_engine_root  # noqa: E402,E501
from .unrealinsights_backend_p2 import build_engine_program  # noqa: E402,E501
# fmt: on


def ensure_engine_unrealinsights(
    engine_root: str | Path,
    *,
    build_if_missing: bool = True,
    configuration: str = "Development",
    platform: str = "Win64",
    timeout: float | None = None,
) -> dict[str, object]:
    """Resolve UnrealInsights.exe for a given engine root, building it if requested."""
    root = resolve_engine_root(engine_root)
    trace_server = resolve_binary_from_engine_root(
        TRACE_SERVER_BINARY_NAME,
        root,
        required=False,
    )
    existing = resolve_binary_from_engine_root(
        INSIGHTS_BINARY_NAME,
        root,
        required=False,
    )
    result = {
        "engine_root": str(root),
        "trace_server": trace_server,
        "build_attempted": False,
        "build": None,
    }
    if existing["available"]:
        result["insights"] = existing
        return result

    if not build_if_missing:
        raise RuntimeError(
            f"{INSIGHTS_BINARY_NAME} not found under engine root: {root}"
        )

    build = build_engine_program(
        root,
        "UnrealInsights",
        platform=platform,
        configuration=configuration,
        timeout=timeout,
    )
    result["build_attempted"] = True
    result["build"] = build
    if not build["succeeded"]:
        raise RuntimeError(f"Failed to build UnrealInsights for engine root: {root}")

    result["insights"] = resolve_binary_from_engine_root(
        INSIGHTS_BINARY_NAME, root, required=True
    )
    return result


def build_insights_command(
    insights_exe: str,
    trace_path: str,
    exec_on_complete: str,
    log_path: str,
) -> list[str]:
    """Build the UnrealInsights.exe command line."""
    return [
        _normalize_path(insights_exe),
        f"-OpenTraceFile={_normalize_path(trace_path)}",
        f"-ABSLOG={_normalize_path(log_path)}",
        "-AutoQuit",
        "-NoUI",
        f"-ExecOnAnalysisCompleteCmd={exec_on_complete}",
        "-log",
    ]


def _quote_cmd_value(value: str) -> str:
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'


def build_insights_command_line(
    insights_exe: str,
    trace_path: str,
    exec_on_complete: str,
    log_path: str,
) -> str:
    """Build a raw Windows command line for UnrealInsights.exe.

    This avoids CreateProcess argv wrapping the whole -ExecOnAnalysisCompleteCmd
    argument in outer quotes, which older UnrealInsights builds fail to parse.
    """
    exe = _quote_cmd_value(_normalize_path(insights_exe))
    trace = _quote_cmd_value(_normalize_path(trace_path))
    log = _quote_cmd_value(_normalize_path(log_path))
    exec_value = _quote_cmd_value(exec_on_complete)
    return (
        f"{exe} "
        f"-OpenTraceFile={trace} "
        f"-ABSLOG={log} "
        f"-AutoQuit -NoUI "
        f"-ExecOnAnalysisCompleteCmd={exec_value} "
        f"-log"
    )


def run_process(
    command: list[str] | str, timeout: float | None = None, wait: bool = True
) -> dict[str, object]:
    """Run or launch a subprocess and return structured execution metadata."""
    if wait:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return {
                "command": command,
                "waited": True,
                "timed_out": False,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "pid": None,
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "command": command,
                "waited": True,
                "timed_out": True,
                "exit_code": None,
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "",
                "pid": None,
            }

    process = subprocess.Popen(command)
    return {
        "command": command,
        "waited": False,
        "timed_out": False,
        "exit_code": None,
        "stdout": None,
        "stderr": None,
        "pid": process.pid,
    }
