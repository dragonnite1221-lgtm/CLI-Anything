# ruff: noqa: F403, F405, E501
from .visual_anchor_base import *  # noqa: F403
from .visual_anchor_p0 import _load_image_as_array, _require_pynput, _screenshot_as_array  # noqa: F401,E501
from .visual_anchor_p1 import _get_window_bounds, _wait_for_template  # noqa: F401,E501
from .visual_anchor_p2 import _mouse_drag  # noqa: F401,E501


class VisualAnchorBackendMixin2:
    def _scroll(self, p: dict, context: BackendContext) -> dict:
        """Scroll at the position of a template image."""
        template_path = p.get("template", "")
        dx = int(p.get("dx", 0))
        dy = int(p.get("dy", -3))   # negative = scroll down
        timeout_ms = int(p.get("timeout_ms", 5000))
        confidence = float(p.get("confidence", 0.85))

        if template_path and Path(template_path).is_file():
            template_arr = _load_image_as_array(template_path)
            match = _wait_for_template(template_arr, confidence, timeout_ms)
            if match is None:
                raise RuntimeError(f"Template not found: {template_path}")
            cx, cy, _ = match
        else:
            # Scroll at current mouse position
            mouse_mod, _ = _require_pynput()
            pos = mouse_mod.Controller().position
            cx, cy = int(pos[0]), int(pos[1])

        mouse_mod, _ = _require_pynput()
        mouse_ctrl = mouse_mod.Controller()
        mouse_ctrl.position = (cx, cy)
        mouse_ctrl.scroll(dx, dy)

        return {"scrolled_at": [cx, cy], "dx": dx, "dy": dy}
    def _drag(self, p: dict, context: BackendContext) -> dict:
        """Drag from one template image to another (or to absolute coords).

        Params:
          from_template:  path to template image for drag start (optional)
          to_template:    path to template image for drag end (optional)
          from_x / from_y: fallback absolute coords if no from_template
          to_x   / to_y:   fallback absolute coords if no to_template
          button:          left | right | middle (default left)
          duration_ms:     how long to hold during drag (default 200)
          confidence:      template match threshold (default 0.85)
          timeout_ms:      how long to wait for templates (default 5000)
        """
        button = p.get("button", "left")
        duration_ms = int(p.get("duration_ms", 200))
        confidence = float(p.get("confidence", 0.85))
        timeout_ms = int(p.get("timeout_ms", 5000))

        # Resolve start position
        from_tmpl = p.get("from_template", "")
        if from_tmpl and Path(from_tmpl).is_file():
            tmpl = _load_image_as_array(from_tmpl)
            match = _wait_for_template(tmpl, confidence, timeout_ms)
            if match is None:
                raise RuntimeError(f"drag: from_template not found: {from_tmpl}")
            fx, fy = match[0], match[1]
        else:
            fx = int(p.get("from_x", 0))
            fy = int(p.get("from_y", 0))

        # Resolve end position
        to_tmpl = p.get("to_template", "")
        if to_tmpl and Path(to_tmpl).is_file():
            tmpl = _load_image_as_array(to_tmpl)
            match = _wait_for_template(tmpl, confidence, timeout_ms)
            if match is None:
                raise RuntimeError(f"drag: to_template not found: {to_tmpl}")
            tx, ty = match[0], match[1]
        else:
            tx = int(p.get("to_x", fx))
            ty = int(p.get("to_y", fy))

        _mouse_drag(fx, fy, tx, ty, button=button, duration_ms=duration_ms)
        return {"dragged_from": [fx, fy], "dragged_to": [tx, ty]}
    def _drag_relative(self, p: dict, context: BackendContext) -> dict:
        """Drag within a window using fractional coordinates.

        Params:
          window_title:     partial window title (uses focused window if empty)
          from_x_pct:       drag start x as fraction of window width
          from_y_pct:       drag start y as fraction of window height
          to_x_pct:         drag end x as fraction of window width
          to_y_pct:         drag end y as fraction of window height
          button:           left | right | middle (default left)
          duration_ms:      hold duration in ms (default 200)
        """
        title = p.get("window_title", "")
        button = p.get("button", "left")
        duration_ms = int(p.get("duration_ms", 200))

        if title:
            bounds = _get_window_bounds(title)
            if bounds is None:
                raise RuntimeError(f"drag_relative: window not found: '{title}'")
            wx, wy = bounds["x"], bounds["y"]
            ww, wh = bounds["width"], bounds["height"]
        else:
            _, monitor = _screenshot_as_array()
            wx, wy = 0, 0
            ww, wh = monitor["width"], monitor["height"]

        fx = int(wx + ww * float(p.get("from_x_pct", 0.0)))
        fy = int(wy + wh * float(p.get("from_y_pct", 0.0)))
        tx = int(wx + ww * float(p.get("to_x_pct", 1.0)))
        ty = int(wy + wh * float(p.get("to_y_pct", 1.0)))

        _mouse_drag(fx, fy, tx, ty, button=button, duration_ms=duration_ms)
        return {
            "dragged_from": [fx, fy],
            "dragged_to": [tx, ty],
            "from_pct": [p.get("from_x_pct"), p.get("from_y_pct")],
            "to_pct": [p.get("to_x_pct"), p.get("to_y_pct")],
        }
