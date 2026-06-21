# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project, cli  # noqa: E402,E501
from .cloudcompare_cli_p2 import project  # noqa: E402,E501
# fmt: on


@project.command("new")
@click.option("--output", "-o", required=True, help="Output .json project file path.")
@click.option("--name", "-n", default=None, help="Project name.")
@click.pass_context
def project_new(ctx: click.Context, output: str, name: Optional[str]) -> None:
    """Create a new empty project file."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        proj = create_project(output, name)
        info = project_info(proj)
        info["project_path"] = os.path.abspath(output)
        _out(ctx, info)
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@project.command("info")
@click.pass_context
def project_info_cmd(ctx: click.Context) -> None:
    """Show project info and loaded entities."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        info = session.info()
        info["project_path"] = path
        _out(ctx, info)
    except click.UsageError as e:
        _error(str(e), json_mode)
        sys.exit(1)
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@project.command("status")
@click.pass_context
def project_status(ctx: click.Context) -> None:
    """Show quick project status."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        _out(ctx, session.status())
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cli.group()
def cloud() -> None:
    """Point cloud operations (add, subsample, filter, analyze)."""


@cloud.command("add")
@click.argument("cloud_file")
@click.option("--label", "-l", default=None, help="Optional label for this cloud.")
@click.pass_context
def cloud_add(ctx: click.Context, cloud_file: str, label: Optional[str]) -> None:
    """Add a cloud file to the project."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        entry = session.add_cloud(cloud_file, label)
        session.save()
        _out(ctx, {"added": entry, "cloud_count": session.cloud_count})
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cloud.command("list")
@click.pass_context
def cloud_list(ctx: click.Context) -> None:
    """List all clouds in the project."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        clouds = session.info()["clouds"]
        _out(ctx, {"clouds": clouds, "count": len(clouds)})
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)
