# ruff: noqa: F403, F405, E501
from .zoom_cli_base import *  # noqa: F403

# fmt: off
from .zoom_cli_p1 import cli, handle_error, output  # noqa: E402,E501
from .zoom_cli_p4 import recording  # noqa: E402,E501
# fmt: on


@recording.command("download")
@click.argument("download_url")
@click.argument("output_path")
@click.option("--overwrite", is_flag=True, help="Overwrite existing file")
@handle_error
def recording_download(download_url, output_path, overwrite):
    """Download a recording file.

    DOWNLOAD_URL: The download URL from 'recording files' output.
    OUTPUT_PATH: Local file path to save the recording.
    """
    result = rec_mod.download_recording(download_url, output_path, overwrite)
    output(result, f"Downloaded to: {output_path}")


@recording.command("delete")
@click.argument("meeting_id")
@click.option("--confirm", is_flag=True, help="Skip confirmation")
@handle_error
def recording_delete(meeting_id, confirm):
    """Delete all recordings for a meeting."""
    if not confirm and not _repl_mode:
        click.confirm(f"Delete recordings for meeting {meeting_id}?", abort=True)
    result = rec_mod.delete_recording(meeting_id)
    output(result, "Recordings deleted.")


def main():
    cli()
