# ruff: noqa: F403, F405, E501
from .cloudanalyzer_cli_base import *  # noqa: F403

# fmt: off
from .cloudanalyzer_cli_p1 import _error, _out, cli, evaluate  # noqa: E402,E501
# fmt: on


@evaluate.command("diff")
@click.argument("source")
@click.argument("target")
@click.option("--threshold", type=float, default=None)
@click.pass_context
def evaluate_diff(
    ctx: click.Context, source: str, target: str, threshold: Optional[float]
) -> None:
    """Quick distance statistics."""
    try:
        result = ca_backend.diff(source, target, threshold=threshold)
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@evaluate.command("ground")
@click.argument("estimated_ground")
@click.argument("estimated_nonground")
@click.argument("reference_ground")
@click.argument("reference_nonground")
@click.option("--voxel-size", type=float, default=0.2)
@click.option("--min-precision", type=float, default=None)
@click.option("--min-recall", type=float, default=None)
@click.option("--min-f1", type=float, default=None)
@click.option("--min-iou", type=float, default=None)
@click.pass_context
def evaluate_ground(
    ctx: click.Context,
    estimated_ground: str,
    estimated_nonground: str,
    reference_ground: str,
    reference_nonground: str,
    voxel_size: float,
    min_precision: Optional[float],
    min_recall: Optional[float],
    min_f1: Optional[float],
    min_iou: Optional[float],
) -> None:
    """Evaluate ground segmentation quality."""
    try:
        result = ca_backend.evaluate_ground(
            estimated_ground,
            estimated_nonground,
            reference_ground,
            reference_nonground,
            voxel_size=voxel_size,
            min_precision=min_precision,
            min_recall=min_recall,
            min_f1=min_f1,
            min_iou=min_iou,
        )
        _out(ctx, result)
        if result.get("quality_gate") and not result["quality_gate"]["passed"]:
            ctx.exit(1)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@evaluate.command("batch")
@click.argument("directory")
@click.argument("reference")
@click.option("--min-auc", type=float, default=None)
@click.option("--max-chamfer", type=float, default=None)
@click.pass_context
def evaluate_batch(
    ctx: click.Context,
    directory: str,
    reference: str,
    min_auc: Optional[float],
    max_chamfer: Optional[float],
) -> None:
    """Batch evaluation of multiple point clouds."""
    try:
        result = ca_backend.batch_evaluate(
            directory,
            reference,
            min_auc=min_auc,
            max_chamfer=max_chamfer,
        )
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@evaluate.command("pipeline")
@click.argument("input_path")
@click.argument("reference")
@click.option("-o", "--output", required=True)
@click.option("-v", "--voxel-size", type=float, default=0.05)
@click.pass_context
def evaluate_pipeline(
    ctx: click.Context,
    input_path: str,
    reference: str,
    output: str,
    voxel_size: float,
) -> None:
    """Filter, downsample, evaluate in one command."""
    try:
        result = ca_backend.run_pipeline(
            input_path,
            reference,
            output,
            voxel_size=voxel_size,
        )
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@cli.group()
@click.pass_context
def trajectory(ctx: click.Context) -> None:
    """Trajectory evaluation commands."""
