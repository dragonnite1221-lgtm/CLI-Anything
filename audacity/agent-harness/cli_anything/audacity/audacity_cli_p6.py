# ruff: noqa: F403, F405, E501
from .audacity_cli_base import *  # noqa: F403

# fmt: off
from .audacity_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .audacity_cli_p5 import label  # noqa: E402,E501
# fmt: on


@label.command("remove")
@click.argument("index", type=int)
@handle_error
def label_remove(index):
    """Remove a label by index."""
    sess = get_session()
    sess.snapshot(f"Remove label {index}")
    removed = label_mod.remove_label(sess.get_project(), index)
    output(removed, f"Removed label: {removed.get('text', '')}")


@label.command("list")
@handle_error
def label_list():
    """List all labels."""
    sess = get_session()
    labels = label_mod.list_labels(sess.get_project())
    output(labels, "Labels:")


@cli.group()
def media():
    """Media file operations."""
    pass


@media.command("probe")
@click.argument("path")
@handle_error
def media_probe(path):
    """Analyze an audio file."""
    info = media_mod.probe_audio(path)
    output(info)


@media.command("check")
@handle_error
def media_check():
    """Check that all referenced audio files exist."""
    sess = get_session()
    result = media_mod.check_media(sess.get_project())
    output(result)


@cli.group("export")
def export_group():
    """Export/render commands."""
    pass


@export_group.command("presets")
@handle_error
def export_presets():
    """List export presets."""
    presets = export_mod.list_presets()
    output(presets, "Export presets:")


@export_group.command("preset-info")
@click.argument("name")
@handle_error
def export_preset_info(name):
    """Show preset details."""
    info = export_mod.get_preset_info(name)
    output(info)


@export_group.command("render")
@click.argument("output_path")
@click.option("--preset", "-p", default="wav", help="Export preset")
@click.option("--overwrite", is_flag=True, help="Overwrite existing file")
@click.option(
    "--channels", "-ch", type=int, default=None, help="Channel override (1 or 2)"
)
@handle_error
def export_render(output_path, preset, overwrite, channels):
    """Render the project to an audio file."""
    sess = get_session()
    result = export_mod.render_mix(
        sess.get_project(),
        output_path,
        preset=preset,
        overwrite=overwrite,
        channels_override=channels,
    )
    output(result, f"Rendered to: {output_path}")


@cli.group("session")
def session_group():
    """Session management commands."""
    pass


@session_group.command("status")
@handle_error
def session_status():
    """Show session status."""
    sess = get_session()
    output(sess.status())


@session_group.command("undo")
@handle_error
def session_undo():
    """Undo the last operation."""
    sess = get_session()
    desc = sess.undo()
    output({"undone": desc}, f"Undone: {desc}")


@session_group.command("redo")
@handle_error
def session_redo():
    """Redo the last undone operation."""
    sess = get_session()
    desc = sess.redo()
    output({"redone": desc}, f"Redone: {desc}")


@session_group.command("history")
@handle_error
def session_history():
    """Show undo history."""
    sess = get_session()
    history = sess.list_history()
    output(history, "Undo history:")
