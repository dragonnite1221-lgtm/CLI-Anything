# ruff: noqa: F403, F405, E501
from .visual_anchor_base import *  # noqa: F403
from .visual_anchor_p0 import _load_image_as_array  # noqa: F401,E501
from .visual_anchor_p1 import _mouse_click, _wait_for_template  # noqa: F401,E501


class VisualAnchorBackendMixin0:
    """Find UI elements by image template and interact with them."""
    name = "visual_anchor"
    priority = 75  # between file_transform(70) and gui_macro(80)
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
            "click_image":    self._click_image,
            "click_relative": self._click_relative,
            "wait_image":     self._wait_image,
            "type_text":      self._type_text,
            "hotkey":         self._hotkey,
            "scroll":         self._scroll,
            "drag":           self._drag,
            "drag_relative":  self._drag_relative,
            "capture_region": self._capture_region,
        }

        handler = dispatch.get(action)
        if handler is None:
            return StepResult(
                success=False,
                error=f"VisualAnchorBackend: unknown action '{action}'. "
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
                error=f"VisualAnchorBackend.{action}: {exc}",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )
    def is_available(self) -> bool:
        for pkg in ("mss", "numpy", "PIL", "pynput"):
            try:
                __import__(pkg if pkg != "PIL" else "PIL.Image")
            except ImportError:
                return False
        return True
    def _click_image(self, p: dict, context: BackendContext) -> dict:
        """Find template on screen and click its center."""
        template_path = p.get("template", "")
        if not template_path or not Path(template_path).is_file():
            raise FileNotFoundError(
                f"Template image not found: '{template_path}'. "
                "Use 'macro record' or 'capture_region' to create one."
            )

        confidence = float(p.get("confidence", 0.85))
        timeout_ms = int(p.get("timeout_ms", 5000))
        button = p.get("button", "left")   # left | right | middle
        double = bool(p.get("double", False))

        template_arr = _load_image_as_array(template_path)
        match = _wait_for_template(template_arr, confidence, timeout_ms)

        if match is None:
            raise RuntimeError(
                f"Template not found on screen after {timeout_ms}ms: {template_path} "
                f"(confidence={confidence})"
            )

        cx, cy, score = match
        _mouse_click(cx, cy, button=button, double=double)

        return {
            "clicked_at": [cx, cy],
            "match_score": round(score, 4),
            "template": template_path,
        }
