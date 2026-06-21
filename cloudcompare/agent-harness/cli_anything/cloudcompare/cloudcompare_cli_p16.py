# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project, cli  # noqa: E402,E501
from .cloudcompare_cli_p15 import export  # noqa: E402,E501
# fmt: on


@export.command("mesh")
@click.argument("mesh_index", type=int)
@click.argument("output_path")
@click.option(
    "--preset", "-f", default=None, help=f"Format preset: {', '.join(MESH_PRESETS)}."
)
@click.option("--overwrite", is_flag=True, default=False)
@click.pass_context
def export_mesh_cmd(
    ctx: click.Context,
    mesh_index: int,
    output_path: str,
    preset: Optional[str],
    overwrite: bool,
) -> None:
    """Export a mesh to a target format using CloudCompare."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        mesh_entry = session.get_mesh(mesh_index)
        result = export_mesh(
            mesh_entry["path"], output_path, preset=preset, overwrite=overwrite
        )
        session.record(
            "export_mesh",
            [mesh_entry["path"]],
            [result["output"]],
            {
                "format": result["format"],
            },
        )
        session.save()
        _out(ctx, result)
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@export.command("batch")
@click.option("--output-dir", "-d", required=True, help="Output directory.")
@click.option("--preset", "-f", default="las", help="Format preset for all outputs.")
@click.option("--overwrite", is_flag=True, default=False)
@click.pass_context
def export_batch(
    ctx: click.Context, output_dir: str, preset: str, overwrite: bool
) -> None:
    """Batch export all project clouds to a directory."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        inputs = [session.get_cloud(i)["path"] for i in range(session.cloud_count)]
        results = batch_export(inputs, output_dir, preset=preset, overwrite=overwrite)
        _out(ctx, {"results": results, "count": len(results)})
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@export.command("formats")
@click.pass_context
def export_formats(ctx: click.Context) -> None:
    """List all available export format presets."""
    _out(ctx, list_presets())


@cli.group("session")
def session_group() -> None:
    """Session management (save, history, status)."""


@session_group.command("save")
@click.pass_context
def session_save(ctx: click.Context) -> None:
    """Save the current project to disk."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        session.save()
        _out(ctx, {"saved": path, "status": "ok"})
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@session_group.command("history")
@click.option("--last", "-n", type=int, default=10, help="Number of recent entries.")
@click.pass_context
def session_history(ctx: click.Context, last: int) -> None:
    """Show recent operation history."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        hist = session.history(last)
        _out(ctx, {"history": hist, "count": len(hist)})
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@session_group.command("undo")
@click.pass_context
def session_undo(ctx: click.Context) -> None:
    """Remove the last operation from history (soft undo)."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        removed = session.undo_last()
        session.save()
        if removed:
            _out(ctx, {"undone": removed})
        else:
            _out(ctx, {"status": "nothing_to_undo"})
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)
