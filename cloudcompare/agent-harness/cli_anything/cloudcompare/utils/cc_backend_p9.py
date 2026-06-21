# ruff: noqa: F403, F405, E501
from .cc_backend_base import *  # noqa: F403

# fmt: off
from .cc_backend_p1 import find_cloudcompare, run_cloudcompare  # noqa: E402,E501
# fmt: on


def extract_connected_components(
    input_path: str,
    output_dir: str,
    octree_level: int = 8,
    min_points: int = 100,
    output_fmt: str = "xyz",
) -> dict:
    """Segment a cloud into connected components (clusters).

    Uses CloudCompare's ``-EXTRACT_CC`` command which labels connected regions
    at a given octree resolution and exports each component as a separate file.

    Args:
        input_path:   Input cloud.
        output_dir:   Directory where component clouds will be saved.
        octree_level: Octree level controlling neighbourhood radius
                      (1-10; higher = finer, more components).
        min_points:   Discard components with fewer than this many points.
        output_fmt:   Output file extension / format (default ``"xyz"``).

    Returns:
        dict with output_dir, components (list of paths), component_count,
        returncode.
    """
    input_path = os.path.abspath(input_path)
    output_dir = os.path.abspath(output_dir)
    in_dir = os.path.dirname(input_path)
    input_stem = os.path.splitext(os.path.basename(input_path))[0]
    fmt = CLOUD_FORMATS.get(output_fmt.lower(), "ASC")

    args = [
        "-O",
        input_path,
        "-C_EXPORT_FMT",
        fmt,
        "-NO_TIMESTAMP",
        "-EXTRACT_CC",
        str(octree_level),
        str(min_points),
        "-SAVE_CLOUDS",
    ]

    # CC saves component files to the input file's directory, not cwd.
    # Files are named: {input_stem}_COMPONENT_{n}.{actual_ext}
    # The actual extension depends on the CC format name, not the input extension
    # (e.g., output_fmt="xyz" → CC format "ASC" → files saved as ".asc").
    _fmt_to_ext = {
        "ASC": "asc",
        "PLY": "ply",
        "LAS": "las",
        "PCD": "pcd",
        "BIN": "bin",
        "E57": "e57",
    }
    actual_ext = _fmt_to_ext.get(fmt, output_fmt.lower())

    result = run_cloudcompare(args, cwd=in_dir)

    # Restrict matching to the current input stem to avoid picking up leftovers.
    components = sorted(
        glob.glob(os.path.join(in_dir, f"{input_stem}_COMPONENT_*.{actual_ext}"))
    )

    # Move components to output_dir if it differs from in_dir.
    if os.path.abspath(output_dir) != os.path.abspath(in_dir):
        os.makedirs(output_dir, exist_ok=True)
        moved = []
        for c in components:
            dest = os.path.join(output_dir, os.path.basename(c))
            shutil.move(c, dest)
            moved.append(dest)
        components = sorted(moved)

    result["output_dir"] = output_dir
    result["components"] = components
    result["component_count"] = len(components)
    return result


def is_available() -> bool:
    """Check if CloudCompare is available."""
    try:
        find_cloudcompare()
        return True
    except RuntimeError:
        return False


def get_version() -> Optional[str]:
    """Try to retrieve CloudCompare version string.

    CloudCompare does not support a --version flag. For Flatpak installations,
    version is read from `flatpak info`. For native installations, returns None.
    """
    try:
        cmd = find_cloudcompare()
        # Flatpak: extract version from `flatpak info`
        if "flatpak" in cmd:
            app_id = next(
                (c for c in cmd if c.startswith("org.cloudcompare")),
                "org.cloudcompare.CloudCompare",
            )
            result = subprocess.run(
                ["flatpak", "info", app_id],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.splitlines():
                if line.strip().startswith("Version:"):
                    return line.split(":", 1)[1].strip()
        return None
    except Exception:
        return None
