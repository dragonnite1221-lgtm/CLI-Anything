# ruff: noqa: F403, F405, E501
from .visual_anchor_base import *  # noqa: F403
from .visual_anchor_p0 import _require_pynput  # noqa: F401,E501


def _mouse_drag(
    fx: int, fy: int, tx: int, ty: int,
    button: str = "left", duration_ms: int = 200
):
    """Press at (fx, fy), move to (tx, ty) over duration_ms, release.

    Tries xdotool first (works with Qt5/KDE apps), falls back to pynput.
    """
    import shutil, subprocess, os

    env = os.environ.copy()
    if "DISPLAY" not in env:
        env["DISPLAY"] = ":0"

    if shutil.which("xdotool"):
        # xdotool is more reliable with Qt5 apps
        steps = max(5, duration_ms // 30)
        subprocess.run(["xdotool", "mousemove", str(fx), str(fy)], env=env)
        time.sleep(0.05)
        subprocess.run(["xdotool", "mousedown", "1"], env=env)
        time.sleep(0.05)
        for i in range(1, steps + 1):
            ix = int(fx + (tx - fx) * i / steps)
            iy = int(fy + (ty - fy) * i / steps)
            subprocess.run(["xdotool", "mousemove", str(ix), str(iy)], env=env)
            time.sleep(duration_ms / 1000.0 / steps)
        subprocess.run(["xdotool", "mousemove", str(tx), str(ty)], env=env)
        time.sleep(0.05)
        subprocess.run(["xdotool", "mouseup", "1"], env=env)
        return

    # Fallback: pynput
    mouse_mod, _ = _require_pynput()
    Button = mouse_mod.Button
    ctrl = mouse_mod.Controller()
    btn_map = {"left": Button.left, "right": Button.right, "middle": Button.middle}
    btn = btn_map.get(button.lower(), Button.left)

    ctrl.position = (fx, fy)
    time.sleep(0.05)
    ctrl.press(btn)
    time.sleep(0.05)

    steps = max(10, duration_ms // 20)
    step_sleep = duration_ms / 1000.0 / steps
    for i in range(1, steps + 1):
        ix = int(fx + (tx - fx) * i / steps)
        iy = int(fy + (ty - fy) * i / steps)
        ctrl.position = (ix, iy)
        time.sleep(step_sleep)

    ctrl.position = (tx, ty)
    time.sleep(0.05)
    ctrl.release(btn)
