# ruff: noqa: F403, F405, E501
from .cc_backend_base import *  # noqa: F403

# fmt: off
from .cc_backend_p1 import open_and_save  # noqa: E402,E501
# fmt: on


def subsample(
    input_path: str,
    output_path: str,
    method: str = "SPATIAL",
    parameter: float = 0.05,
) -> dict:
    """Subsample a point cloud.

    Args:
        input_path: Input cloud file.
        output_path: Output cloud file.
        method: RANDOM (count), SPATIAL (min dist), or OCTREE (level).
        parameter: For RANDOM: point count. For SPATIAL: min distance.
                   For OCTREE: octree level (1-10).
    """
    method = method.upper()
    if method not in ("RANDOM", "SPATIAL", "OCTREE"):
        raise ValueError(f"method must be RANDOM, SPATIAL, or OCTREE, got {method!r}")

    if method == "OCTREE":
        param_str = str(int(parameter))
    elif method == "RANDOM":
        count = int(parameter)
        if count <= 0:
            raise ValueError(
                f"RANDOM subsampling parameter must be a positive integer point count, got {parameter!r}"
            )
        param_str = str(count)
    else:
        param_str = str(parameter)

    return open_and_save(input_path, output_path, ["-SS", method, param_str])


def compute_roughness(
    input_path: str,
    output_path: str,
    radius: float = 0.1,
) -> dict:
    """Compute roughness scalar field for a point cloud.

    Args:
        input_path: Input cloud file.
        output_path: Output cloud file (with roughness SF).
        radius: Sphere radius for roughness computation.
    """
    return open_and_save(input_path, output_path, ["-ROUGH", str(radius)])


def compute_density(
    input_path: str,
    output_path: str,
    sphere_radius: float = 0.1,
    density_type: str = "KNN",
) -> dict:
    """Compute point density scalar field.

    Args:
        input_path: Input cloud file.
        output_path: Output cloud file.
        sphere_radius: Sphere radius for density computation.
        density_type: KNN, SURFACE, or VOLUME.
    """
    density_type = density_type.upper()
    extra = ["-DENSITY", str(sphere_radius), "-TYPE", density_type]
    return open_and_save(input_path, output_path, extra)


def compute_curvature(
    input_path: str,
    output_path: str,
    curvature_type: str = "MEAN",
    radius: float = 0.1,
) -> dict:
    """Compute curvature scalar field.

    Args:
        input_path: Input cloud file.
        output_path: Output cloud file.
        curvature_type: MEAN or GAUSS.
        radius: Kernel radius.
    """
    curvature_type = curvature_type.upper()
    return open_and_save(
        input_path, output_path, ["-CURV", curvature_type, str(radius)]
    )


def sor_filter(
    input_path: str,
    output_path: str,
    nb_points: int = 6,
    std_ratio: float = 1.0,
) -> dict:
    """Statistical Outlier Removal (SOR) filter.

    Args:
        input_path: Input cloud file.
        output_path: Output cloud file.
        nb_points: Number of nearest neighbors.
        std_ratio: Standard deviation multiplier threshold.
    """
    return open_and_save(
        input_path, output_path, ["-SOR", str(nb_points), str(std_ratio)]
    )
