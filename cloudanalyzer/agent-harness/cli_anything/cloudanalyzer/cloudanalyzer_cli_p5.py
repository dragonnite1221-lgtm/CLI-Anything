# ruff: noqa: F403, F405, E501
from .cloudanalyzer_cli_base import *  # noqa: F403

# fmt: off
from .cloudanalyzer_cli_p1 import _error, _out, cli  # noqa: E402,E501
from .cloudanalyzer_cli_p4 import process  # noqa: E402,E501
# fmt: on


@process.command("filter")
@click.argument("input_path")
@click.option("-o", "--output", required=True)
@click.option("--nb-neighbors", type=int, default=20)
@click.option("--std-ratio", type=float, default=2.0)
@click.pass_context
def process_filter(
    ctx: click.Context,
    input_path: str,
    output: str,
    nb_neighbors: int,
    std_ratio: float,
) -> None:
    """Statistical outlier removal."""
    try:
        result = ca_backend.filter_outliers(
            input_path,
            output,
            nb_neighbors=nb_neighbors,
            std_ratio=std_ratio,
        )
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@process.command("merge")
@click.argument("inputs", nargs=-1, required=True)
@click.option("-o", "--output", required=True)
@click.pass_context
def process_merge(ctx: click.Context, inputs: tuple[str, ...], output: str) -> None:
    """Merge multiple point clouds."""
    try:
        result = ca_backend.merge(list(inputs), output)
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@process.command("convert")
@click.argument("input_path")
@click.option("-o", "--output", required=True)
@click.pass_context
def process_convert(ctx: click.Context, input_path: str, output: str) -> None:
    """Convert between point cloud formats."""
    try:
        result = ca_backend.convert(input_path, output)
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@cli.group()
@click.pass_context
def inspect(ctx: click.Context) -> None:
    """Visualization and inspection commands."""


@inspect.command("view")
@click.argument("path")
@click.pass_context
def inspect_view(ctx: click.Context, path: str) -> None:
    """Open a point cloud viewer."""
    try:
        ca_backend.view_point_cloud(path)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@inspect.command("web")
@click.argument("source")
@click.argument("reference", required=False, default=None)
@click.option("--heatmap", is_flag=True)
@click.option("--trajectory", default=None)
@click.option("--trajectory-reference", default=None)
@click.option("--port", type=int, default=8080)
@click.pass_context
def inspect_web(
    ctx: click.Context,
    source: str,
    reference: Optional[str],
    heatmap: bool,
    trajectory: Optional[str],
    trajectory_reference: Optional[str],
    port: int,
) -> None:
    """Interactive browser inspection."""
    try:
        ca_backend.web_serve(
            source,
            reference,
            port=port,
            heatmap=heatmap,
            trajectory=trajectory,
            trajectory_reference=trajectory_reference,
        )
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@inspect.command("web-export")
@click.argument("source")
@click.argument("reference", required=False, default=None)
@click.option("-o", "--output", required=True)
@click.option("--heatmap", is_flag=True)
@click.option("--trajectory", default=None)
@click.option("--trajectory-reference", default=None)
@click.pass_context
def inspect_web_export(
    ctx: click.Context,
    source: str,
    reference: Optional[str],
    output: str,
    heatmap: bool,
    trajectory: Optional[str],
    trajectory_reference: Optional[str],
) -> None:
    """Export a static HTML inspection bundle."""
    try:
        result = ca_backend.web_export_bundle(
            source,
            reference,
            output,
            heatmap=heatmap,
            trajectory=trajectory,
            trajectory_reference=trajectory_reference,
        )
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@cli.group()
@click.pass_context
def info(ctx: click.Context) -> None:
    """Metadata commands."""


@info.command("show")
@click.argument("path")
@click.pass_context
def info_show(ctx: click.Context, path: str) -> None:
    """Show point cloud metadata."""
    try:
        result = ca_backend.info(path)
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@info.command("version")
@click.pass_context
def info_version(ctx: click.Context) -> None:
    """Show CloudAnalyzer version."""
    try:
        ver = ca_backend.get_version()
        _out(ctx, {"cloudanalyzer_version": ver, "harness_version": VERSION})
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@cli.group()
@click.pass_context
def session(ctx: click.Context) -> None:
    """Session management commands."""
