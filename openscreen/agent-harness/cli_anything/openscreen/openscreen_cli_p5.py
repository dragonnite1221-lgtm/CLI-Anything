# ruff: noqa: F403, F405, E501
from .openscreen_cli_base import *  # noqa: F403
# fmt: off
from .openscreen_cli_p1 import _auto_save, _dry_run, _session, handle_error, output  # noqa: E402,E501
from .openscreen_cli_p2 import cli  # noqa: E402,E501
from .openscreen_cli_p4 import speed  # noqa: E402,E501
# fmt: on


@speed.command("remove")
@click.argument("region_id")
@handle_error
def speed_remove(region_id):
    """Remove a speed region by ID."""
    result = tl_mod.remove_speed_region(_session, region_id)
    output(result)
    if _auto_save and not _dry_run and _session.project_path:
        _session.save_project()
@cli.group()
def trim():
    """Trim regions — cut out sections of the recording."""
    pass
@trim.command("list")
@handle_error
def trim_list():
    """List all trim regions."""
    result = tl_mod.list_trim_regions(_session)
    output(result)
@trim.command("add")
@click.option("--start", required=True, type=int, help="Start time in ms")
@click.option("--end", required=True, type=int, help="End time in ms")
@handle_error
def trim_add(start, end):
    """Add a trim region (cuts this section out)."""
    result = tl_mod.add_trim_region(_session, start, end)
    output(result, "Trim region added")
    if _auto_save and not _dry_run and _session.project_path:
        _session.save_project()
@trim.command("remove")
@click.argument("region_id")
@handle_error
def trim_remove(region_id):
    """Remove a trim region by ID."""
    result = tl_mod.remove_trim_region(_session, region_id)
    output(result)
@cli.group()
def crop():
    """Crop — set the visible area of the recording."""
    pass
@crop.command("get")
@handle_error
def crop_get():
    """Show current crop region."""
    result = tl_mod.get_crop(_session)
    output(result)
@crop.command("set")
@click.option("--x", default=0.0, type=float, help="Left edge (0-1)")
@click.option("--y", default=0.0, type=float, help="Top edge (0-1)")
@click.option("--width", "w", default=1.0, type=float, help="Width (0-1)")
@click.option("--height", "h", default=1.0, type=float, help="Height (0-1)")
@handle_error
def crop_set(x, y, w, h):
    """Set crop region (normalized 0-1 coordinates)."""
    result = tl_mod.set_crop(_session, x, y, w, h)
    output(result, "Crop updated")
    if _auto_save and not _dry_run and _session.project_path:
        _session.save_project()
@cli.group()
def annotation():
    """Annotations — add text overlays to the recording."""
    pass
@annotation.command("list")
@handle_error
def annotation_list():
    """List all annotations."""
    result = tl_mod.list_annotations(_session)
    output(result)
@annotation.command("add-text")
@click.option("--start", required=True, type=int, help="Start time in ms")
@click.option("--end", required=True, type=int, help="End time in ms")
@click.option("--text", required=True, help="Text content")
@click.option("--x", default=0.5, type=float, help="X position (0-1)")
@click.option("--y", default=0.5, type=float, help="Y position (0-1)")
@click.option("--font-size", default=32, type=int, help="Font size")
@click.option("--color", default="#ffffff", help="Text color (hex)")
@click.option("--bg-color", default="#000000", help="Background color (hex)")
@handle_error
def annotation_add_text(start, end, text, x, y, font_size, color, bg_color):
    """Add a text annotation."""
    result = tl_mod.add_text_annotation(
        _session, start, end, text, x, y, font_size, color, bg_color
    )
    output(result, "Annotation added")
    if _auto_save and not _dry_run and _session.project_path:
        _session.save_project()
@annotation.command("remove")
@click.argument("region_id")
@handle_error
def annotation_remove(region_id):
    """Remove an annotation by ID."""
    result = tl_mod.remove_annotation(_session, region_id)
    output(result)
@cli.group()
def media():
    """Media — probe and inspect video files."""
    pass
@media.command("probe")
@click.argument("path")
@handle_error
def media_probe(path):
    """Probe a video file and show metadata."""
    result = media_mod.probe(path)
    output(result)
@media.command("check")
@click.argument("path")
@handle_error
def media_check(path):
    """Check if a video file is valid."""
    result = media_mod.check_video(path)
    output(result)
@media.command("thumbnail")
@click.argument("input_path")
@click.argument("output_path")
@click.option("-t", "--time", "time_s", default=0.0, help="Time in seconds")
@handle_error
def media_thumbnail(input_path, output_path, time_s):
    """Extract a thumbnail frame from a video."""
    result = media_mod.extract_thumbnail(input_path, output_path, time_s)
    output(result)
