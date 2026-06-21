# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _render_with_melt  # noqa: E402,E501
# fmt: on


def render(
    session: Session,
    output_path: str,
    preset: str = "default",
    width: Optional[int] = None,
    height: Optional[int] = None,
    overwrite: bool = False,
    extra_args: Optional[list[str]] = None,
    prefer_ffmpeg: bool = False,
) -> dict:
    """Render the project to an output file.

    This works by:
    1. Saving the current project to a temporary .mlt file
    2. Using melt to render it

    Args:
        session: Active session with an open project
        output_path: Path for the output file
        preset: Export preset name
        width: Override output width
        height: Override output height
        overwrite: Overwrite existing output file
        extra_args: Additional command-line arguments for the encoder
        prefer_ffmpeg: Backward-compatible preview hint; melt remains the
            render backend because it natively interprets MLT projects.
    """
    if not session.is_open:
        raise RuntimeError("No project is open")

    output_path = os.path.abspath(output_path)
    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(
            f"Output file already exists: {output_path}. Use --overwrite to replace."
        )

    if preset not in EXPORT_PRESETS:
        available = ", ".join(sorted(EXPORT_PRESETS.keys()))
        raise ValueError(f"Unknown preset: {preset!r}. Available: {available}")

    melt = shutil.which("melt")
    if not melt:
        raise RuntimeError(
            "melt is required for rendering but not found. "
            "Install it with: apt install melt  (or equivalent for your OS)"
        )
    # No ffmpeg fallback — melt is the only render path because it natively
    # reads MLT XML and handles all project features (transitions, compositing,
    # multi-track). Direct ffmpeg encoding cannot interpret MLT projects.

    preset_config = EXPORT_PRESETS[preset]

    output_ext = os.path.splitext(output_path)[1].lower()
    if not output_ext:
        fmt = preset_config.get("format", "mp4")
        output_path += f".{fmt}"

    return _render_with_melt(
        session, output_path, preset_config, melt, width, height, extra_args
    )
