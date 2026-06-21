# ruff: noqa: F403, F405, E501
from .openscreen_cli_base import *  # noqa: F403
# fmt: off
from .openscreen_cli_p1 import _auto_save, _dry_run, _json_output, _session, output  # noqa: E402,E501
from .openscreen_cli_p3 import repl  # noqa: E402,E501
# fmt: on


def _repl_trim(args, skin, pt_session=None):
    """Handle trim subcommands in REPL."""
    if not args:
        skin.error("Usage: trim list|add|rm <id>")
        return
    sub = args[0]
    if sub == "list":
        result = tl_mod.list_trim_regions(_session)
        output(result)
    elif sub == "add":
        skin.info("Add trim region:")
        start = int(skin.sub_input("  start_ms: ", pt_session))
        end = int(skin.sub_input("  end_ms: ", pt_session))
        result = tl_mod.add_trim_region(_session, start, end)
        skin.success(f"Added trim: {result['id']}")
    elif sub == "rm" and len(args) > 1:
        tl_mod.remove_trim_region(_session, args[1])
        skin.success(f"Removed: {args[1]}")
    else:
        skin.error("Usage: trim list|add|rm <id>")
@click.group(invoke_without_command=True)
@click.version_option("1.0.0", prog_name="Openscreen CLI")
@click.option("--json", "json_mode", is_flag=True, help="Output in JSON format")
@click.option("--session", "session_id", default=None, help="Session ID to resume")
@click.option("--project", "project_path", default=None, help="Open project on start")
@click.option("-s", "--save", "auto_save", is_flag=True, help="Auto-save after mutations")
@click.option("--dry-run", "dry_run", is_flag=True, default=False,
              help="Run command without saving changes to disk")
@click.pass_context
def cli(ctx, json_mode, session_id, project_path, auto_save, dry_run):
    """Openscreen CLI — Screen recording editor.

    Edit screen recordings via command line: zoom, speed, trim, crop,
    annotate, and export polished demo videos.

    Run without a subcommand to enter REPL mode.
    """
    global _session, _json_output, _auto_save, _dry_run
    _json_output = json_mode
    _auto_save = auto_save
    _dry_run = dry_run
    _session = Session(session_id)

    if project_path:
        _session.open_project(project_path)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)
