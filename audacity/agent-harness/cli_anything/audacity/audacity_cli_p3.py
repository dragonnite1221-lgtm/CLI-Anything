# ruff: noqa: F403, F405, E501
from .audacity_cli_base import *  # noqa: F403

# fmt: off
from .audacity_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .audacity_cli_p2 import project  # noqa: E402,E501
# fmt: on


@project.command("save")
@click.argument("path", required=False)
@handle_error
def project_save(path):
    """Save the current project."""
    sess = get_session()
    saved = sess.save_session(path)
    output({"saved": saved}, f"Saved to: {saved}")


@project.command("info")
@handle_error
def project_info():
    """Show project information."""
    sess = get_session()
    info = proj_mod.get_project_info(sess.get_project())
    output(info)


@project.command("settings")
@click.option("--sample-rate", "-sr", type=int, default=None)
@click.option("--bit-depth", "-bd", type=int, default=None)
@click.option("--channels", "-ch", type=int, default=None)
@handle_error
def project_settings(sample_rate, bit_depth, channels):
    """View or update project settings."""
    sess = get_session()
    proj = sess.get_project()
    if sample_rate or bit_depth or channels:
        sess.snapshot("Change settings")
        result = proj_mod.set_settings(proj, sample_rate, bit_depth, channels)
        output(result, "Settings updated:")
    else:
        output(proj.get("settings", {}), "Project settings:")


@project.command("json")
@handle_error
def project_json():
    """Print raw project JSON."""
    sess = get_session()
    click.echo(json.dumps(sess.get_project(), indent=2, default=str))


@cli.group()
def track():
    """Track management commands."""
    pass


@track.command("add")
@click.option("--name", "-n", default=None, help="Track name")
@click.option(
    "--type",
    "track_type",
    type=click.Choice(["audio", "label"]),
    default="audio",
    help="Track type",
)
@click.option("--volume", "-v", type=float, default=1.0, help="Volume (0.0-2.0)")
@click.option("--pan", "-p", type=float, default=0.0, help="Pan (-1.0 to 1.0)")
@handle_error
def track_add(name, track_type, volume, pan):
    """Add a new track."""
    sess = get_session()
    sess.snapshot(f"Add track: {name or 'new'}")
    result = track_mod.add_track(
        sess.get_project(),
        name=name,
        track_type=track_type,
        volume=volume,
        pan=pan,
    )
    output(result, f"Added track: {result['name']}")


@track.command("remove")
@click.argument("index", type=int)
@handle_error
def track_remove(index):
    """Remove a track by index."""
    sess = get_session()
    sess.snapshot(f"Remove track {index}")
    removed = track_mod.remove_track(sess.get_project(), index)
    output(removed, f"Removed track: {removed.get('name', '')}")


@track.command("list")
@handle_error
def track_list():
    """List all tracks."""
    sess = get_session()
    tracks = track_mod.list_tracks(sess.get_project())
    output(tracks, "Tracks:")


@track.command("set")
@click.argument("index", type=int)
@click.argument("prop")
@click.argument("value")
@handle_error
def track_set(index, prop, value):
    """Set a track property (name, mute, solo, volume, pan)."""
    sess = get_session()
    sess.snapshot(f"Set track {index} {prop}={value}")
    result = track_mod.set_track_property(sess.get_project(), index, prop, value)
    output(
        {"track": index, "property": prop, "value": value},
        f"Set track {index} {prop} = {value}",
    )


@cli.group()
def clip():
    """Clip management commands."""
    pass


@clip.command("import")
@click.argument("path")
@handle_error
def clip_import(path):
    """Probe/import an audio file (show metadata)."""
    info = clip_mod.import_audio(path)
    output(info, f"Audio file: {path}")
