# ruff: noqa: F403, F405, E501
from .cc_backend_base import *  # noqa: F403

# fmt: off
from .cc_backend_p1 import run_cloudcompare  # noqa: E402,E501
# fmt: on


def delaunay_mesh(
    input_path: str,
    output_path: str,
    axis_aligned: bool = True,
    max_edge_length: float = 0.0,
) -> dict:
    """Create a 2.5-D Delaunay triangulation mesh from a point cloud.

    Projects the cloud onto a plane (axis-aligned XY or best-fit) and
    triangulates the projected points.  Suitable for terrain-like surfaces.

    Args:
        input_path:      Input cloud.
        output_path:     Output mesh file (extension determines format).
        axis_aligned:    If True, project onto the XY plane (-AA).
                         If False, use the best-fit plane (-BEST_FIT).
        max_edge_length: Remove triangles whose longest edge exceeds this
                         value (0 = no limit).

    Returns:
        dict with output, exists, file_size, returncode.
    """
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)
    out_dir = os.path.dirname(output_path) or "."
    out_ext = Path(output_path).suffix.lstrip(".")
    fmt = MESH_FORMATS.get(out_ext.lower(), "OBJ")

    args = ["-O", input_path, "-DELAUNAY"]
    if axis_aligned:
        args.append("-AA")
    else:
        args.append("-BEST_FIT")
    if max_edge_length > 0:
        args += ["-MAX_EDGE_LENGTH", str(max_edge_length)]
    args += [
        "-M_EXPORT_FMT",
        fmt,
        "-NO_TIMESTAMP",
        "-SAVE_MESHES",
        "FILE",
        output_path,
    ]

    result = run_cloudcompare(args, cwd=out_dir)
    result["output"] = output_path
    result["exists"] = os.path.exists(output_path)
    if result["exists"]:
        result["file_size"] = os.path.getsize(output_path)
    return result


def sample_mesh(
    mesh_path: str,
    output_path: str,
    count: int = 10000,
) -> dict:
    """Sample a point cloud from a mesh surface.

    Randomly places ``count`` points on the mesh triangles, proportional to
    triangle area.

    Args:
        mesh_path:   Input mesh file.
        output_path: Output sampled point cloud.
        count:       Number of points to sample.
    """
    mesh_path = os.path.abspath(mesh_path)
    output_path = os.path.abspath(output_path)
    out_dir = os.path.dirname(output_path) or "."
    out_ext = Path(output_path).suffix.lstrip(".")
    fmt = CLOUD_FORMATS.get(out_ext.lower(), "ASC")

    args = [
        "-O",
        mesh_path,
        "-SAMPLE_MESH",
        "DENSITY",
        str(count),
        "-C_EXPORT_FMT",
        fmt,
        "-NO_TIMESTAMP",
        "-SAVE_CLOUDS",
        "FILE",
        output_path,
    ]

    result = run_cloudcompare(args, cwd=out_dir)
    result["output"] = output_path
    result["exists"] = os.path.exists(output_path)
    if result["exists"]:
        result["file_size"] = os.path.getsize(output_path)
    return result
