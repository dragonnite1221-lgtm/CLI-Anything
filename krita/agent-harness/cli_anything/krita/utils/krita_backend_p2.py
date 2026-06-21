# ruff: noqa: F403, F405, E501
from .krita_backend_base import *  # noqa: F403

# fmt: off
from .krita_backend_p1 import _run, find_krita  # noqa: E402,E501
# fmt: on


def export_file(
    input_path: str | Path,
    output_path: str | Path,
    *,
    format: Optional[str] = None,
    export_options: Optional[Dict[str, Any]] = None,
    timeout: int = 300,
) -> Dict[str, Any]:
    """Export *input_path* to *output_path* using Krita's CLI.

    Parameters:
        input_path: Source file (any format Krita can open).
        output_path: Destination file.  The extension determines the output
            format unless *format* is given.
        format: If provided, override the output format (e.g. ``"png"``).
            The extension of *output_path* will still be respected for the
            filename.
        export_options: Optional dict of key-value pairs forwarded to Krita
            via ``--export-option key=value`` flags (e.g. compression, quality).
        timeout: Maximum seconds to wait for Krita.

    Returns:
        Result dict with keys ``ok``, ``returncode``, ``stdout``, ``stderr``,
        ``command``, and ``output_path``.
    """
    krita = find_krita()
    input_path = str(Path(input_path).resolve())
    output_path = str(Path(output_path).resolve())

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    args = [krita, "--export", "--export-filename", output_path]
    if export_options:
        for key, value in export_options.items():
            args += ["--export-option", f"{key}={value}"]
    args.append(input_path)

    result = _run(args, timeout=timeout)
    result["output_path"] = output_path
    result["output_exists"] = os.path.isfile(output_path)
    return result


def export_animation(
    input_path: str | Path,
    output_dir: str | Path,
    *,
    format: str = "png",
    basename: str = "frame",
    first_frame: Optional[int] = None,
    last_frame: Optional[int] = None,
    timeout: int = 600,
) -> Dict[str, Any]:
    """Export animation frames from *input_path*.

    Parameters:
        input_path: Source animation file (e.g. ``.kra`` with animation data).
        output_dir: Directory to write frame files into.
        format: Frame image format (``"png"``, ``"jpg"``, ``"gif"``, etc.).
        basename: Filename prefix for each frame (e.g. ``frame0000.png``).
        first_frame: Optional first frame index to export.
        last_frame: Optional last frame index to export.
        timeout: Maximum seconds to wait for Krita.

    Returns:
        Result dict.  On success ``output_files`` lists exported frame paths.
    """
    krita = find_krita()
    input_path = str(Path(input_path).resolve())
    output_dir = str(Path(output_dir).resolve())
    os.makedirs(output_dir, exist_ok=True)

    # Build the export sequence filename pattern.
    # Krita expects the output filename to contain the base for numbering.
    export_filename = os.path.join(output_dir, f"{basename}.{format}")

    args = [
        krita,
        "--export-sequence",
        "--export-filename",
        export_filename,
    ]
    if first_frame is not None:
        args += ["--export-sequence-start", str(first_frame)]
    if last_frame is not None:
        args += ["--export-sequence-end", str(last_frame)]
    args.append(input_path)

    result = _run(args, timeout=timeout)

    # Collect whatever frames appeared in the output directory.
    frame_pattern = os.path.join(output_dir, f"{basename}*.{format}")
    result["output_dir"] = output_dir
    result["output_files"] = sorted(glob.glob(frame_pattern))
    return result
