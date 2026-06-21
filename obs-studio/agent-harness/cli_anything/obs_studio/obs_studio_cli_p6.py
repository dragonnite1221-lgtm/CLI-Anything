# ruff: noqa: F403, F405, E501
from .obs_studio_cli_base import *  # noqa: F403

# fmt: off
from .obs_studio_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .obs_studio_cli_p5 import audio_group  # noqa: E402,E501
# fmt: on


@audio_group.command("volume")
@click.argument("index", type=int)
@click.argument("level", type=float)
@handle_error
def audio_volume(index, level):
    """Set volume for an audio source (0.0-3.0)."""
    sess = get_session()
    sess.snapshot(f"Set audio {index} volume={level}")
    src = audio_mod.set_volume(sess.get_project(), index, level)
    output({"audio": index, "volume": level}, f"Volume set to {level}")


@audio_group.command("mute")
@click.argument("index", type=int)
@handle_error
def audio_mute(index):
    """Mute an audio source."""
    sess = get_session()
    sess.snapshot(f"Mute audio {index}")
    src = audio_mod.mute(sess.get_project(), index)
    output({"audio": index, "muted": True}, f"Muted audio {index}")


@audio_group.command("unmute")
@click.argument("index", type=int)
@handle_error
def audio_unmute(index):
    """Unmute an audio source."""
    sess = get_session()
    sess.snapshot(f"Unmute audio {index}")
    src = audio_mod.unmute(sess.get_project(), index)
    output({"audio": index, "muted": False}, f"Unmuted audio {index}")


@audio_group.command("monitor")
@click.argument("index", type=int)
@click.argument(
    "monitor_type", type=click.Choice(["none", "monitor_only", "monitor_and_output"])
)
@handle_error
def audio_monitor(index, monitor_type):
    """Set audio monitoring type."""
    sess = get_session()
    sess.snapshot(f"Set audio {index} monitor={monitor_type}")
    src = audio_mod.set_monitor(sess.get_project(), index, monitor_type)
    output({"audio": index, "monitor": monitor_type}, f"Monitor set to {monitor_type}")


@audio_group.command("list")
@handle_error
def audio_list():
    """List all audio sources."""
    sess = get_session()
    sources = audio_mod.list_audio(sess.get_project())
    output(sources, "Audio sources:")


@cli.group("transition")
def transition_group():
    """Transition management commands."""
    pass


@transition_group.command("add")
@click.argument(
    "transition_type", type=click.Choice(sorted(trans_mod.TRANSITION_TYPES.keys()))
)
@click.option("--name", "-n", default=None, help="Transition name")
@click.option("--duration", "-d", type=int, default=None, help="Duration in ms")
@handle_error
def transition_add(transition_type, name, duration):
    """Add a transition."""
    sess = get_session()
    sess.snapshot(f"Add transition: {transition_type}")
    trans = trans_mod.add_transition(
        sess.get_project(),
        transition_type,
        name=name,
        duration=duration,
    )
    output(trans, f"Added transition: {trans['name']}")


@transition_group.command("remove")
@click.argument("index", type=int)
@handle_error
def transition_remove(index):
    """Remove a transition."""
    sess = get_session()
    sess.snapshot(f"Remove transition {index}")
    removed = trans_mod.remove_transition(sess.get_project(), index)
    output(removed, f"Removed transition: {removed['name']}")


@transition_group.command("set-active")
@click.argument("index", type=int)
@handle_error
def transition_set_active(index):
    """Set the active transition."""
    sess = get_session()
    sess.snapshot(f"Set active transition {index}")
    result = trans_mod.set_active_transition(sess.get_project(), index)
    output(result, f"Active transition: {result['active_transition']}")


@transition_group.command("duration")
@click.argument("index", type=int)
@click.argument("duration", type=int)
@handle_error
def transition_duration(index, duration):
    """Set transition duration in milliseconds."""
    sess = get_session()
    sess.snapshot(f"Set transition {index} duration={duration}")
    trans = trans_mod.set_duration(sess.get_project(), index, duration)
    output(trans, f"Duration set to {duration}ms")


@transition_group.command("list")
@handle_error
def transition_list():
    """List all transitions."""
    sess = get_session()
    transitions = trans_mod.list_transitions(sess.get_project())
    output(transitions, "Transitions:")


@cli.group("output")
def output_group():
    """Output/streaming/recording configuration."""
    pass
