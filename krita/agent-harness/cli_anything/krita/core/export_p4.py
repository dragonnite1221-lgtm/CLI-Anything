# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p2 import build_kra_from_project  # noqa: E402,E501
# fmt: on


def export_animation(
    project: dict,
    output_dir: str,
    preset: str = "png",
    frame_range: Optional[Tuple[int, int]] = None,
    basename: str = "frame",
) -> Dict[str, Any]:
    """
    Export animation frames using the Krita backend.

    Parameters
    ----------
    project : dict
        The project JSON state.
    output_dir : str
        Directory to write frame files into.
    preset : str
        Export preset name.
    frame_range : tuple[int, int] | None
        Optional ``(start, end)`` frame range. ``None`` exports all frames.
    basename : str
        Base filename for exported frames (e.g. ``frame`` -> ``frame_0001.png``).

    Returns
    -------
    dict
        ``{"frame_count": int, "output_dir": str, "format": str}``
    """
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    if preset not in EXPORT_PRESETS:
        raise ValueError(
            f"Unknown export preset '{preset}'. "
            f"Available presets: {', '.join(sorted(EXPORT_PRESETS))}"
        )

    preset_config = EXPORT_PRESETS[preset]

    # Build temporary .kra
    tmp_dir = tempfile.mkdtemp(prefix="krita_anim_export_")
    kra_path = os.path.join(tmp_dir, "project.kra")
    build_kra_from_project(project, kra_path)

    result = backend_export_animation(
        input_path=kra_path,
        output_dir=output_dir,
        frame_range=frame_range,
        basename=basename,
        export_options=preset_config.get("options", {}),
    )

    frame_count = result.get("frame_count", 0) if isinstance(result, dict) else 0

    return {
        "frame_count": frame_count,
        "output_dir": output_dir,
        "format": preset_config["extension"],
    }


def list_presets() -> List[Dict[str, str]]:
    """
    Return a list of available export presets with descriptions.

    Returns
    -------
    list[dict]
        Each entry has ``name``, ``extension``, and ``description`` keys.
    """
    return [
        {
            "name": name,
            "extension": cfg["extension"],
            "description": cfg["description"],
        }
        for name, cfg in EXPORT_PRESETS.items()
    ]


def get_supported_formats() -> List[str]:
    """
    Return a sorted list of all supported export format extensions.

    Returns
    -------
    list[str]
        Unique format extensions (e.g. ``["bmp", "gif", "jpg", ...]``).
    """
    formats = sorted({cfg["extension"] for cfg in EXPORT_PRESETS.values()})
    return formats
