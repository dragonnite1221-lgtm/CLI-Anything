# ruff: noqa: F403, F405, E501
from .visual_anchor_base import *  # noqa: F403


def _x_env() -> dict:
    """Return env dict with DISPLAY set, for subprocess calls to X tools."""
    env = os.environ.copy()
    if "DISPLAY" not in env:
        env["DISPLAY"] = ":0"
    return env


def _require_numpy():
    try:
        import numpy as np
        return np
    except ImportError:
        raise ImportError(
            "numpy is required for the visual_anchor backend.\n"
            "  pip install numpy"
        )


def _require_pil():
    try:
        from PIL import Image
        return Image
    except ImportError:
        raise ImportError(
            "Pillow is required for the visual_anchor backend.\n"
            "  pip install Pillow"
        )


def _require_mss():
    try:
        import mss
        return mss
    except ImportError:
        raise ImportError(
            "mss is required for screen capture.\n"
            "  pip install mss"
        )


def _require_pynput():
    try:
        from pynput import mouse as _m, keyboard as _k
        return _m, _k
    except ImportError:
        raise ImportError(
            "pynput is required for mouse/keyboard control.\n"
            "  pip install pynput"
        )


def _load_image_as_array(path: str):
    """Load an image file as a numpy uint8 RGB array."""
    np = _require_numpy()
    Image = _require_pil()
    img = Image.open(path).convert("RGB")
    return np.array(img, dtype=np.uint8)


def _screenshot_as_array():
    """Capture the full screen and return as numpy RGB array."""
    np = _require_numpy()
    mss = _require_mss()
    Image = _require_pil()
    with mss.mss() as sct:
        # Monitor 1 = first physical monitor (index 0 = all monitors combined)
        monitor = sct.monitors[1]
        raw = sct.grab(monitor)
        img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
        return np.array(img, dtype=np.uint8), monitor


def _find_template(
    screen: "np.ndarray",
    template: "np.ndarray",
    confidence: float = 0.85,
    step: int = 1,
) -> Optional[tuple[int, int, float]]:
    """Find template in screen.  Returns (center_x, center_y, score) or None.

    score is 0..1 where 1 = perfect match.
    Confidence threshold: only return match if score >= confidence.
    """
    np = _require_numpy()

    sh, sw = screen.shape[:2]
    th, tw = template.shape[:2]

    if th > sh or tw > sw:
        return None

    screen_f = screen.astype(np.float32)
    tmpl_f = template.astype(np.float32)
    tmpl_norm = tmpl_f - tmpl_f.mean()
    tmpl_std = tmpl_f.std()
    if tmpl_std < 1e-6:
        return None  # blank template

    best_score = -1.0
    best_pos: Optional[tuple[int, int]] = None

    for y in range(0, sh - th + 1, step):
        for x in range(0, sw - tw + 1, step):
            region = screen_f[y:y + th, x:x + tw]
            region_norm = region - region.mean()
            region_std = region.std()
            if region_std < 1e-6:
                continue
            score = float(
                (region_norm * tmpl_norm).sum()
                / (th * tw * region_std * tmpl_std)
            )
            if score > best_score:
                best_score = score
                best_pos = (x + tw // 2, y + th // 2)

    if best_pos is None or best_score < confidence:
        return None

    return (best_pos[0], best_pos[1], best_score)
