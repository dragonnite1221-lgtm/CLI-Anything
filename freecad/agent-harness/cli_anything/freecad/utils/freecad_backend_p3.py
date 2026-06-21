# ruff: noqa: F403, F405, E501
from .freecad_backend_base import *  # noqa: F403

# fmt: off
from .freecad_backend_p2 import run_macro_content  # noqa: E402,E501
# fmt: on


def export_headless(
    macro_content: str,
    output_path: str,
    timeout: int = 120,
) -> Dict[str, Any]:
    """Write a macro to a temp file, execute it, and verify the output.

    This is a convenience wrapper that combines writing a macro script
    to a temporary file, executing it via :func:`run_macro`, and verifying
    that the expected output file was created.

    Parameters
    ----------
    macro_content : str
        Complete Python macro script content.
    output_path : str
        Expected output file path (the macro should write to this path).
    timeout : int
        Maximum seconds to wait for execution.

    Returns
    -------
    dict
        ``{"output": str, "format": str, "method": "freecad-headless",
        "file_size": int}``

    Raises
    ------
    RuntimeError
        If the macro execution fails (non-zero exit code) or the output
        file is not created.
    """
    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    result = run_macro_content(macro_content, timeout=timeout)

    if result["returncode"] != 0:
        raise RuntimeError(
            f"FreeCAD macro execution failed (exit code {result['returncode']}). "
            f"stderr: {result['stderr']}"
        )

    if not os.path.isfile(output_path):
        raise RuntimeError(
            f"FreeCAD macro completed but output file was not created: "
            f"{output_path}. stdout: {result['stdout']}"
        )

    ext = Path(output_path).suffix.lstrip(".")
    file_size = os.path.getsize(output_path)

    return {
        "output": output_path,
        "format": ext,
        "method": "freecad-headless",
        "file_size": file_size,
    }
