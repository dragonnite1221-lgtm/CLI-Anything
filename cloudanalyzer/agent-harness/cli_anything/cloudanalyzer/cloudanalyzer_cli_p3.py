# ruff: noqa: F403, F405, E501
from .cloudanalyzer_cli_base import *  # noqa: F403

# fmt: off
from .cloudanalyzer_cli_p1 import _error, _out, cli  # noqa: E402,E501
from .cloudanalyzer_cli_p2 import trajectory  # noqa: E402,E501
# fmt: on


@trajectory.command("evaluate")
@click.argument("estimated")
@click.argument("reference")
@click.option("--max-ate", type=float, default=None)
@click.option("--max-rpe", type=float, default=None)
@click.option("--max-drift", type=float, default=None)
@click.option("--min-coverage", type=float, default=None)
@click.option("--max-lateral", type=float, default=None)
@click.option("--max-longitudinal", type=float, default=None)
@click.option("--align-origin", is_flag=True)
@click.option("--align-rigid", is_flag=True)
@click.pass_context
def trajectory_evaluate(
    ctx: click.Context,
    estimated: str,
    reference: str,
    max_ate: Optional[float],
    max_rpe: Optional[float],
    max_drift: Optional[float],
    min_coverage: Optional[float],
    max_lateral: Optional[float],
    max_longitudinal: Optional[float],
    align_origin: bool,
    align_rigid: bool,
) -> None:
    """Evaluate estimated vs reference trajectory."""
    try:
        result = ca_backend.evaluate_trajectory(
            estimated,
            reference,
            max_ate=max_ate,
            max_rpe=max_rpe,
            max_drift=max_drift,
            min_coverage=min_coverage,
            max_lateral=max_lateral,
            max_longitudinal=max_longitudinal,
            align_origin=align_origin,
            align_rigid=align_rigid,
        )
        _out(ctx, result)
        gate = result.get("quality_gate")
        if gate and not gate["passed"]:
            ctx.exit(1)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@trajectory.command("batch")
@click.argument("directory")
@click.option("--reference-dir", required=True)
@click.option("--max-ate", type=float, default=None)
@click.option("--max-rpe", type=float, default=None)
@click.option("--max-drift", type=float, default=None)
@click.option("--min-coverage", type=float, default=None)
@click.pass_context
def trajectory_batch(
    ctx: click.Context,
    directory: str,
    reference_dir: str,
    max_ate: Optional[float],
    max_rpe: Optional[float],
    max_drift: Optional[float],
    min_coverage: Optional[float],
) -> None:
    """Batch trajectory evaluation."""
    try:
        result = ca_backend.trajectory_batch_evaluate(
            directory,
            reference_dir,
            max_ate=max_ate,
            max_rpe=max_rpe,
            max_drift=max_drift,
            min_coverage=min_coverage,
        )
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@trajectory.command("run-evaluate")
@click.argument("map_path")
@click.argument("map_reference")
@click.argument("trajectory_path")
@click.argument("trajectory_reference")
@click.option("--min-auc", type=float, default=None)
@click.option("--max-ate", type=float, default=None)
@click.pass_context
def trajectory_run_evaluate(
    ctx: click.Context,
    map_path: str,
    map_reference: str,
    trajectory_path: str,
    trajectory_reference: str,
    min_auc: Optional[float],
    max_ate: Optional[float],
) -> None:
    """Integrated map + trajectory evaluation."""
    try:
        result = ca_backend.evaluate_run(
            map_path,
            map_reference,
            trajectory_path,
            trajectory_reference,
            min_auc=min_auc,
            max_ate=max_ate,
        )
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@cli.group()
@click.pass_context
def check(ctx: click.Context) -> None:
    """Config-driven quality gate commands."""


@check.command("run")
@click.argument("config_path")
@click.option("--output-json", default=None, help="Dump summary JSON")
@click.pass_context
def check_run(ctx: click.Context, config_path: str, output_json: Optional[str]) -> None:
    """Run unified QA from a config file."""
    try:
        result = ca_backend.run_check_suite(config_path)
        if output_json:
            Path(output_json).parent.mkdir(parents=True, exist_ok=True)
            Path(output_json).write_text(json.dumps(result, indent=2), encoding="utf-8")
        _out(ctx, result)
        if not result.get("summary", {}).get("passed", True):
            ctx.exit(1)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)
