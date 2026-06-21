# ruff: noqa: F403, F405, E501
from .openscreen_cli_base import *  # noqa: F403
# fmt: off
from .openscreen_cli_p1 import _json_output, _session, handle_error, output  # noqa: E402,E501
from .openscreen_cli_p2 import cli  # noqa: E402,E501
# fmt: on


@cli.group()
def export():
    """Export — render the final video."""
    pass
@cli.group()
def preview():
    """Preview bundle capture and inspection."""
    pass
@export.command("presets")
@handle_error
def export_presets():
    """List available export presets."""
    result = export_mod.list_presets()
    output(result)
@export.command("render")
@click.argument("output_path")
@handle_error
def export_render(output_path):
    """Render the project to a video file."""
    def on_progress(stage, msg):
        if not _json_output:
            click.echo(f"  [{stage}] {msg}")

    result = export_mod.render(_session, output_path, on_progress)
    output(result, f"Exported to: {output_path}")
@preview.command("recipes")
@handle_error
def preview_recipes():
    """List available preview recipes."""
    output(preview_mod.list_recipes(), "Preview recipes")
@preview.command("capture")
@click.option("--recipe", default="quick", help="Preview recipe name")
@click.option("--force", is_flag=True, help="Bypass preview cache")
@click.option("--root-dir", default=None, help="Override preview bundle root directory")
@handle_error
def preview_capture(recipe, force, root_dir):
    """Capture a preview bundle for the active project."""
    result = preview_mod.capture(
        _session,
        recipe=recipe,
        force=force,
        root_dir=root_dir,
        command=f"cli-anything-openscreen --project {_session.project_path or ''} preview capture --recipe {recipe}".strip(),
    )
    bundle_dir = result.get("_bundle_dir", result.get("bundle_dir", ""))
    status = "Reused preview bundle" if result.get("cached") else "Created preview bundle"
    output(result, f"{status}: {bundle_dir}")
@preview.command("latest")
@click.option("--recipe", default=None, help="Filter by recipe name")
@click.option("--root-dir", default=None, help="Override preview bundle root directory")
@handle_error
def preview_latest(recipe, root_dir):
    """Show the latest preview bundle manifest."""
    result = preview_mod.latest(project_path=_session.project_path, recipe=recipe, root_dir=root_dir)
    output(result, f"Latest preview bundle: {result.get('_bundle_dir', '')}")
@cli.group("session")
def session_group():
    """Session — undo, redo, status, save/list sessions."""
    pass
@session_group.command("status")
@handle_error
def session_status():
    """Show current session status."""
    result = _session.status()
    output(result)
@session_group.command("undo")
@handle_error
def session_undo():
    """Undo the last operation."""
    if _session.undo():
        output({"status": "undone", "undo_remaining": len(_session._undo_stack)})
    else:
        output({"status": "nothing_to_undo"})
@session_group.command("redo")
@handle_error
def session_redo():
    """Redo the last undone operation."""
    if _session.redo():
        output({"status": "redone", "redo_remaining": len(_session._redo_stack)})
    else:
        output({"status": "nothing_to_redo"})
@session_group.command("save")
@handle_error
def session_save_state():
    """Save session state to disk."""
    path = _session.save_session_state()
    output({"status": "saved", "path": path})
@session_group.command("list")
@handle_error
def session_list():
    """List all saved sessions."""
    result = Session.list_sessions()
    output(result)
