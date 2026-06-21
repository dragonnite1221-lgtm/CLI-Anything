# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project, cli  # noqa: E402,E501
from .cloudcompare_cli_p16 import session_group  # noqa: E402,E501
# fmt: on


@session_group.command("set-format")
@click.option("--cloud-fmt", default=None, help="Cloud export format (e.g. LAS, PLY).")
@click.option("--cloud-ext", default=None, help="Cloud file extension (e.g. las, ply).")
@click.option("--mesh-fmt", default=None, help="Mesh export format (e.g. OBJ, STL).")
@click.option("--mesh-ext", default=None, help="Mesh file extension.")
@click.pass_context
def session_set_format(
    ctx: click.Context,
    cloud_fmt: Optional[str],
    cloud_ext: Optional[str],
    mesh_fmt: Optional[str],
    mesh_ext: Optional[str],
) -> None:
    """Update default export format settings."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        session.set_export_format(cloud_fmt, cloud_ext, mesh_fmt, mesh_ext)
        session.save()
        _out(ctx, {"settings": session.get_settings()})
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cli.command("info")
@click.pass_context
def info_cmd(ctx: click.Context) -> None:
    """Show CloudCompare installation info."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    available = is_available()
    try:
        cmd = find_cloudcompare() if available else []
    except RuntimeError:
        cmd = []
    version = get_version() if available else None
    _out(
        ctx,
        {
            "cloudcompare_available": available,
            "command": cmd,
            "version": version,
            "supported_cloud_formats": list(CLOUD_PRESETS.keys()),
            "supported_mesh_formats": list(MESH_PRESETS.keys()),
        },
    )


def main():
    cli(obj={})
