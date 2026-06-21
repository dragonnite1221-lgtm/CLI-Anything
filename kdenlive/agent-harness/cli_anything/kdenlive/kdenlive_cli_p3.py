# ruff: noqa: F403, F405, E501
from .kdenlive_cli_base import *  # noqa: F403

# fmt: off
from .kdenlive_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .kdenlive_cli_p2 import project  # noqa: E402,E501
# fmt: on


@project.command("open")
@click.argument("path")
@handle_error
def project_open(path):
    """Open an existing project."""
    proj = proj_mod.open_project(path)
    sess = get_session()
    sess.set_project(proj, path)
    info = proj_mod.get_project_info(proj)
    output(info, f"Opened: {path}")


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


@project.command("profiles")
@handle_error
def project_profiles():
    """List available video profiles."""
    profiles = proj_mod.list_profiles()
    output(profiles, "Available profiles:")


@project.command("json")
@handle_error
def project_json():
    """Print raw project JSON."""
    sess = get_session()
    click.echo(json.dumps(sess.get_project(), indent=2, default=str))


@cli.group("bin")
def bin_group():
    """Media bin management commands."""
    pass


@bin_group.command("import")
@click.argument("source")
@click.option("--name", "-n", default=None, help="Clip name")
@click.option("--duration", "-d", type=float, default=0.0, help="Duration in seconds")
@click.option(
    "--type",
    "clip_type",
    type=click.Choice(["video", "audio", "image", "color", "title"]),
    default="video",
)
@handle_error
def bin_import(source, name, duration, clip_type):
    """Import a clip into the media bin."""
    sess = get_session()
    sess.snapshot("Import clip")
    clip = bin_mod.import_clip(
        sess.get_project(), source, name=name, duration=duration, clip_type=clip_type
    )
    output(clip, f"Imported: {clip['name']}")


@bin_group.command("remove")
@click.argument("clip_id")
@handle_error
def bin_remove(clip_id):
    """Remove a clip from the bin."""
    sess = get_session()
    sess.snapshot(f"Remove clip {clip_id}")
    removed = bin_mod.remove_clip(sess.get_project(), clip_id)
    output(removed, f"Removed clip: {removed['name']}")


@bin_group.command("list")
@handle_error
def bin_list():
    """List all clips in the bin."""
    sess = get_session()
    clips = bin_mod.list_clips(sess.get_project())
    output(clips, "Bin clips:")


@bin_group.command("get")
@click.argument("clip_id")
@handle_error
def bin_get(clip_id):
    """Get detailed clip info."""
    sess = get_session()
    clip = bin_mod.get_clip(sess.get_project(), clip_id)
    output(clip)


@cli.group()
def timeline():
    """Timeline management commands."""
    pass


@timeline.command("add-track")
@click.option("--name", "-n", default=None, help="Track name")
@click.option(
    "--type", "track_type", type=click.Choice(["video", "audio"]), default="video"
)
@click.option("--mute", is_flag=True)
@click.option("--hide", is_flag=True)
@click.option("--locked", is_flag=True)
@handle_error
def timeline_add_track(name, track_type, mute, hide, locked):
    """Add a track to the timeline."""
    sess = get_session()
    sess.snapshot("Add track")
    track = tl_mod.add_track(
        sess.get_project(),
        name=name,
        track_type=track_type,
        mute=mute,
        hide=hide,
        locked=locked,
    )
    output(track, f"Added track: {track['name']}")


@timeline.command("remove-track")
@click.argument("track_id", type=int)
@handle_error
def timeline_remove_track(track_id):
    """Remove a track."""
    sess = get_session()
    sess.snapshot(f"Remove track {track_id}")
    removed = tl_mod.remove_track(sess.get_project(), track_id)
    output(removed, f"Removed track: {removed['name']}")
