# ruff: noqa: F403, F405, E501
from .cc_backend_base import *  # noqa: F403

# fmt: off
from .cc_backend_p1 import open_and_save, run_cloudcompare  # noqa: E402,E501
# fmt: on


def compute_c2m_distances(
    cloud_path: str,
    mesh_path: str,
    output_path: str,
    flip_normals: bool = False,
    unsigned: bool = False,
) -> dict:
    """Compute cloud-to-mesh distances.

    Args:
        cloud_path: Input point cloud.
        mesh_path: Reference mesh.
        output_path: Output cloud with distance SF.
        flip_normals: Flip mesh normals before computing.
        unsigned: Compute unsigned distances.
    """
    args = [
        "-O",
        os.path.abspath(mesh_path),
        "-O",
        os.path.abspath(cloud_path),
        "-C2M_DIST",
    ]
    if flip_normals:
        args.append("-FLIP_NORMS")
    if unsigned:
        args.append("-UNSIGNED")

    output_path = os.path.abspath(output_path)
    out_ext = os.path.splitext(output_path)[1].lstrip(".")
    fmt = CLOUD_FORMATS.get(out_ext.lower(), "ASC")

    args += [
        "-C_EXPORT_FMT",
        fmt,
        "-NO_TIMESTAMP",
        "-SAVE_CLOUDS",
        "FILE",
        output_path,
    ]

    result = run_cloudcompare(args)
    result["output"] = output_path
    result["exists"] = os.path.exists(output_path)
    if result["exists"]:
        result["file_size"] = os.path.getsize(output_path)
    return result


def run_icp(
    aligned_path: str,
    reference_path: str,
    output_path: str,
    max_iterations: int = 100,
    min_error_diff: float = 1e-6,
    overlap: float = 100.0,
) -> dict:
    """Run ICP (Iterative Closest Point) registration.

    Args:
        aligned_path: Cloud to align.
        reference_path: Reference cloud.
        output_path: Aligned output cloud.
        max_iterations: Maximum ICP iterations.
        min_error_diff: Stop when improvement is below this.
        overlap: Percentage of overlap (0-100).
    """
    args = [
        "-O",
        os.path.abspath(reference_path),
        "-O",
        os.path.abspath(aligned_path),
        "-ICP",
        "-ITER",
        str(max_iterations),
        "-MIN_ERROR_DIFF",
        str(min_error_diff),
        "-OVERLAP",
        str(overlap),
    ]

    output_path = os.path.abspath(output_path)
    out_ext = os.path.splitext(output_path)[1].lstrip(".")
    fmt = CLOUD_FORMATS.get(out_ext.lower(), "ASC")

    args += [
        "-C_EXPORT_FMT",
        fmt,
        "-NO_TIMESTAMP",
        "-SAVE_CLOUDS",
        "FILE",
        output_path,
    ]

    result = run_cloudcompare(args)
    result["output"] = output_path
    result["exists"] = os.path.exists(output_path)
    if result["exists"]:
        result["file_size"] = os.path.getsize(output_path)
    return result


def coord_to_sf(
    input_path: str,
    output_path: str,
    dimension: str = "Z",
    sf_index: int = 0,
) -> dict:
    """Convert a coordinate axis (X/Y/Z) to a scalar field.

    This is the standard way to create a height (elevation) scalar field
    from the Z coordinate, which can then be used for filtering or analysis.

    Args:
        input_path: Input cloud file.
        output_path: Output cloud file (with the new scalar field).
        dimension: Axis to convert: X, Y, or Z. Default Z (height).
        sf_index: Index to set as active SF after creation. Default 0.
    """
    dim = dimension.upper()
    if dim not in ("X", "Y", "Z"):
        raise ValueError(f"dimension must be X, Y, or Z, got {dim!r}")
    extra = ["-COORD_TO_SF", dim, "-SET_ACTIVE_SF", str(sf_index)]
    return open_and_save(input_path, output_path, extra)
