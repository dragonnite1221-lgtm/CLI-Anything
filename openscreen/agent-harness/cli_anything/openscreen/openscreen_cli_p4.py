# ruff: noqa: F403, F405, E501
from .openscreen_cli_base import *  # noqa: F403
# fmt: off
from .openscreen_cli_p1 import _auto_save, _dry_run, _session, handle_error, output  # noqa: E402,E501
from .openscreen_cli_p2 import cli  # noqa: E402,E501
# fmt: on


@cli.group()
def project():
    """Project management — new, open, save, info, settings."""
    pass
@project.command("new")
@click.option("-v", "--video", default=None, help="Source video path")
@click.option("-o", "--output", default=None, help="Save project to this path")
@handle_error
def project_new(video, output):
    """Create a new project."""
    result = proj_mod.new_project(_session, video)
    if output:
        proj_mod.save_project(_session, output)
        result["saved_to"] = output
    output_fn = globals()["output"]
    output_fn(result, "Project created")
@project.command("open")
@click.argument("path")
@handle_error
def project_open(path):
    """Open an existing .openscreen project."""
    result = proj_mod.open_project(_session, path)
    output(result, f"Opened: {path}")
@project.command("save")
@click.option("-o", "--output", "output_path", default=None, help="Save to path (default: current)")
@handle_error
def project_save(output_path=None):
    """Save the current project."""
    result = proj_mod.save_project(_session, output_path)
    output(result)
@project.command("info")
@handle_error
def project_info():
    """Show project information."""
    result = proj_mod.info(_session)
    output(result)
@project.command("set-video")
@click.argument("path")
@handle_error
def project_set_video(path):
    """Set the source video for the project."""
    result = proj_mod.set_video(_session, path)
    output(result, f"Video set: {path}")
@project.command("set")
@click.argument("key")
@click.argument("value")
@handle_error
def project_set(key, value):
    """Set a project setting (e.g., aspectRatio, wallpaper, padding)."""
    # Auto-convert numeric and boolean values
    if value.lower() in ("true", "false"):
        value = value.lower() == "true"
    else:
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass
    result = proj_mod.set_setting(_session, key, value)
    output(result)
    if _auto_save and not _dry_run and _session.project_path:
        _session.save_project()
@cli.group()
def zoom():
    """Zoom regions — add, remove, list zoom effects on timeline."""
    pass
@zoom.command("list")
@handle_error
def zoom_list():
    """List all zoom regions."""
    result = tl_mod.list_zoom_regions(_session)
    output(result)
@zoom.command("add")
@click.option("--start", required=True, type=int, help="Start time in milliseconds")
@click.option("--end", required=True, type=int, help="End time in milliseconds")
@click.option("--depth", default=3, type=int, help="Zoom depth 1-6 (default: 3)")
@click.option("--focus-x", default=0.5, type=float, help="Focus X (0-1)")
@click.option("--focus-y", default=0.5, type=float, help="Focus Y (0-1)")
@click.option("--focus-mode", default="manual", help="Focus mode: manual or auto")
@handle_error
def zoom_add(start, end, depth, focus_x, focus_y, focus_mode):
    """Add a zoom region."""
    result = tl_mod.add_zoom_region(
        _session, start, end, depth, focus_x, focus_y, focus_mode
    )
    output(result, "Zoom region added")
    if _auto_save and not _dry_run and _session.project_path:
        _session.save_project()
@zoom.command("remove")
@click.argument("region_id")
@handle_error
def zoom_remove(region_id):
    """Remove a zoom region by ID."""
    result = tl_mod.remove_zoom_region(_session, region_id)
    output(result)
    if _auto_save and not _dry_run and _session.project_path:
        _session.save_project()
@cli.group()
def speed():
    """Speed regions — add, remove, list speed changes."""
    pass
@speed.command("list")
@handle_error
def speed_list():
    """List all speed regions."""
    result = tl_mod.list_speed_regions(_session)
    output(result)
@speed.command("add")
@click.option("--start", required=True, type=int, help="Start time in ms")
@click.option("--end", required=True, type=int, help="End time in ms")
@click.option("--speed", "spd", default=1.5, type=float, help="Speed multiplier")
@handle_error
def speed_add(start, end, spd):
    """Add a speed region."""
    result = tl_mod.add_speed_region(_session, start, end, spd)
    output(result, "Speed region added")
    if _auto_save and not _dry_run and _session.project_path:
        _session.save_project()
