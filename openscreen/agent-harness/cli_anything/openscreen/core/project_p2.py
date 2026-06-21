# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403

# fmt: off
from .project_p1 import _validate_crop_region  # noqa: E402,E501
# fmt: on


def set_setting(session: Session, key: str, value) -> dict:
    """Set a project editor setting.

    Supported keys: aspectRatio, wallpaper, padding, borderRadius,
    shadowIntensity, motionBlurAmount, showBlur, exportQuality,
    exportFormat, gifFrameRate, gifLoop, gifSizePreset,
    webcamLayoutPreset, webcamMaskShape, cropRegion.
    """
    if not session.is_open:
        raise RuntimeError("No project is open")

    editor = session.editor
    VALID_KEYS = {
        "aspectRatio",
        "wallpaper",
        "padding",
        "borderRadius",
        "shadowIntensity",
        "motionBlurAmount",
        "showBlur",
        "exportQuality",
        "exportFormat",
        "gifFrameRate",
        "gifLoop",
        "gifSizePreset",
        "webcamLayoutPreset",
        "webcamMaskShape",
        "cropRegion",
    }
    if key not in VALID_KEYS:
        raise ValueError(f"Unknown setting: {key}. Valid: {sorted(VALID_KEYS)}")

    if key == "aspectRatio" and value not in ASPECT_RATIOS:
        raise ValueError(
            f"Invalid aspectRatio '{value}'. Valid: {', '.join(ASPECT_RATIOS)}"
        )

    if key == "exportQuality" and value not in EXPORT_QUALITIES:
        raise ValueError(
            f"Invalid exportQuality '{value}'. Valid: {', '.join(EXPORT_QUALITIES)}"
        )

    if key == "exportFormat" and value not in EXPORT_FORMATS:
        raise ValueError(
            f"Invalid exportFormat '{value}'. Valid: {', '.join(EXPORT_FORMATS)}"
        )

    if key == "padding":
        v = int(value)
        if not (0 <= v <= 100):
            raise ValueError(f"padding must be 0-100, got {v}")

    if key == "shadowIntensity":
        v = float(value)
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"shadowIntensity must be 0.0-1.0, got {v}")

    if key == "motionBlurAmount":
        v = float(value)
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"motionBlurAmount must be 0.0-1.0, got {v}")

    if key == "borderRadius":
        v = int(value)
        if v < 0:
            raise ValueError(f"borderRadius must be >= 0, got {v}")

    if key == "cropRegion":
        _validate_crop_region(value)

    session.checkpoint()
    editor[key] = value
    return {"status": "ok", "key": key, "value": value}
