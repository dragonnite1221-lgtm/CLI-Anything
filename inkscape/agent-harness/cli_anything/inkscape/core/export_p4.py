# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


def export_pdf(
    project: Dict[str, Any],
    output_path: str,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Export the document as PDF.

    Generates an SVG and provides an Inkscape command for PDF conversion.
    If Inkscape is available, runs it directly.
    """
    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(f"Output file already exists: {output_path}")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Generate SVG first
    svg_path = output_path.rsplit(".", 1)[0] + ".svg"
    save_svg(project, svg_path)

    inkscape_cmd = f"inkscape {svg_path} --export-filename={output_path}"

    # Try to use Inkscape if available
    if shutil.which("inkscape"):
        import subprocess

        try:
            subprocess.run(
                ["inkscape", svg_path, f"--export-filename={output_path}"],
                check=True,
                capture_output=True,
                timeout=60,
            )
            return {
                "output": output_path,
                "format": "pdf",
                "svg_source": svg_path,
                "rendered_by": "inkscape",
            }
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass

    return {
        "output": output_path,
        "format": "pdf",
        "svg_source": svg_path,
        "inkscape_command": inkscape_cmd,
        "status": "svg_generated",
        "message": "Run the inkscape command to produce PDF.",
    }


def export_svg(
    project: Dict[str, Any], output_path: str, overwrite: bool = False
) -> Dict[str, Any]:
    """Export the document as a valid SVG file."""
    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(f"Output file already exists: {output_path}")

    save_svg(project, output_path)

    return {
        "output": output_path,
        "format": "svg",
        "size_bytes": os.path.getsize(output_path),
    }


def list_presets() -> List[Dict[str, Any]]:
    """List available export presets."""
    result = []
    for name, preset in EXPORT_PRESETS.items():
        result.append(
            {
                "name": name,
                "format": preset["format"],
                "dpi": preset["dpi"],
                "description": preset["description"],
            }
        )
    return result
