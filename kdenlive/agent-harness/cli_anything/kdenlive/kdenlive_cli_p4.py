# ruff: noqa: F403, F405, E501
from .kdenlive_cli_base import *  # noqa: F403

# fmt: off
from .kdenlive_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .kdenlive_cli_p3 import timeline  # noqa: E402,E501
# fmt: on


@timeline.command("add-clip")
@click.argument("track_id", type=int)
@click.argument("clip_id")
@click.option("--position", "-p", type=float, default=0.0, help="Position in seconds")
@click.option("--in", "in_point", type=float, default=0.0, help="In point in seconds")
@click.option(
    "--out", "out_point", type=float, default=None, help="Out point in seconds"
)
@handle_error
def timeline_add_clip(track_id, clip_id, position, in_point, out_point):
    """Add a clip to a track."""
    sess = get_session()
    sess.snapshot("Add clip to track")
    entry = tl_mod.add_clip_to_track(
        sess.get_project(),
        track_id,
        clip_id,
        position=position,
        in_point=in_point,
        out_point=out_point,
    )
    output(entry, "Added clip to track")


@timeline.command("remove-clip")
@click.argument("track_id", type=int)
@click.argument("clip_index", type=int)
@handle_error
def timeline_remove_clip(track_id, clip_index):
    """Remove a clip from a track."""
    sess = get_session()
    sess.snapshot("Remove clip from track")
    removed = tl_mod.remove_clip_from_track(sess.get_project(), track_id, clip_index)
    output(removed, "Removed clip from track")


@timeline.command("trim")
@click.argument("track_id", type=int)
@click.argument("clip_index", type=int)
@click.option("--in", "new_in", type=float, default=None, help="New in point")
@click.option("--out", "new_out", type=float, default=None, help="New out point")
@handle_error
def timeline_trim(track_id, clip_index, new_in, new_out):
    """Trim a clip's in/out points."""
    sess = get_session()
    sess.snapshot("Trim clip")
    result = tl_mod.trim_clip(
        sess.get_project(), track_id, clip_index, new_in=new_in, new_out=new_out
    )
    output(result, "Trimmed clip")


@timeline.command("split")
@click.argument("track_id", type=int)
@click.argument("clip_index", type=int)
@click.argument("split_at", type=float)
@handle_error
def timeline_split(track_id, clip_index, split_at):
    """Split a clip at a time offset."""
    sess = get_session()
    sess.snapshot("Split clip")
    parts = tl_mod.split_clip(sess.get_project(), track_id, clip_index, split_at)
    output(parts, "Split clip into two parts")


@timeline.command("move")
@click.argument("track_id", type=int)
@click.argument("clip_index", type=int)
@click.argument("new_position", type=float)
@handle_error
def timeline_move(track_id, clip_index, new_position):
    """Move a clip to a new position."""
    sess = get_session()
    sess.snapshot("Move clip")
    result = tl_mod.move_clip(sess.get_project(), track_id, clip_index, new_position)
    output(result, f"Moved clip to {new_position}")


@timeline.command("list")
@handle_error
def timeline_list():
    """List all tracks."""
    sess = get_session()
    tracks = tl_mod.list_tracks(sess.get_project())
    output(tracks, "Tracks:")


@cli.group("filter")
def filter_group():
    """Filter/effect management commands."""
    pass


@filter_group.command("add")
@click.argument("track_id", type=int)
@click.argument("clip_index", type=int)
@click.argument("filter_name")
@click.option("--param", "-p", multiple=True, help="Parameter: key=value")
@handle_error
def filter_add(track_id, clip_index, filter_name, param):
    """Add a filter to a clip."""
    params = {}
    for p in param:
        if "=" not in p:
            raise ValueError(f"Invalid param format: '{p}'. Use key=value.")
        k, v = p.split("=", 1)
        try:
            v = float(v) if "." in v else int(v)
        except ValueError:
            pass
        params[k] = v

    sess = get_session()
    sess.snapshot(f"Add filter {filter_name}")
    result = filt_mod.add_filter(
        sess.get_project(),
        track_id,
        clip_index,
        filter_name,
        params=params if params else None,
    )
    output(result, f"Added filter: {filter_name}")


@filter_group.command("remove")
@click.argument("track_id", type=int)
@click.argument("clip_index", type=int)
@click.argument("filter_index", type=int)
@handle_error
def filter_remove(track_id, clip_index, filter_index):
    """Remove a filter from a clip."""
    sess = get_session()
    sess.snapshot("Remove filter")
    removed = filt_mod.remove_filter(
        sess.get_project(), track_id, clip_index, filter_index
    )
    output(removed, f"Removed filter: {removed['name']}")
