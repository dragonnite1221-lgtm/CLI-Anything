# ruff: noqa: F403, F405, E501
from .audacity_cli_base import *  # noqa: F403

# fmt: off
from .audacity_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .audacity_cli_p3 import clip  # noqa: E402,E501
# fmt: on


@clip.command("add")
@click.argument("track_index", type=int)
@click.argument("source")
@click.option("--name", "-n", default=None, help="Clip name")
@click.option("--start", "-s", type=float, default=0.0, help="Start time on timeline")
@click.option("--end", "-e", type=float, default=None, help="End time on timeline")
@click.option("--trim-start", type=float, default=0.0, help="Trim start within source")
@click.option("--trim-end", type=float, default=None, help="Trim end within source")
@click.option("--volume", "-v", type=float, default=1.0, help="Clip volume")
@handle_error
def clip_add(track_index, source, name, start, end, trim_start, trim_end, volume):
    """Add an audio clip to a track."""
    sess = get_session()
    sess.snapshot(f"Add clip to track {track_index}")
    result = clip_mod.add_clip(
        sess.get_project(),
        track_index,
        source,
        name=name,
        start_time=start,
        end_time=end,
        trim_start=trim_start,
        trim_end=trim_end,
        volume=volume,
    )
    output(result, f"Added clip: {result['name']}")


@clip.command("remove")
@click.argument("track_index", type=int)
@click.argument("clip_index", type=int)
@handle_error
def clip_remove(track_index, clip_index):
    """Remove a clip from a track."""
    sess = get_session()
    sess.snapshot(f"Remove clip {clip_index} from track {track_index}")
    removed = clip_mod.remove_clip(sess.get_project(), track_index, clip_index)
    output(removed, f"Removed clip: {removed.get('name', '')}")


@clip.command("trim")
@click.argument("track_index", type=int)
@click.argument("clip_index", type=int)
@click.option("--trim-start", type=float, default=None, help="New trim start")
@click.option("--trim-end", type=float, default=None, help="New trim end")
@handle_error
def clip_trim(track_index, clip_index, trim_start, trim_end):
    """Trim a clip's start and/or end."""
    sess = get_session()
    sess.snapshot(f"Trim clip {clip_index} on track {track_index}")
    result = clip_mod.trim_clip(
        sess.get_project(),
        track_index,
        clip_index,
        trim_start=trim_start,
        trim_end=trim_end,
    )
    output(result, "Clip trimmed")


@clip.command("split")
@click.argument("track_index", type=int)
@click.argument("clip_index", type=int)
@click.argument("split_time", type=float)
@handle_error
def clip_split(track_index, clip_index, split_time):
    """Split a clip at a given time position."""
    sess = get_session()
    sess.snapshot(f"Split clip {clip_index} at {split_time}")
    result = clip_mod.split_clip(
        sess.get_project(),
        track_index,
        clip_index,
        split_time,
    )
    output(result, f"Split clip into 2 parts at {split_time}s")


@clip.command("move")
@click.argument("track_index", type=int)
@click.argument("clip_index", type=int)
@click.argument("new_start", type=float)
@handle_error
def clip_move(track_index, clip_index, new_start):
    """Move a clip to a new start time."""
    sess = get_session()
    sess.snapshot(f"Move clip {clip_index} to {new_start}")
    result = clip_mod.move_clip(
        sess.get_project(),
        track_index,
        clip_index,
        new_start,
    )
    output(result, f"Moved clip to {new_start}s")


@clip.command("list")
@click.argument("track_index", type=int)
@handle_error
def clip_list(track_index):
    """List clips on a track."""
    sess = get_session()
    clips = clip_mod.list_clips(sess.get_project(), track_index)
    output(clips, f"Clips on track {track_index}:")


@cli.group("effect")
def effect_group():
    """Effect management commands."""
    pass


@effect_group.command("list-available")
@click.option(
    "--category",
    "-c",
    type=str,
    default=None,
    help="Filter by category: volume, fade, transform, delay, eq, dynamics, generate, restoration",
)
@handle_error
def effect_list_available(category):
    """List all available effects."""
    effects = fx_mod.list_available(category)
    output(effects, "Available effects:")


@effect_group.command("info")
@click.argument("name")
@handle_error
def effect_info(name):
    """Show details about an effect."""
    info = fx_mod.get_effect_info(name)
    output(info)
