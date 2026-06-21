# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import export_cloud  # noqa: E402,E501
# fmt: on


def export_mesh(
    input_path: str,
    output_path: str,
    preset: Optional[str] = None,
    overwrite: bool = False,
) -> dict:
    """Export a mesh to a new format using CloudCompare.

    Args:
        input_path: Source mesh file.
        output_path: Destination file path.
        preset: Optional format preset (e.g., 'obj', 'stl', 'ply').
        overwrite: Whether to overwrite existing output.

    Returns:
        dict with output info.
    """
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Resolve preset before overwrite check — preset can change the output extension.
    if preset:
        preset = preset.lower()
        if preset not in MESH_PRESETS:
            raise ValueError(
                f"Unknown mesh preset {preset!r}. Options: {list(MESH_PRESETS)}"
            )
        info = MESH_PRESETS[preset]
        fmt = info["format"]
        ext = info["ext"]
        out_base = os.path.splitext(output_path)[0]
        output_path = f"{out_base}.{ext}"
    else:
        out_ext = os.path.splitext(output_path)[1].lstrip(".").lower()
        fmt = MESH_FORMATS.get(out_ext, "OBJ")
        ext = out_ext

    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(
            f"Output file already exists: {output_path}. Use overwrite=True."
        )

    args = [
        "-O",
        input_path,
        "-M_EXPORT_FMT",
        fmt,
        "-NO_TIMESTAMP",
        "-SAVE_MESHES",
        "FILE",
        output_path,
    ]

    result = run_cloudcompare(args)
    exists = os.path.exists(output_path)

    if result["returncode"] != 0:
        raise RuntimeError(
            f"CloudCompare mesh export failed (exit {result['returncode']}):\n"
            f"  stderr: {result['stderr'][:500]}"
        )

    if not exists:
        raise RuntimeError(
            f"CloudCompare ran but output file was not created: {output_path}"
        )

    return {
        "output": output_path,
        "format": fmt,
        "extension": ext,
        "file_size": os.path.getsize(output_path),
        "returncode": result["returncode"],
        "command": result["command"],
    }


def batch_export(
    input_paths: list[str],
    output_dir: str,
    preset: str = "las",
    overwrite: bool = False,
) -> list[dict]:
    """Batch export multiple clouds to a directory.

    Args:
        input_paths: List of input cloud files.
        output_dir: Directory for output files.
        preset: Format preset for all outputs.
        overwrite: Whether to overwrite existing files.

    Returns:
        List of result dicts (one per input).
    """
    os.makedirs(output_dir, exist_ok=True)
    results = []
    for inp in input_paths:
        stem = Path(inp).stem
        ext = CLOUD_PRESETS.get(preset, CLOUD_PRESETS["las"])["ext"]
        out = os.path.join(output_dir, f"{stem}.{ext}")
        try:
            r = export_cloud(inp, out, preset=preset, overwrite=overwrite)
            r["status"] = "ok"
        except Exception as e:
            r = {"input": inp, "output": out, "status": "error", "error": str(e)}
        results.append(r)
    return results
