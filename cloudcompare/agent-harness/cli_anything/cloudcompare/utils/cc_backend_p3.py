# ruff: noqa: F403, F405, E501
from .cc_backend_base import *  # noqa: F403

# fmt: off
from .cc_backend_p1 import open_and_save, run_cloudcompare  # noqa: E402,E501
# fmt: on


def crop_cloud(
    input_path: str,
    output_path: str,
    xmin: float,
    ymin: float,
    zmin: float,
    xmax: float,
    ymax: float,
    zmax: float,
    outside: bool = False,
) -> dict:
    """Crop a point cloud to a bounding box.

    Args:
        input_path: Input cloud file.
        output_path: Output cloud file.
        xmin/ymin/zmin: Minimum corner.
        xmax/ymax/zmax: Maximum corner.
        outside: If True, keep points outside the box.
    """
    extra = ["-CROP", f"{xmin}:{ymin}:{zmin}:{xmax}:{ymax}:{zmax}"]
    if outside:
        extra.append("-OUTSIDE")
    return open_and_save(input_path, output_path, extra)


def merge_clouds(
    input_paths: list[str],
    output_path: str,
) -> dict:
    """Merge multiple point clouds into one.

    Args:
        input_paths: List of input cloud files.
        output_path: Output merged cloud file.
    """
    if len(input_paths) < 2:
        raise ValueError("Need at least 2 clouds to merge")

    output_path = os.path.abspath(output_path)
    out_ext = os.path.splitext(output_path)[1].lstrip(".")
    fmt = CLOUD_FORMATS.get(out_ext.lower(), "ASC")

    args = []
    for p in input_paths:
        args += ["-O", os.path.abspath(p)]

    args += [
        "-MERGE_CLOUDS",
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


def compute_c2c_distances(
    compare_path: str,
    reference_path: str,
    output_path: str,
    split_xyz: bool = False,
    octree_level: int = 10,
) -> dict:
    """Compute cloud-to-cloud distances.

    Args:
        compare_path: 'Compared' cloud (gets the distance SF).
        reference_path: 'Reference' cloud.
        output_path: Output cloud file with distance SF.
        split_xyz: If True, also compute X/Y/Z components separately.
        octree_level: Octree level for the computation.
    """
    args = [
        "-O",
        os.path.abspath(reference_path),
        "-O",
        os.path.abspath(compare_path),
        "-C2C_DIST",
        "-OCTREE_LEVEL",
        str(octree_level),
    ]
    if split_xyz:
        args.append("-SPLIT_XYZ")

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
