# ruff: noqa: F403, F405, E501
from .drawio_cli_base import *  # noqa: F403

# fmt: off
from .drawio_cli_p1 import get_session, handle_error, output  # noqa: E402,E501
from .drawio_cli_p2 import _run_repl  # noqa: E402,E501
# fmt: on


@click.group(invoke_without_command=True)
@click.option("--json", "json_mode", is_flag=True, help="Output in JSON format")
@click.option("--session", "session_id", default=None, help="Session ID to use/resume")
@click.option("--project", "project_path", default=None, help="Open a project file")
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    default=False,
    help="Run command without saving changes to disk",
)
@click.pass_context
def cli(ctx, json_mode, session_id, project_path, dry_run):
    """Draw.io CLI — Diagram creation from the command line.

    A stateful CLI for manipulating draw.io diagram files.
    Designed for AI agents and power users.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output, _session
    _json_output = json_mode

    if session_id:
        _session = Session(session_id)
    else:
        _session = Session()

    if project_path:
        _session.open_project(project_path)

    # Auto-save on exit when --project was used and project was modified
    @ctx.call_on_close
    def _auto_save():
        if dry_run:
            return
        if project_path and _session and _session.is_open and _session.is_modified:
            _session.save_project()

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl, project_path=None)


@cli.command()
@click.option("--project", "project_path", default=None, help="Open a project on start")
def repl(project_path):
    """Start an interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    s = get_session()
    if project_path:
        s.open_project(project_path)

    from cli_anything.drawio.utils.repl_skin import ReplSkin

    skin = ReplSkin("drawio", version="1.0.0")
    skin.print_banner()

    if project_path:
        skin.info(f"Opened: {project_path}")
        print()

    try:
        _run_repl(s, skin)
    except (KeyboardInterrupt, EOFError):
        skin.print_goodbye()

    _repl_mode = False


@cli.group()
def project():
    """Project management: new, open, save, info."""
    pass


@cli.group()
def session():
    """Session management: status, undo, redo."""
    pass


@project.command("new")
@click.option(
    "--preset",
    default="letter",
    type=click.Choice(sorted(proj_mod.PAGE_PRESETS.keys())),
    help="Page size preset",
)
@click.option("--width", type=int, default=None, help="Custom page width")
@click.option("--height", type=int, default=None, help="Custom page height")
@click.option(
    "-o",
    "--output",
    "output_path",
    default=None,
    help="Save the new project to this path",
)
@handle_error
def project_new(preset, width, height, output_path):
    """Create a new blank diagram."""
    session = get_session()
    result = proj_mod.new_project(session, preset, width, height)
    if output_path:
        save_result = proj_mod.save_project(session, output_path)
        result["saved_to"] = save_result["path"]
    output(result, f"Created new diagram ({result['page_size']})")


@project.command("open")
@click.argument("path")
@handle_error
def project_open(path):
    """Open an existing .drawio project file."""
    session = get_session()
    result = proj_mod.open_project(session, path)
    output(result, f"Opened: {path}")


@project.command("save")
@click.argument("path", required=False)
@handle_error
def project_save(path):
    """Save the current project."""
    session = get_session()
    result = proj_mod.save_project(session, path)
    output(result, f"Saved to: {result['path']}")


@project.command("info")
@handle_error
def project_info():
    """Show detailed project information."""
    session = get_session()
    result = proj_mod.project_info(session)
    output(result, "Project info:")


@project.command("xml")
@handle_error
def project_xml():
    """Print the raw XML of the current project."""
    session = get_session()
    if not session.is_open:
        raise RuntimeError("No project is open")
    from cli_anything.drawio.utils.drawio_xml import xml_to_string

    click.echo(xml_to_string(session.root))


@project.command("presets")
@handle_error
def project_presets():
    """List available page size presets."""
    result = proj_mod.list_presets()
    output(result, "Page presets:")


@cli.group()
def shape():
    """Shape operations: add, remove, move, resize, style."""
    pass


@cli.group()
def page():
    """Page operations: add, remove, rename, list."""
    pass
