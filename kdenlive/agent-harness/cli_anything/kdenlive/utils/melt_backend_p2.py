# ruff: noqa: F403, F405, E501
from .melt_backend_base import *  # noqa: F403

# fmt: off
from .melt_backend_p1 import _validate_codec, _validate_extra_args, find_melt  # noqa: E402,E501
# fmt: on


def render_mlt(
    mlt_path: str,
    output_path: str,
    vcodec: str = "libx264",
    acodec: str = "aac",
    overwrite: bool = False,
    timeout: int = 300,
    extra_args: Optional[list] = None,
) -> dict:
    """Render an MLT XML file to a video using melt.

    Args:
        mlt_path: Path to the .mlt XML file
        output_path: Output video file path
        vcodec: Video codec
        acodec: Audio codec
        overwrite: Allow overwriting existing files
        timeout: Maximum seconds
        extra_args: Additional melt arguments

    Returns:
        Dict with output path, file size, method
    """
    _validate_codec(vcodec, ALLOWED_VCODECS, "video codec")
    _validate_codec(acodec, ALLOWED_ACODECS, "audio codec")

    if not os.path.exists(mlt_path):
        raise FileNotFoundError(f"MLT file not found: {mlt_path}")

    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(f"Output file exists: {output_path}")

    melt = find_melt()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    cmd = [
        melt,
        mlt_path,
        "-consumer",
        f"avformat:{output_path}",
        f"vcodec={vcodec}",
        f"acodec={acodec}",
    ]

    if extra_args:
        _validate_extra_args(extra_args)
        cmd.extend(extra_args)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"melt render failed (exit {result.returncode}):\n"
            f"  stderr: {result.stderr[-500:]}"
        )

    if not os.path.exists(output_path):
        raise RuntimeError(
            f"melt produced no output file.\n"
            f"  Expected: {output_path}\n"
            f"  stdout: {result.stdout[-500:]}"
        )

    return {
        "output": os.path.abspath(output_path),
        "format": os.path.splitext(output_path)[1].lstrip("."),
        "method": "melt",
        "file_size": os.path.getsize(output_path),
    }
