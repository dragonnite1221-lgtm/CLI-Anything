# ruff: noqa: F403, F405, E501
from .cloudanalyzer_cli_base import *  # noqa: F403

# fmt: off
from .cloudanalyzer_cli_p1 import _error, _out, cli  # noqa: E402,E501
from .cloudanalyzer_cli_p3 import check  # noqa: E402,E501
# fmt: on


@check.command("init")
@click.argument("destination")
@click.option("--profile", default="integrated", help="Template profile")
@click.option("--force", is_flag=True, help="Overwrite existing file")
@click.pass_context
def check_init(ctx: click.Context, destination: str, profile: str, force: bool) -> None:
    """Generate a starter config file."""
    dest = Path(destination)
    if dest.exists() and not force:
        _error(
            f"File exists: {dest}. Use --force to overwrite.",
            ctx.obj.get("json", False),
        )
        ctx.exit(1)
        return
    try:
        template = ca_backend.render_check_scaffold(profile=profile)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(template, encoding="utf-8")
        _out(ctx, {"created": str(dest), "profile": profile})
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@cli.group()
@click.pass_context
def baseline(ctx: click.Context) -> None:
    """Baseline evolution commands."""


@baseline.command("decision")
@click.argument("candidate_json")
@click.option("--history", "history_paths", multiple=True, help="History JSON files")
@click.option(
    "--history-dir", default=None, help="Auto-discover history from directory"
)
@click.option("--output-json", default=None)
@click.pass_context
def baseline_decision(
    ctx: click.Context,
    candidate_json: str,
    history_paths: tuple[str, ...],
    history_dir: Optional[str],
    output_json: Optional[str],
) -> None:
    """Decide promote / keep / reject for a baseline."""
    try:
        paths = list(history_paths)
        if history_dir:
            paths.extend(ca_backend.baseline_discover(history_dir))
        if not paths:
            _error("Provide --history or --history-dir.", ctx.obj.get("json", False))
            ctx.exit(1)
            return
        result = ca_backend.baseline_decision(candidate_json, paths)
        if output_json:
            Path(output_json).parent.mkdir(parents=True, exist_ok=True)
            Path(output_json).write_text(json.dumps(result, indent=2), encoding="utf-8")
        _out(ctx, result)
        if result.get("decision") == "reject":
            ctx.exit(1)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@baseline.command("save")
@click.argument("summary_json")
@click.option("--history-dir", default="qa/history", help="History directory")
@click.option("--label", default=None)
@click.option("--keep", type=int, default=None, help="Rotate to keep N baselines")
@click.pass_context
def baseline_save(
    ctx: click.Context,
    summary_json: str,
    history_dir: str,
    label: Optional[str],
    keep: Optional[int],
) -> None:
    """Save a QA summary to the history directory."""
    try:
        dest = ca_backend.baseline_save(summary_json, history_dir, label=label)
        data: dict = {"saved": dest}
        if keep is not None:
            removed = ca_backend.baseline_rotate(history_dir, keep=keep)
            data["rotated"] = len(removed)
        _out(ctx, data)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@baseline.command("list")
@click.option("--history-dir", default="qa/history", help="History directory")
@click.pass_context
def baseline_list(ctx: click.Context, history_dir: str) -> None:
    """List saved baselines."""
    try:
        entries = ca_backend.baseline_list(history_dir)
        _out(ctx, entries)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@cli.group()
@click.pass_context
def process(ctx: click.Context) -> None:
    """Point cloud processing commands."""


@process.command("downsample")
@click.argument("input_path")
@click.option("-o", "--output", required=True, help="Output file path")
@click.option("-v", "--voxel-size", type=float, required=True)
@click.pass_context
def process_downsample(
    ctx: click.Context, input_path: str, output: str, voxel_size: float
) -> None:
    """Voxel grid downsampling."""
    try:
        result = ca_backend.downsample(input_path, output, voxel_size)
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@process.command("split")
@click.argument("input_path")
@click.option("-o", "--output-dir", required=True)
@click.option("-g", "--grid-size", type=float, required=True)
@click.option("-a", "--axis", default="xy", help="Split axes (xy/xz/yz)")
@click.pass_context
def process_split(
    ctx: click.Context, input_path: str, output_dir: str, grid_size: float, axis: str
) -> None:
    """Split point cloud into grid tiles."""
    try:
        result = ca_backend.split(input_path, output_dir, grid_size, axis=axis)
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@process.command("sample")
@click.argument("input_path")
@click.option("-o", "--output", required=True)
@click.option("-n", "--num-points", type=int, required=True)
@click.pass_context
def process_sample(
    ctx: click.Context, input_path: str, output: str, num_points: int
) -> None:
    """Random point sampling."""
    try:
        result = ca_backend.random_sample(input_path, output, num_points)
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)
