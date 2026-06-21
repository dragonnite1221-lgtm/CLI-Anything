# ruff: noqa: F403, F405, E501
from .krita_backend_base import *  # noqa: F403

# fmt: off
from .krita_backend_p2 import export_file  # noqa: E402,E501
# fmt: on


def batch_export(
    input_paths: list[str | Path],
    output_dir: str | Path,
    *,
    format: str = "png",
    timeout: int = 600,
) -> Dict[str, Any]:
    """Export multiple files to *output_dir* in the given *format*.

    Parameters:
        input_paths: List of source files.
        output_dir: Target directory for all exported files.
        format: Output format extension (e.g. ``"png"``, ``"jpg"``).
        timeout: Maximum seconds per file.

    Returns:
        Aggregate result dict with per-file results in ``"files"``.
    """
    output_dir = str(Path(output_dir).resolve())
    os.makedirs(output_dir, exist_ok=True)

    results: list[Dict[str, Any]] = []
    all_ok = True
    for src in input_paths:
        src = Path(src)
        dest = os.path.join(output_dir, f"{src.stem}.{format}")
        r = export_file(src, dest, timeout=timeout)
        results.append(r)
        if not r["ok"]:
            all_ok = False

    return {
        "ok": all_ok,
        "files": results,
        "output_dir": output_dir,
    }
