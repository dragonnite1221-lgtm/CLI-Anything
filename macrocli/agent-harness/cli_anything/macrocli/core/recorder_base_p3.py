# ruff: noqa: F403, F405, E501
from .recorder_base_base import *  # noqa: F403


_KEY_NAME_MAP = {
    "ctrl_l": "ctrl",
    "ctrl_r": "ctrl",
    "shift_r": "shift",
    "alt_l": "alt",
    "alt_r": "alt",
    "alt_gr": "alt",
    "cmd_r": "cmd",
    "super_l": "super",
    "super_r": "super",
}


def _key_to_str(key) -> str:
    """Convert a pynput Key or KeyCode to a string."""
    try:
        from pynput.keyboard import Key

        if isinstance(key, Key):
            name = key.name  # e.g. "ctrl_l", "shift", "f5"
            return _KEY_NAME_MAP.get(name, name)
        # KeyCode
        if hasattr(key, "char") and key.char:
            return key.char
        if hasattr(key, "vk") and key.vk:
            return f"vk{key.vk}"
    except Exception:
        pass
    return str(key)


__all__ = [
    "MacroRecorder",
    "Optional",
    "Path",
    "RecordedStep",
    "_KEY_NAME_MAP",
    "_MODIFIER_KEYS",
    "_TEMPLATE_PADDING",
    "_capture_template",
    "_get_active_window_at",
    "_key_to_str",
    "annotations",
    "dataclass",
    "field",
    "os",
    "sys",
    "threading",
    "time",
]
