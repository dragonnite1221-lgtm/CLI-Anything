# ruff: noqa: F403, F405, E501
from .gui_macro_base import *  # noqa: F403


class GUIMacroBackendMixin0:
    """Replay precompiled GUI automation sequences."""
    name = "gui_macro"
    priority = 80
    def execute(self, step: MacroStep, params: dict, context: BackendContext) -> StepResult:
        t0 = time.time()
        action = step.action
        step_params = substitute(step.params, params)

        if context.dry_run:
            return StepResult(
                success=True,
                output={"dry_run": True, "action": action},
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        if action != "replay":
            return StepResult(
                success=False,
                error=f"GUIMacroBackend: unknown action '{action}'. Expected 'replay'.",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        return self._replay(step_params, context, t0)
    def is_available(self) -> bool:
        """Available when at least one automation library is present."""
        for lib in ("pyautogui", "pynput"):
            try:
                __import__(lib)
                return True
            except ImportError:
                pass
        return False
    def _replay(self, p: dict, context: BackendContext, t0: float) -> StepResult:
        """Load and replay a compiled macro file."""
        macro_file = p.get("macro_file", "")
        if not macro_file:
            return StepResult(
                success=False,
                error="GUIMacroBackend.replay: 'macro_file' param is required.",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        macro_path = Path(macro_file)
        if not macro_path.is_file():
            return StepResult(
                success=False,
                error=f"GUIMacroBackend: compiled macro not found: {macro_file}",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        try:
            with open(macro_path, encoding="utf-8") as f:
                macro_blob = json.load(f)
        except Exception as exc:
            return StepResult(
                success=False,
                error=f"GUIMacroBackend: failed to load macro file: {exc}",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        layout_strict: bool = p.get("layout_strict", False)
        if layout_strict:
            check = self._check_layout(macro_blob)
            if check:
                return StepResult(
                    success=False,
                    error=f"GUIMacroBackend: layout mismatch — {check}",
                    backend_used=self.name,
                    duration_ms=(time.time() - t0) * 1000,
                )

        try:
            steps_run = self._execute_steps(macro_blob.get("steps", []), context)
            return StepResult(
                success=True,
                output={"steps_executed": steps_run, "macro_file": macro_file},
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )
        except Exception as exc:
            return StepResult(
                success=False,
                error=f"GUIMacroBackend.replay: {exc}",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )
