# ruff: noqa: F403, F405, E501
from .cc_backend_base import *  # noqa: F403

# fmt: off
from .cc_backend_p1 import run_cloudcompare  # noqa: E402,E501
# fmt: on


def csf_filter(
    input_path: str,
    ground_output: str,
    offground_output: Optional[str] = None,
    scene: str = "RELIEF",
    cloth_resolution: float = 2.0,
    class_threshold: float = 0.5,
    max_iteration: int = 500,
    proc_slope: bool = False,
) -> dict:
    """Ground filtering using the Cloth Simulation Filter (CSF) algorithm.

    CSF simulates a cloth draped over an inverted point cloud to separate
    ground points from off-ground points (vegetation, buildings, etc.).

    Reference: Zhang et al. (2016) Remote Sensing 8(6):501.

    Args:
        input_path: Input cloud file (LiDAR scan).
        ground_output: Output path for the ground point cloud.
        offground_output: Output path for the off-ground cloud (optional).
                          If None, off-ground points are not exported.
        scene: Scene type affecting cloth rigidness:
               - SLOPE  (rigidness=1): steep terrain with slopes
               - RELIEF (rigidness=2): general terrain (default)
               - FLAT   (rigidness=3): flat or urban terrain
        cloth_resolution: Grid resolution of the cloth (metres). Smaller =
                          finer ground detail but slower. Default 2.0.
        class_threshold: Max distance (metres) from cloth to classify a point
                         as ground. Default 0.5.
        max_iteration: Maximum cloth simulation iterations. Default 500.
        proc_slope: Enable post-processing to smooth slope artifacts. Default False.

    Returns:
        dict with keys: returncode, ground, ground_exists, ground_size,
        and optionally offground, offground_exists, offground_size.
    """
    scene = scene.upper()
    if scene not in ("SLOPE", "RELIEF", "FLAT"):
        raise ValueError(f"scene must be SLOPE, RELIEF, or FLAT, got {scene!r}")

    input_path = os.path.abspath(input_path)
    ground_output = os.path.abspath(ground_output)
    in_dir = os.path.dirname(input_path)
    in_stem = os.path.splitext(os.path.basename(input_path))[0]

    # Determine export format from requested output extension
    out_ext = os.path.splitext(ground_output)[1].lstrip(".").lower()
    fmt = CLOUD_FORMATS.get(out_ext, "LAS")

    # Build the CC command.
    # IMPORTANT: -C_EXPORT_FMT must come BEFORE -CSF so the format is set
    # before CSF calls exportEntity() internally for -EXPORT_GROUND/OFFGROUND.
    args = [
        "-O",
        input_path,
        "-C_EXPORT_FMT",
        fmt,
        "-NO_TIMESTAMP",
        "-CSF",
        "-SCENES",
        scene,
        "-CLOTH_RESOLUTION",
        str(cloth_resolution),
        "-CLASS_THRESHOLD",
        str(class_threshold),
        "-MAX_ITERATION",
        str(max_iteration),
    ]
    if proc_slope:
        args.append("-PROC_SLOPE")
    args.append("-EXPORT_GROUND")
    if offground_output is not None:
        args.append("-EXPORT_OFFGROUND")

    result = run_cloudcompare(args, cwd=in_dir)

    # CC auto-generates output filenames: {stem}_ground_points.{ext}
    # Use glob to find them robustly (extension may vary by fmt)
    def _find_and_move(pattern: str, dest: str) -> bool:
        candidates = glob.glob(pattern)
        if not candidates:
            return False
        src = candidates[0]
        if src != dest:
            os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
            os.replace(src, dest)
        return os.path.exists(dest)

    ground_exists = _find_and_move(
        os.path.join(in_dir, f"{in_stem}_ground_points.*"),
        ground_output,
    )

    result["ground"] = ground_output
    result["ground_exists"] = ground_exists
    result["ground_size"] = os.path.getsize(ground_output) if ground_exists else 0

    if offground_output is not None:
        offground_output = os.path.abspath(offground_output)
        offground_exists = _find_and_move(
            os.path.join(in_dir, f"{in_stem}_offground_points.*"),
            offground_output,
        )
        result["offground"] = offground_output
        result["offground_exists"] = offground_exists
        result["offground_size"] = (
            os.path.getsize(offground_output) if offground_exists else 0
        )

    return result
