# ruff: noqa: F403, F405, E501
from .cc_backend_base import *  # noqa: F403

# fmt: off
from .cc_backend_p1 import open_and_save  # noqa: E402,E501
# fmt: on


def filter_sf_by_value(
    input_path: str,
    output_path: str,
    min_val: float,
    max_val: float,
    sf_index: Optional[int] = None,
) -> dict:
    """Filter a cloud to points whose active scalar field value falls in [min_val, max_val].

    Typical usage: after coord_to_sf(dim="Z"), filter to a height range.

    Args:
        input_path: Input cloud file (must have an active scalar field).
        output_path: Output cloud file (filtered).
        min_val: Minimum SF value to keep.
        max_val: Maximum SF value to keep.
        sf_index: If given, sets this SF index as active before filtering.
                  Use when the cloud has multiple SFs and you need to pick one.
    """
    extra = []
    if sf_index is not None:
        extra += ["-SET_ACTIVE_SF", str(sf_index)]
    extra += ["-FILTER_SF", str(min_val), str(max_val)]
    return open_and_save(input_path, output_path, extra)


def coord_to_sf_and_filter(
    input_path: str,
    output_path: str,
    dimension: str = "Z",
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
) -> dict:
    """Convert a coordinate to SF and optionally filter by value range in one pass.

    Combines -COORD_TO_SF and -FILTER_SF in a single CloudCompare invocation.
    Useful for height-based slice extraction (e.g., keep points between z=10 and z=20).

    Args:
        input_path: Input cloud file.
        output_path: Output cloud file.
        dimension: X, Y, or Z. Default Z.
        min_val: Minimum value to keep. None = no lower bound (uses 'MIN').
        max_val: Maximum value to keep. None = no upper bound (uses 'MAX').
    """
    dim = dimension.upper()
    if dim not in ("X", "Y", "Z"):
        raise ValueError(f"dimension must be X, Y, or Z, got {dim!r}")

    extra = ["-COORD_TO_SF", dim, "-SET_ACTIVE_SF", "0"]

    if min_val is not None or max_val is not None:
        lo = str(min_val) if min_val is not None else "MIN"
        hi = str(max_val) if max_val is not None else "MAX"
        extra += ["-FILTER_SF", lo, hi]

    return open_and_save(input_path, output_path, extra)


def convert_format(
    input_path: str,
    output_path: str,
) -> dict:
    """Convert a point cloud from one format to another.

    Args:
        input_path: Input cloud (any supported format).
        output_path: Output cloud (format determined by extension).
    """
    return open_and_save(input_path, output_path)


def compute_normals(
    input_path: str,
    output_path: str,
    octree_level: int = 10,
    orientation: str = "PLUS_Z",
) -> dict:
    """Compute normals via octree.

    Args:
        input_path: Input cloud.
        output_path: Output cloud with normals.
        octree_level: Octree level for normal computation.
        orientation: Normal orientation hint: PLUS_X/Y/Z or MINUS_X/Y/Z.
    """
    extra = ["-OCTREE_NORMALS", str(octree_level)]
    if orientation:
        extra += ["-ORIENT", orientation]
    return open_and_save(input_path, output_path, extra)
