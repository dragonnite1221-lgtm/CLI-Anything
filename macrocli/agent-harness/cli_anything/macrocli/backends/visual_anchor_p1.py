# ruff: noqa: F403, F405, E501
from .visual_anchor_base import *  # noqa: F403
from .visual_anchor_p0 import _find_template, _require_pynput, _screenshot_as_array, _x_env  # noqa: F401,E501


def _wait_for_template(
    template_array: "np.ndarray",
    confidence: float,
    timeout_ms: int,
    poll_ms: int = 300,
) -> Optional[tuple[int, int, float]]:
    """Poll until template found on screen or timeout. Returns match or None."""
    deadline = time.time() + timeout_ms / 1000.0
    while time.time() < deadline:
        screen, _ = _screenshot_as_array()
        result = _find_template(screen, template_array, confidence)
        if result is not None:
            return result
        time.sleep(poll_ms / 1000.0)
    return None


def _get_window_bounds(title_fragment: str) -> Optional[dict]:
    """Return {x, y, width, height} of the first window whose title contains
    title_fragment.  Works on Linux (xwininfo + wmctrl) and macOS (AppleScript).
    Returns None if not found or not available.
    """
    import subprocess
    import shutil
    import platform

    system = platform.system()

    if system == "Linux":
        # Try wmctrl first (most reliable)
        if shutil.which("wmctrl"):
            r = subprocess.run(
                ["wmctrl", "-lG"], capture_output=True, text=True, env=_x_env()
            )
            for line in r.stdout.splitlines():
                parts = line.split(None, 9)
                if len(parts) >= 9 and title_fragment.lower() in parts[-1].lower():
                    try:
                        # wmctrl -lG: wid desktop x y w h host title
                        x, y, w, h = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
                        return {"x": x, "y": y, "width": w, "height": h}
                    except ValueError:
                        pass
        # Fallback: xwininfo
        if shutil.which("xwininfo"):
            r = subprocess.run(
                ["xwininfo", "-name", title_fragment],
                capture_output=True, text=True, env=_x_env()
            )
            bounds = {}
            for line in r.stdout.splitlines():
                line = line.strip()
                if "Absolute upper-left X:" in line:
                    bounds["x"] = int(line.split()[-1])
                elif "Absolute upper-left Y:" in line:
                    bounds["y"] = int(line.split()[-1])
                elif "Width:" in line:
                    bounds["width"] = int(line.split()[-1])
                elif "Height:" in line:
                    bounds["height"] = int(line.split()[-1])
            if len(bounds) == 4:
                return bounds

    elif system == "Darwin":
        # macOS: use AppleScript to get window position
        script = f"""
        tell application "System Events"
            set ws to every window of every process whose name contains "{title_fragment}"
            if ws is not {{}} then
                set w to item 1 of item 1 of ws
                set p to position of w
                set s to size of w
                return (item 1 of p as text) & "," & (item 2 of p as text) & "," & (item 1 of s as text) & "," & (item 2 of s as text)
            end if
        end tell
        """
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            parts = r.stdout.strip().split(",")
            if len(parts) == 4:
                try:
                    return {
                        "x": int(parts[0]), "y": int(parts[1]),
                        "width": int(parts[2]), "height": int(parts[3])
                    }
                except ValueError:
                    pass

    return None


def _mouse_click(x: int, y: int, button: str = "left", double: bool = False):
    """Move mouse to (x, y) and click."""
    mouse_mod, _ = _require_pynput()
    Button = mouse_mod.Button
    ctrl = mouse_mod.Controller()

    btn_map = {
        "left": Button.left,
        "right": Button.right,
        "middle": Button.middle,
    }
    btn = btn_map.get(button.lower(), Button.left)

    ctrl.position = (x, y)
    time.sleep(0.05)
    ctrl.press(btn)
    ctrl.release(btn)
    if double:
        time.sleep(0.08)
        ctrl.press(btn)
        ctrl.release(btn)
