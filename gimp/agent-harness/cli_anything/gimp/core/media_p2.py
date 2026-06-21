# ruff: noqa: F403, F405, E501
from .media_base import *  # noqa: F403

# fmt: off
from .media_p1 import _last_nonzero  # noqa: E402,E501
# fmt: on


def _hist_mean(hist: list) -> float:
    total = sum(hist)
    if total == 0:
        return 0.0
    weighted = sum(i * v for i, v in enumerate(hist))
    return round(weighted / total, 1)


def _first_nonzero(hist: list) -> int:
    for i, v in enumerate(hist):
        if v > 0:
            return i
    return 0


def get_image_histogram(path: str) -> Dict[str, Any]:
    """Get histogram data for an image.  Requires Pillow."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")

    try:
        from PIL import Image
    except ImportError:
        raise RuntimeError(
            "Histogram analysis requires Pillow.  Install it with:\n"
            "  pip install Pillow"
        )

    with Image.open(path) as img:
        if img.mode not in ("RGB", "RGBA", "L"):
            img = img.convert("RGB")

        hist = img.histogram()

        if img.mode in ("RGB", "RGBA"):
            r_hist = hist[0:256]
            g_hist = hist[256:512]
            b_hist = hist[512:768]
            return {
                "mode": img.mode,
                "channels": {
                    "red": {
                        "min": _first_nonzero(r_hist),
                        "max": _last_nonzero(r_hist),
                        "mean": _hist_mean(r_hist),
                    },
                    "green": {
                        "min": _first_nonzero(g_hist),
                        "max": _last_nonzero(g_hist),
                        "mean": _hist_mean(g_hist),
                    },
                    "blue": {
                        "min": _first_nonzero(b_hist),
                        "max": _last_nonzero(b_hist),
                        "mean": _hist_mean(b_hist),
                    },
                },
            }
        else:
            return {
                "mode": img.mode,
                "channels": {
                    "luminance": {
                        "min": _first_nonzero(hist),
                        "max": _last_nonzero(hist),
                        "mean": _hist_mean(hist),
                    },
                },
            }
