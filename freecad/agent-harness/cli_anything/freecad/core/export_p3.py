# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


def list_presets() -> List[Dict[str, str]]:
    """Return a list of available export presets with descriptions.

    Returns
    -------
    list[dict]
        Each entry has ``name``, ``format``, and ``description`` keys.
    """
    return [
        {
            "name": name,
            "format": cfg["format"],
            "description": cfg["description"],
        }
        for name, cfg in EXPORT_PRESETS.items()
    ]
