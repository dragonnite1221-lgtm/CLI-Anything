# ruff: noqa: F403, F405, E501
from .gimp_cli_base import *  # noqa: F403

# fmt: off
from .gimp_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .gimp_cli_p4 import filter_group  # noqa: E402,E501
# fmt: on


@filter_group.command("remove")
@click.argument("filter_index", type=int)
@click.option("--layer", "-l", "layer_index", type=int, default=0)
@handle_error
def filter_remove(filter_index, layer_index):
    """Remove a filter by index."""
    sess = get_session()
    sess.snapshot(f"Remove filter {filter_index} from layer {layer_index}")
    result = filt_mod.remove_filter(sess.get_project(), filter_index, layer_index)
    output(result, f"Removed filter {filter_index}")


@filter_group.command("set")
@click.argument("filter_index", type=int)
@click.argument("param")
@click.argument("value")
@click.option("--layer", "-l", "layer_index", type=int, default=0)
@handle_error
def filter_set(filter_index, param, value, layer_index):
    """Set a filter parameter."""
    try:
        value = float(value) if "." in str(value) else int(value)
    except ValueError:
        pass
    sess = get_session()
    sess.snapshot(f"Set filter {filter_index} {param}={value}")
    filt_mod.set_filter_param(
        sess.get_project(), filter_index, param, value, layer_index
    )
    output(
        {"filter": filter_index, "param": param, "value": value},
        f"Set filter {filter_index} {param} = {value}",
    )


@filter_group.command("list")
@click.option("--layer", "-l", "layer_index", type=int, default=0)
@handle_error
def filter_list(layer_index):
    """List filters on a layer."""
    sess = get_session()
    filters = filt_mod.list_filters(sess.get_project(), layer_index)
    output(filters, f"Filters on layer {layer_index}:")


@cli.group()
def media():
    """Media file operations."""
    pass


@media.command("probe")
@click.argument("path")
@handle_error
def media_probe(path):
    """Analyze an image file."""
    info = media_mod.probe_image(path)
    output(info)


@media.command("list")
@handle_error
def media_list():
    """List media files referenced in the project."""
    sess = get_session()
    media = media_mod.list_media_in_project(sess.get_project())
    output(media, "Referenced media files:")


@media.command("check")
@handle_error
def media_check():
    """Check that all referenced media files exist."""
    sess = get_session()
    result = media_mod.check_media(sess.get_project())
    output(result)


@media.command("histogram")
@click.argument("path")
@handle_error
def media_histogram(path):
    """Show histogram analysis of an image."""
    result = media_mod.get_image_histogram(path)
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
@click.option("--preset", "-p", default="png", help="Export preset")
@click.option("--overwrite", is_flag=True, help="Overwrite existing file")
@click.option("--quality", "-q", type=int, default=None, help="Quality override")
@click.option("--format", "fmt", type=str, default=None, help="Format override")
@handle_error
def export_render(output_path, preset, overwrite, quality, fmt):
    """Render the project to an image file."""
    sess = get_session()
    result = export_mod.render(
        sess.get_project(),
        output_path,
        preset=preset,
        overwrite=overwrite,
        quality=quality,
        format_override=fmt,
    )
    output(result, f"Rendered to: {output_path}")


@cli.group()
def session():
    """Session management commands."""
    pass


@session.command("status")
@handle_error
def session_status():
    """Show session status."""
    sess = get_session()
    output(sess.status())


@session.command("undo")
@handle_error
def session_undo():
    """Undo the last operation."""
    sess = get_session()
    desc = sess.undo()
    output({"undone": desc}, f"Undone: {desc}")


@session.command("redo")
@handle_error
def session_redo():
    """Redo the last undone operation."""
    sess = get_session()
    desc = sess.redo()
    output({"redone": desc}, f"Redone: {desc}")
