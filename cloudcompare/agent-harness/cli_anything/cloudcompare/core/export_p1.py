# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


def list_presets() -> dict:
    """Return available presets for cloud and mesh export."""
    return {
        "cloud": {k: v["desc"] for k, v in CLOUD_PRESETS.items()},
        "mesh": {k: v["desc"] for k, v in MESH_PRESETS.items()},
    }


def export_cloud(
    input_path: str,
    output_path: str,
    preset: Optional[str] = None,
    extra_args: Optional[list[str]] = None,
    overwrite: bool = False,
) -> dict:
    """Export a point cloud to a new format using CloudCompare.

    Args:
        input_path: Source cloud file.
        output_path: Destination file path (format from extension or preset).
        preset: Optional format preset name (e.g., 'las', 'ply').
        extra_args: Additional CC command args applied before saving.
        overwrite: Whether to overwrite existing output file.

    Returns:
        dict with output path, format, file_size, and backend result.

    Raises:
        FileNotFoundError: If input doesn't exist.
        FileExistsError: If output exists and overwrite=False.
        RuntimeError: If export fails.
    """
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Determine format from preset or extension (must happen before overwrite check
    # because a preset can change the output file extension).
    if preset:
        preset = preset.lower()
        if preset not in CLOUD_PRESETS:
            raise ValueError(
                f"Unknown preset {preset!r}. Options: {list(CLOUD_PRESETS)}"
            )
        info = CLOUD_PRESETS[preset]
        fmt = info["format"]
        ext = info["ext"]
        # If output_path has different extension, replace it
        out_base = os.path.splitext(output_path)[0]
        output_path = f"{out_base}.{ext}"
    else:
        out_ext = os.path.splitext(output_path)[1].lstrip(".").lower()
        fmt = CLOUD_FORMATS.get(out_ext, "ASC")
        ext = out_ext

    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(
            f"Output file already exists: {output_path}. Use overwrite=True."
        )

    result = open_and_save(input_path, output_path, extra_args)

    if result["returncode"] != 0:
        raise RuntimeError(
            f"CloudCompare export failed (exit {result['returncode']}):\n"
            f"  stderr: {result['stderr'][:500]}"
        )

    if not result.get("exists"):
        raise RuntimeError(
            f"CloudCompare ran but output file was not created: {output_path}"
        )

    return {
        "output": output_path,
        "format": fmt,
        "extension": ext,
        "file_size": result.get("file_size", 0),
        "returncode": result["returncode"],
        "command": result["command"],
    }
