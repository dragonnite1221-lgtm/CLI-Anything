# ruff: noqa: F403, F405, E501
from .obs_studio_cli_base import *  # noqa: F403

# fmt: off
from .obs_studio_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .obs_studio_cli_p6 import output_group  # noqa: E402,E501
# fmt: on


@output_group.command("streaming")
@click.option(
    "--service",
    type=click.Choice(["twitch", "youtube", "facebook", "custom"]),
    default=None,
)
@click.option("--server", type=str, default=None)
@click.option("--key", type=str, default=None)
@handle_error
def output_streaming(service, server, key):
    """Configure streaming settings."""
    sess = get_session()
    sess.snapshot("Update streaming settings")
    result = out_mod.set_streaming(
        sess.get_project(), service=service, server=server, key=key
    )
    globals()["output"](result, "Streaming settings updated")


@output_group.command("recording")
@click.option("--path", type=str, default=None)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["mkv", "mp4", "mov", "flv", "ts"]),
    default=None,
)
@click.option(
    "--quality", type=click.Choice(["low", "medium", "high", "lossless"]), default=None
)
@handle_error
def output_recording(path, fmt, quality):
    """Configure recording settings."""
    sess = get_session()
    sess.snapshot("Update recording settings")
    result = out_mod.set_recording(
        sess.get_project(), path=path, fmt=fmt, quality=quality
    )
    globals()["output"](result, "Recording settings updated")


@output_group.command("settings")
@click.option("--width", type=int, default=None)
@click.option("--height", type=int, default=None)
@click.option("--fps", type=int, default=None)
@click.option("--video-bitrate", type=int, default=None)
@click.option("--audio-bitrate", type=int, default=None)
@click.option("--encoder", type=str, default=None)
@click.option("--preset", type=str, default=None, help="Apply encoding preset")
@handle_error
def output_settings(width, height, fps, video_bitrate, audio_bitrate, encoder, preset):
    """Configure output settings."""
    sess = get_session()
    sess.snapshot("Update output settings")
    result = out_mod.set_output_settings(
        sess.get_project(),
        output_width=width,
        output_height=height,
        fps=fps,
        video_bitrate=video_bitrate,
        audio_bitrate=audio_bitrate,
        encoder=encoder,
        preset=preset,
    )
    globals()["output"](result, "Output settings updated")


@output_group.command("info")
@handle_error
def output_info():
    """Show current output configuration."""
    sess = get_session()
    info = out_mod.get_output_info(sess.get_project())
    globals()["output"](info)


@output_group.command("presets")
@handle_error
def output_presets():
    """List available encoding presets."""
    presets = out_mod.list_encoding_presets()
    globals()["output"](presets, "Encoding presets:")


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


@session.command("history")
@handle_error
def session_history():
    """Show undo history."""
    sess = get_session()
    history = sess.list_history()
    output(history, "Undo history:")


def main():
    cli()
