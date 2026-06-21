# ruff: noqa: F403, F405, E501
from .semantic_ui_base import *  # noqa: F403
from .semantic_ui_p0 import _atspi_available, _xdotool_key, _xdotool_type  # noqa: F401,E501


class SemanticUIBackendMixin0:
    """Drive applications through semantic (accessibility) controls."""
    name = "semantic_ui"
    priority = 50
    def execute(self, step: MacroStep, params: dict, context: BackendContext) -> StepResult:
        t0 = time.time()
        action = step.action
        p = substitute(step.params, params)

        if context.dry_run:
            return StepResult(
                success=True,
                output={"dry_run": True, "action": action},
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        dispatch = {
            "shortcut":        self._shortcut,
            "type_text":       self._type_text,
            "menu_click":      self._menu_click,
            "button_click":    self._button_click,
            "wait_for_window": self._wait_for_window,
            "focus_window":    self._focus_window,
            "get_controls":    self._get_controls,
        }

        handler = dispatch.get(action)
        if handler is None:
            return StepResult(
                success=False,
                error=f"SemanticUIBackend: unknown action '{action}'. "
                      f"Available: {sorted(dispatch)}",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        try:
            output = handler(p, context)
            return StepResult(
                success=True,
                output=output or {},
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )
        except Exception as exc:
            return StepResult(
                success=False,
                error=f"SemanticUIBackend.{action}: {exc}",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )
    def is_available(self) -> bool:
        if _SYSTEM == "Linux":
            return _atspi_available() or bool(shutil.which("xdotool"))
        elif _SYSTEM == "Darwin":
            return bool(shutil.which("osascript"))
        elif _SYSTEM == "Windows":
            try:
                import pywinauto  # noqa: F401
                return True
            except ImportError:
                return False
        return False
    def _shortcut(self, p: dict, context: BackendContext) -> dict:
        keys: str = p.get("keys", "")
        if not keys:
            raise ValueError("shortcut requires 'keys' param.")

        if _SYSTEM == "Linux":
            _xdotool_key(keys)
            return {"keys": keys, "method": "xdotool"}

        elif _SYSTEM == "Darwin":
            # Use pynput (cross-platform) or AppleScript key code
            from cli_anything.macrocli.backends.visual_anchor import VisualAnchorBackend
            from cli_anything.macrocli.core.macro_model import MacroStep as MS
            va = VisualAnchorBackend()
            step = MS(id="x", backend="visual_anchor", action="hotkey", params={"keys": keys})
            result = va._hotkey({"keys": keys}, context)
            return result

        elif _SYSTEM == "Windows":
            import pywinauto.keyboard as kb
            # Convert ctrl+s → {VK_CONTROL}s
            kb.send_keys(keys.replace("+", ""))
            return {"keys": keys, "method": "pywinauto"}

        raise NotImplementedError(f"shortcut not implemented for {_SYSTEM}")
    def _type_text(self, p: dict, context: BackendContext) -> dict:
        text: str = p.get("text", "")
        if not text:
            raise ValueError("type_text requires 'text' param.")

        if _SYSTEM == "Linux":
            _xdotool_type(text)
            return {"typed": len(text), "method": "xdotool"}

        # macOS / Windows: fall through to visual_anchor type_text
        from cli_anything.macrocli.backends.visual_anchor import VisualAnchorBackend
        va = VisualAnchorBackend()
        return va._type_text(p, context)
