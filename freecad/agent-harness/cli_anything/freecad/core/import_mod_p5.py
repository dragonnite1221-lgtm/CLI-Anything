# ruff: noqa: F403, F405, E501
from .import_mod_base import *  # noqa: F403

# fmt: off
from .import_mod_p1 import _detect_format, _validate_path  # noqa: E402,E501
# fmt: on


def import_info(path: str) -> Dict[str, Any]:
    """Preview file metadata without modifying any project.

    Returns information about the file including size, detected format,
    and estimated object count.  Does **not** require a project dict.

    Parameters
    ----------
    path : str
        Filesystem path to the file.

    Returns
    -------
    dict
        Metadata dictionary with keys ``path``, ``format``,
        ``size_bytes``, ``exists``, and ``estimated_objects``.

    Raises
    ------
    ValueError
        If *path* is empty or the format is unrecognised.
    """
    path = _validate_path(path)
    fmt = _detect_format(path)

    exists = os.path.isfile(path)
    size = os.path.getsize(path) if exists else 0

    # Classify destination
    if fmt in PART_FORMATS:
        target = "parts"
    elif fmt in MESH_FORMATS:
        target = "meshes"
    elif fmt in DRAFT_FORMATS:
        target = "draft_objects"
    else:
        target = "unknown"

    return {
        "path": path,
        "format": fmt,
        "size_bytes": size,
        "exists": exists,
        "estimated_objects": 1,
        "target_collection": target,
    }
