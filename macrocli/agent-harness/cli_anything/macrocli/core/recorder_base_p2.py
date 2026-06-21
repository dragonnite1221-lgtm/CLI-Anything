# ruff: noqa: F403, F405, E501
from .recorder_base_base import *  # noqa: F403


def _get_active_window_at(x: int, y: int) -> tuple[str, Optional[dict]]:
    """Return (app_name, bounds) of the currently focused window.

    Uses xdotool getwindowfocus — reliable, no text parsing of hostnames,
    works regardless of hostname format.
    """
    import shutil
    import subprocess
    import os

    env = os.environ.copy()
    if "DISPLAY" not in env:
        env["DISPLAY"] = ":0"

    if not shutil.which("xdotool"):
        return "", None

    try:
        # Get geometry of focused window
        gr = subprocess.run(
            ["xdotool", "getwindowfocus", "getwindowgeometry", "--shell"],
            capture_output=True,
            text=True,
            env=env,
            timeout=2,
        )
        geo = {}
        for line in gr.stdout.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                geo[k.strip()] = v.strip()

        wx = int(geo.get("X", 0))
        wy = int(geo.get("Y", 0))
        ww = int(geo.get("WIDTH", 0))
        wh = int(geo.get("HEIGHT", 0))
        wid = geo.get("WINDOW", "")

        if not wid or ww == 0 or wh == 0:
            return "", None

        # Get window title
        nr = subprocess.run(
            ["xdotool", "getwindowname", wid],
            capture_output=True,
            text=True,
            env=env,
            timeout=2,
        )
        full_title = nr.stdout.strip()

        # Extract app name: last segment after " - "
        # e.g. "macrocli.txt (/tmp) - gedit" → "gedit"
        # Plain titles (e.g. "Terminal") are returned as-is
        if " - " in full_title:
            app_name = full_title.split(" - ")[-1].strip()
        else:
            app_name = full_title.strip()

        bounds = {"x": wx, "y": wy, "width": ww, "height": wh}
        return app_name, bounds

    except Exception:
        return "", None


_TEMPLATE_PADDING = 60  # pixels around click point to capture


def _capture_template(x: int, y: int, output_path: str) -> bool:
    """Capture a small region around (x, y) and save as PNG template.

    Returns False if the region has too little variance (blank/featureless)
    to be useful as a template.
    """
    try:
        import mss
        from PIL import Image
        import numpy as np

        pad = _TEMPLATE_PADDING
        region = {
            "left": max(0, x - pad),
            "top": max(0, y - pad),
            "width": pad * 2,
            "height": pad * 2,
        }
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with mss.mss() as sct:
            raw = sct.grab(region)
            img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")

            # Check variance — featureless templates are useless
            arr = np.array(img, dtype=np.float32)
            if arr.std() < 8.0:
                return False  # blank region, skip

            img.save(output_path)
        return True
    except Exception as e:
        print(f"[recorder] Warning: could not capture template: {e}", file=sys.stderr)
        return False


_MODIFIER_KEYS = frozenset(
    [
        "ctrl_l",
        "ctrl_r",
        "shift",
        "shift_r",
        "alt_l",
        "alt_r",
        "alt_gr",
        "cmd",
        "cmd_r",
        "super_l",
        "super_r",
    ]
)
