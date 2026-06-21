# ruff: noqa: F403, F405, E501
from .visual_anchor_base import *  # noqa: F403
from .visual_anchor_p0 import _load_image_as_array, _require_pynput, _screenshot_as_array  # noqa: F401,E501
from .visual_anchor_p1 import _get_window_bounds, _mouse_click, _wait_for_template  # noqa: F401,E501


class VisualAnchorBackendMixin1:
    def _click_relative(self, p: dict, context: BackendContext) -> dict:
        """Click at a fractional position within a named window."""
        title = p.get("window_title", "")
        x_pct = float(p.get("x_pct", 0.5))
        y_pct = float(p.get("y_pct", 0.5))
        button = p.get("button", "left")
        double = bool(p.get("double", False))

        if title:
            bounds = _get_window_bounds(title)
            if bounds is None:
                raise RuntimeError(
                    f"Window not found: '{title}'. "
                    "Make sure the application is open and the title matches."
                )
            cx = int(bounds["x"] + bounds["width"] * x_pct)
            cy = int(bounds["y"] + bounds["height"] * y_pct)
        else:
            # Relative to full screen
            _, monitor = _screenshot_as_array()
            cx = int(monitor["width"] * x_pct)
            cy = int(monitor["height"] * y_pct)

        _mouse_click(cx, cy, button=button, double=double)
        return {"clicked_at": [cx, cy], "x_pct": x_pct, "y_pct": y_pct}
    def _wait_image(self, p: dict, context: BackendContext) -> dict:
        """Wait until a template image appears on screen."""
        template_path = p.get("template", "")
        if not template_path or not Path(template_path).is_file():
            raise FileNotFoundError(f"Template image not found: '{template_path}'")

        confidence = float(p.get("confidence", 0.85))
        timeout_ms = int(p.get("timeout_ms", 10000))

        template_arr = _load_image_as_array(template_path)
        match = _wait_for_template(template_arr, confidence, timeout_ms)

        if match is None:
            raise RuntimeError(
                f"Template never appeared within {timeout_ms}ms: {template_path}"
            )

        cx, cy, score = match
        return {"found_at": [cx, cy], "match_score": round(score, 4)}
    def _type_text(self, p: dict, context: BackendContext) -> dict:
        """Type a string using keyboard injection."""
        text = p.get("text", "")
        interval_ms = int(p.get("interval_ms", 30))
        if not text:
            raise ValueError("type_text requires 'text' param.")

        _, keyboard_mod = _require_pynput()
        ctrl = keyboard_mod.Controller()

        import time as _time
        for char in text:
            ctrl.press(char)
            ctrl.release(char)
            if interval_ms > 0:
                _time.sleep(interval_ms / 1000.0)

        return {"typed": len(text), "text_preview": text[:40]}
    def _hotkey(self, p: dict, context: BackendContext) -> dict:
        """Send a keyboard shortcut (e.g. ctrl+shift+e)."""
        keys_str = p.get("keys", "")
        if not keys_str:
            raise ValueError("hotkey requires 'keys' param (e.g. 'ctrl+s').")

        _, keyboard_mod = _require_pynput()
        Key = keyboard_mod.Key
        ctrl = keyboard_mod.Controller()

        # Parse keys: ctrl+shift+e → [Key.ctrl, Key.shift, 'e']
        key_objects = []
        for k in keys_str.split("+"):
            k = k.strip().lower()
            # Map common names to pynput Key enum
            mapping = {
                "ctrl": Key.ctrl, "control": Key.ctrl,
                "shift": Key.shift,
                "alt": Key.alt,
                "cmd": Key.cmd, "super": Key.cmd, "win": Key.cmd,
                "enter": Key.enter, "return": Key.enter,
                "tab": Key.tab,
                "esc": Key.esc, "escape": Key.esc,
                "space": Key.space,
                "backspace": Key.backspace,
                "delete": Key.delete,
                "up": Key.up, "down": Key.down,
                "left": Key.left, "right": Key.right,
                "home": Key.home, "end": Key.end,
                "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
                "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
                "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
            }
            if k in mapping:
                key_objects.append(mapping[k])
            elif len(k) == 1:
                key_objects.append(k)
            else:
                raise ValueError(f"Unknown key name: '{k}'")

        # Press all, then release all in reverse
        for k in key_objects:
            ctrl.press(k)
        for k in reversed(key_objects):
            ctrl.release(k)

        return {"hotkey": keys_str}
