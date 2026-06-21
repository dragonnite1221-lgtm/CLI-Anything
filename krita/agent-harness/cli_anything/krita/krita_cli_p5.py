# ruff: noqa: F403, F405, E501
from .krita_cli_base import *  # noqa: F403

# fmt: off
from .krita_cli_p1 import _load_project, _output, _save_current, cli, handle_error  # noqa: E402,E501
from .krita_cli_p4 import export_group  # noqa: E402,E501
# fmt: on


@export_group.command("animation")
@click.argument("output_dir", type=click.Path())
@click.option("-p", "--preset", default="png", help="Frame format preset.")
@click.option("--basename", default="frame", help="Base filename for frames.")
@click.pass_context
@handle_error
def export_anim(ctx, output_dir, preset, basename):
    """Export animation frames."""
    proj = _load_project(ctx)
    result = export_animation(proj, output_dir, preset=preset, basename=basename)
    _output(result, ctx)


@export_group.command("presets")
@click.pass_context
@handle_error
def export_presets(ctx):
    """List available export presets."""
    presets = list_presets()
    if ctx.obj.get("json"):
        click.echo(json.dumps(presets, indent=2))
    else:
        click.echo("Export presets:")
        for p in presets:
            click.echo(f"  {p['name']}: {p['description']}")


@export_group.command("formats")
@click.pass_context
@handle_error
def export_formats(ctx):
    """List supported export formats."""
    formats = get_supported_formats()
    if ctx.obj.get("json"):
        click.echo(json.dumps({"formats": formats}))
    else:
        click.echo("Supported formats:")
        for fmt in formats:
            click.echo(f"  - {fmt}")


@cli.group()
@click.pass_context
def session(ctx):
    """Session state and undo/redo."""
    pass


@session.command("undo")
@click.pass_context
@handle_error
def session_undo(ctx):
    """Undo the last operation."""
    global _current_project
    state = _session.undo()
    if state is None:
        _output({"status": "nothing_to_undo"}, ctx)
        return
    _current_project = state
    _save_current(ctx)
    _output({"status": "undone", "history_position": _session.current_index()}, ctx)


@session.command("redo")
@click.pass_context
@handle_error
def session_redo(ctx):
    """Redo the last undone operation."""
    global _current_project
    state = _session.redo()
    if state is None:
        _output({"status": "nothing_to_redo"}, ctx)
        return
    _current_project = state
    _save_current(ctx)
    _output({"status": "redone", "history_position": _session.current_index()}, ctx)


@session.command("history")
@click.pass_context
@handle_error
def session_history(ctx):
    """Show session history."""
    hist = _session.history()
    if ctx.obj.get("json"):
        click.echo(json.dumps(hist, indent=2, default=str))
    else:
        for i, entry in enumerate(hist):
            marker = ">>>" if i == _session.current_index() else "   "
            click.echo(
                f"  {marker} [{i}] {entry.get('label', '')} ({entry.get('timestamp', '')})"
            )


@cli.command("status")
@click.pass_context
@handle_error
def status(ctx):
    """Show current status (project, session, Krita version)."""
    global _current_project, _current_project_path
    data = {
        "project_loaded": _current_project is not None,
        "project_path": _current_project_path,
        "history_size": len(_session.history()),
        "can_undo": _session.can_undo(),
        "can_redo": _session.can_redo(),
    }
    if _current_project:
        data["project_name"] = _current_project.get("name", "Unknown")
        c = _current_project.get("canvas", {})
        data["canvas"] = (
            f"{c.get('width', '?')}x{c.get('height', '?')} {c.get('colorspace', '?')} {c.get('depth', '?')}"
        )
        data["layer_count"] = len(_current_project.get("layers", []))
    try:
        data["krita_version"] = get_version()
        data["krita_installed"] = True
    except RuntimeError:
        data["krita_installed"] = False
    _output(data, ctx)


def main():
    cli(obj={})
