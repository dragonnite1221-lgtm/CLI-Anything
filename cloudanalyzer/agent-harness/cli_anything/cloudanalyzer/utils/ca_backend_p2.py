# ruff: noqa: F403, F405, E501
from .ca_backend_base import *  # noqa: F403

# fmt: off
from .ca_backend_p1 import _ensure_ca  # noqa: E402,E501
# fmt: on


def trajectory_batch_evaluate(
    directory: str,
    reference_dir: str,
    **kwargs: Any,
) -> dict:
    """Batch trajectory evaluation."""
    _ensure_ca()
    from ca.batch import trajectory_batch_evaluate as _tbe

    return _tbe(directory, reference_dir, **kwargs)


def evaluate_run(
    map_path: str,
    map_reference_path: str,
    trajectory_path: str,
    trajectory_reference_path: str,
    **kwargs: Any,
) -> dict:
    """Evaluate one map and one trajectory together."""
    _ensure_ca()
    from ca.run_evaluate import evaluate_run as _er

    return _er(
        map_path,
        map_reference_path,
        trajectory_path,
        trajectory_reference_path,
        **kwargs,
    )


def random_sample(input_path: str, output_path: str, num_points: int) -> dict:
    """Random point sampling."""
    _ensure_ca()
    from ca.sample import random_sample as _rs

    return _rs(input_path, output_path, num_points)


def filter_outliers(
    input_path: str,
    output_path: str,
    **kwargs: Any,
) -> dict:
    """Statistical outlier removal."""
    _ensure_ca()
    from ca.filter import filter_outliers as _fo

    return _fo(input_path, output_path, **kwargs)


def merge(paths: list[str], output: str) -> dict:
    """Merge point clouds."""
    _ensure_ca()
    from ca.merge import merge as _m

    return _m(paths, output)


def convert(input_path: str, output_path: str) -> dict:
    """Convert between point cloud formats."""
    _ensure_ca()
    from ca.convert import convert as _c

    return _c(input_path, output_path)


def view_point_cloud(path: str) -> None:
    """Open the interactive point cloud viewer (single file)."""
    _ensure_ca()
    from ca.view import view as _view

    _view([path])


def web_serve(
    source: str,
    reference: str | None,
    *,
    port: int = 8080,
    heatmap: bool = False,
    trajectory: str | None = None,
    trajectory_reference: str | None = None,
    open_browser: bool = True,
) -> None:
    """Start the CloudAnalyzer web viewer."""
    _ensure_ca()
    from ca.web import serve

    paths: list[str] = [source] if not reference else [source, reference]
    serve(
        paths,
        port=port,
        open_browser=open_browser,
        heatmap=heatmap,
        trajectory_path=trajectory,
        trajectory_reference_path=trajectory_reference,
    )


def web_export_bundle(
    source: str,
    reference: str | None,
    output_dir: str,
    *,
    heatmap: bool = False,
    trajectory: str | None = None,
    trajectory_reference: str | None = None,
) -> dict:
    """Write a static HTML viewer bundle."""
    _ensure_ca()
    from ca.web import export_static_bundle

    paths: list[str] = [source] if not reference else [source, reference]
    return export_static_bundle(
        paths,
        output_dir=output_dir,
        heatmap=heatmap,
        trajectory_path=trajectory,
        trajectory_reference_path=trajectory_reference,
    )
