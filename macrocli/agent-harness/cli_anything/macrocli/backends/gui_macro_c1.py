# ruff: noqa: F403, F405, E501
from .gui_macro_base import *  # noqa: F403


class GUIMacroBackendMixin1:
    def _check_layout(self, macro_blob: dict) -> str:
        """Return error string if current screen doesn't match expected."""
        expected_res = macro_blob.get("screen_resolution", "")
        if not expected_res:
            return ""
        try:
            import pyautogui
            w, h = pyautogui.size()
            current_res = f"{w}x{h}"
            if current_res != expected_res:
                return f"screen is {current_res}, macro expects {expected_res}"
        except ImportError:
            pass  # Can't verify — allow through
        return ""
    def _execute_steps(self, steps: list, context: BackendContext) -> int:
        """Execute each step in the compiled macro."""
        try:
            import pyautogui
            has_pyautogui = True
        except ImportError:
            has_pyautogui = False

        count = 0
        for s in steps:
            stype = s.get("type", "")
            delay = s.get("delay_ms", 100) / 1000.0

            if stype == "click":
                if not has_pyautogui:
                    raise ImportError("pyautogui required for click steps. pip install pyautogui")
                button = s.get("button", "left")
                pyautogui.click(s["x"], s["y"], button=button)

            elif stype == "key":
                if not has_pyautogui:
                    raise ImportError("pyautogui required for key steps. pip install pyautogui")
                keys = s.get("keys", "").split("+")
                if len(keys) == 1:
                    pyautogui.press(keys[0])
                else:
                    pyautogui.hotkey(*keys)

            elif stype == "type":
                if not has_pyautogui:
                    raise ImportError("pyautogui required for type steps. pip install pyautogui")
                pyautogui.typewrite(s.get("text", ""), interval=0.03)

            elif stype == "wait_file":
                deadline = time.time() + s.get("timeout_ms", 5000) / 1000.0
                path = s.get("path", "")
                while time.time() < deadline:
                    if Path(path).exists():
                        break
                    time.sleep(0.1)
                else:
                    raise TimeoutError(f"wait_file timed out: {path}")
                delay = 0  # no additional delay after file wait

            elif stype == "sleep":
                time.sleep(s.get("ms", 500) / 1000.0)
                delay = 0

            if delay > 0:
                time.sleep(delay)
            count += 1

        return count
