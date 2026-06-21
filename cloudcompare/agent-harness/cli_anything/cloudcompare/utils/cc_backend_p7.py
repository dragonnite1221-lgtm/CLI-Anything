# ruff: noqa: F403, F405, E501
from .cc_backend_base import *  # noqa: F403

# fmt: off
from .cc_backend_p1 import open_and_save  # noqa: E402,E501
# fmt: on


def sf_to_rgb(
    input_path: str,
    output_path: str,
) -> dict:
    """Convert the active scalar field to RGB colours.

    CloudCompare maps each SF value through the current colour ramp and stores
    the result as per-point RGB.  Useful before applying colour-based filters
    or exporting a coloured cloud.

    Args:
        input_path: Input cloud (must have an active scalar field).
        output_path: Output cloud with RGB colours.
    """
    return open_and_save(input_path, output_path, ["-SF_CONVERT_TO_RGB", "TRUE"])


def rgb_to_sf(
    input_path: str,
    output_path: str,
) -> dict:
    """Convert RGB colours to a scalar field (intensity/greyscale).

    The resulting SF stores the luminance of each point's RGB triplet.

    Args:
        input_path: Input cloud with RGB colours.
        output_path: Output cloud with the new scalar field.
    """
    return open_and_save(input_path, output_path, ["-RGB_CONVERT_TO_SF"])


def noise_filter(
    input_path: str,
    output_path: str,
    knn: int = 6,
    noisiness: float = 1.0,
    use_radius: bool = False,
    radius: float = 0.1,
    absolute: bool = False,
) -> dict:
    """Apply the PCL noise filter to remove noisy points.

    Uses CloudCompare's ``-NOISE`` command (backed by the PCL wrapper plugin).
    Noisy points are identified by comparing each point's deviation from its
    local neighbourhood to a noise threshold.

    Note: CC's CLI does not provide Gaussian/Bilateral spatial smoothing.
    This PCL noise filter is the closest available spatial noise-removal
    operation via the command line.

    Args:
        input_path:   Input cloud.
        output_path:  Filtered output cloud (noisy points removed).
        knn:          Number of nearest neighbours used when ``use_radius``
                      is False (default 6).
        noisiness:    Noise threshold multiplier.  Points whose deviation
                      exceeds this multiple of the local noise estimate are
                      removed (default 1.0).
        use_radius:   If True, use a fixed search radius instead of KNN.
        radius:       Search radius when ``use_radius`` is True.
        absolute:     If True, interpret ``noisiness`` as an absolute
                      distance threshold (ABS) rather than relative (REL).

    Returns:
        dict with output, exists, file_size, returncode.
    """
    mode = "RADIUS" if use_radius else "KNN"
    mode_val = str(radius) if use_radius else str(knn)
    threshold_mode = "ABS" if absolute else "REL"

    extra = ["-NOISE", mode, mode_val, threshold_mode, str(noisiness)]
    return open_and_save(input_path, output_path, extra)


def invert_normals(
    input_path: str,
    output_path: str,
) -> dict:
    """Invert (flip) all normals in a point cloud.

    Args:
        input_path:  Input cloud with normals.
        output_path: Output cloud with flipped normals.
    """
    return open_and_save(input_path, output_path, ["-INVERT_NORMALS"])


def apply_transform(
    input_path: str,
    output_path: str,
    matrix_file: str,
    inverse: bool = False,
) -> dict:
    """Apply a rigid-body (or affine) transformation to a point cloud.

    The transformation is read from a plain-text file containing a 4×4 matrix
    (one row per line, values space-separated).

    Args:
        input_path:   Input cloud or mesh.
        output_path:  Transformed output cloud.
        matrix_file:  Path to the 4×4 transformation matrix text file.
        inverse:      If True, apply the inverse of the matrix.

    Example matrix file (identity)::

        1 0 0 0
        0 1 0 0
        0 0 1 0
        0 0 0 1
    """
    matrix_file = os.path.abspath(matrix_file)
    extra = ["-APPLY_TRANS"]
    if inverse:
        extra.append("-INVERSE")
    extra.append(matrix_file)
    return open_and_save(input_path, output_path, extra)
