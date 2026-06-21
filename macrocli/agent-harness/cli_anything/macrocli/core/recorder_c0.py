# ruff: noqa: F403, F405, E501
from .recorder_base import *  # noqa: F403


class MacroRecorderMixin0:
    """Records mouse and keyboard events and converts them to macro steps."""

    STOP_HOTKEY = frozenset(["ctrl", "alt", "s"])  # Ctrl+Alt+S to stop

    def __init__(self, macro_name: str, output_dir: str = "."):
        self.macro_name = macro_name
        self.output_dir = Path(output_dir)
        self.templates_dir = self.output_dir / f"{macro_name}_templates"

        self._steps: list[RecordedStep] = []
        self._step_index = 0
        self._pressed_modifiers: set[str] = set()
        self._pending_chars: list[str] = []
        self._last_event_time = time.time()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

        # Double-click detection
        self._last_click_pos: Optional[tuple[int, int]] = None
        self._last_click_time: float = 0.0
        self._DOUBLE_CLICK_MS = 400

    def _next_index(self) -> int:
        self._step_index += 1
        return self._step_index

    def _flush_pending_chars(self):
        """Accumulate consecutive character presses into a single type step."""
        if self._pending_chars:
            text = "".join(self._pending_chars)
            step = RecordedStep(
                index=self._next_index(),
                kind="type",
                text=text,
            )
            self._steps.append(step)
            self._pending_chars.clear()

    def on_click(self, x: int, y: int, button, pressed: bool):
        if not pressed:
            return  # only record press events

        with self._lock:
            self._flush_pending_chars()

            btn_str = button.name if hasattr(button, "name") else str(button)

            # Detect double click
            now = time.time()
            is_double = (
                self._last_click_pos == (x, y)
                and (now - self._last_click_time) * 1000 < self._DOUBLE_CLICK_MS
            )
            if is_double:
                # Upgrade last click step to double=True
                if self._steps and self._steps[-1].kind == "click":
                    self._steps[-1].double = True
                self._last_click_pos = None
                return

            self._last_click_pos = (x, y)
            self._last_click_time = now

            # Try to find the window under the click point
            window_title, window_bounds = _get_active_window_at(x, y)

            # Compute relative coords within window (fallback to screen pct)
            if window_bounds:
                wx, wy = window_bounds["x"], window_bounds["y"]
                ww, wh = window_bounds["width"], window_bounds["height"]
                x_pct = round((x - wx) / ww, 4) if ww > 0 else 0.5
                y_pct = round((y - wy) / wh, 4) if wh > 0 else 0.5
            else:
                window_title = ""
                x_pct = round(x / 1920, 4)
                y_pct = round(y / 1080, 4)

            # Also try to capture a template (useful when region has features)
            idx = self._next_index()
            template_file = str(self.templates_dir / f"step_{idx:03d}_click.png")
            captured = _capture_template(x, y, template_file)

            step = RecordedStep(
                index=idx,
                kind="click",
                x=x,
                y=y,
                button=btn_str,
                template_path=template_file if captured else "",
                window_title=window_title,
                x_pct=x_pct,
                y_pct=y_pct,
            )
            self._steps.append(step)
            print(
                f"[recorder] click #{idx} at ({x},{y}) "
                f"window='{window_title}' rel=({x_pct},{y_pct})",
                flush=True,
            )
