# ruff: noqa: F403, F405, E501
from .llm_assist_base import *  # noqa: F403


def _take_screenshot() -> bytes:
    """Capture the current screen and return as PNG bytes."""
    try:
        import mss
        from PIL import Image
        import io

        with mss.mss() as sct:
            monitor = sct.monitors[1]
            raw = sct.grab(monitor)
            img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
    except ImportError:
        raise ImportError("mss and Pillow required: pip install mss Pillow")


def _load_image_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


_ALLOWED_TYPES = {
    "click_image",
    "click_relative",
    "type_text",
    "hotkey",
    "wait_image",
    "wait_for_window",
    "menu_click",
    "scroll",
}
_REQUIRED_FIELDS = {
    "click_image": {"type", "description"},
    "click_relative": {"type", "window_title", "x_pct", "y_pct"},
    "type_text": {"type", "text"},
    "hotkey": {"type", "keys"},
    "wait_image": {"type", "description"},
    "wait_for_window": {"type", "title_contains"},
    "menu_click": {"type", "app_name", "menu_path"},
    "scroll": {"type"},
}


def _validate_steps(raw_steps: list) -> tuple[list[dict], list[str]]:
    """Validate and sanitize steps from model output.

    Returns (valid_steps, error_messages).
    """
    valid = []
    errors = []

    for i, step in enumerate(raw_steps):
        if not isinstance(step, dict):
            errors.append(f"Step {i}: not a dict, skipped.")
            continue

        stype = step.get("type", "")
        if stype not in _ALLOWED_TYPES:
            errors.append(f"Step {i}: unknown type '{stype}', skipped.")
            continue

        required = _REQUIRED_FIELDS.get(stype, {"type"})
        missing = required - set(step.keys())
        if missing:
            errors.append(f"Step {i} ({stype}): missing fields {missing}, skipped.")
            continue

        # Reject any absolute coordinate fields
        for bad_field in ("x", "y", "px", "pixels"):
            if bad_field in step:
                errors.append(
                    f"Step {i} ({stype}): absolute coordinate field '{bad_field}' rejected."
                )
                step.pop(bad_field)

        valid.append(step)

    return valid, errors
