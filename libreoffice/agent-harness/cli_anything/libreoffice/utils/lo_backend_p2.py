# ruff: noqa: F403, F405, E501
from .lo_backend_base import *  # noqa: F403

# fmt: off
from .lo_backend_p1 import convert, get_version  # noqa: E402,E501
# fmt: on


def convert_odf_to(
    odf_path: str,
    output_format: str,
    output_path: Optional[str] = None,
    overwrite: bool = False,
    timeout: int = 120,
) -> dict:
    """Convert an ODF file to another format via LibreOffice headless.

    This is the high-level function used by the CLI export pipeline.

    Args:
        odf_path: Path to the ODF file (.odt, .ods, .odp).
        output_format: Target format (pdf, docx, xlsx, pptx, etc.).
        output_path: Desired output path. If None, uses same dir as input.
        overwrite: Allow overwriting existing output files.
        timeout: Maximum seconds for conversion.

    Returns:
        Dict with output path, format, and file size.
    """
    if output_path and os.path.exists(output_path) and not overwrite:
        raise FileExistsError(f"Output file exists: {output_path}. Use --overwrite.")

    # Convert to a temp dir first, then move to desired location
    with tempfile.TemporaryDirectory() as tmpdir:
        converted = convert(odf_path, output_format, output_dir=tmpdir, timeout=timeout)

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            shutil.move(converted, output_path)
            final_path = os.path.abspath(output_path)
        else:
            # Move to same directory as input
            dest_dir = os.path.dirname(os.path.abspath(odf_path))
            dest = os.path.join(dest_dir, os.path.basename(converted))
            if os.path.exists(dest) and not overwrite:
                raise FileExistsError(f"Output file exists: {dest}. Use --overwrite.")
            shutil.move(converted, dest)
            final_path = os.path.abspath(dest)

    return {
        "action": "convert",
        "output": final_path,
        "format": output_format,
        "method": "libreoffice-headless",
        "libreoffice_version": get_version(),
        "file_size": os.path.getsize(final_path),
    }
