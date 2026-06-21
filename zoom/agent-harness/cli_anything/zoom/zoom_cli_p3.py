# ruff: noqa: F403, F405, E501
from .zoom_cli_base import *  # noqa: F403

# fmt: off
from .zoom_cli_p1 import cli, handle_error, output  # noqa: E402,E501
from .zoom_cli_p2 import auth  # noqa: E402,E501
# fmt: on


@auth.command("logout")
@handle_error
def auth_logout():
    """Remove saved tokens."""
    result = auth_mod.logout()
    output(result, "Logged out.")


@cli.group()
def meeting():
    """Meeting management commands."""
    pass


@meeting.command("create")
@click.option("--topic", "-t", required=True, help="Meeting topic/title")
@click.option(
    "--start-time",
    "-s",
    default=None,
    help="Start time (ISO 8601, e.g., 2025-01-15T10:00:00Z)",
)
@click.option("--duration", "-d", type=int, default=60, help="Duration in minutes")
@click.option("--timezone", default="UTC", help="Timezone (e.g., Asia/Shanghai)")
@click.option("--agenda", default="", help="Meeting description/agenda")
@click.option("--password", default=None, help="Meeting password")
@click.option(
    "--auto-recording",
    type=click.Choice(["none", "local", "cloud"]),
    default="none",
    help="Auto-recording mode",
)
@click.option("--waiting-room", is_flag=True, help="Enable waiting room")
@click.option("--join-before-host", is_flag=True, help="Allow join before host")
@click.option("--no-mute", is_flag=True, help="Don't mute participants on entry")
@handle_error
def meeting_create(
    topic,
    start_time,
    duration,
    timezone,
    agenda,
    password,
    auto_recording,
    waiting_room,
    join_before_host,
    no_mute,
):
    """Create a new Zoom meeting."""
    result = meet_mod.create_meeting(
        topic=topic,
        start_time=start_time,
        duration=duration,
        timezone=timezone,
        agenda=agenda,
        password=password,
        auto_recording=auto_recording,
        waiting_room=waiting_room,
        join_before_host=join_before_host,
        mute_upon_entry=not no_mute,
    )
    output(result, f"Meeting created: {topic}")


@meeting.command("list")
@click.option(
    "--status",
    "-s",
    type=click.Choice(["upcoming", "scheduled", "live", "pending"]),
    default="upcoming",
    help="Meeting status filter",
)
@click.option("--page-size", type=int, default=30, help="Results per page")
@handle_error
def meeting_list(status, page_size):
    """List meetings."""
    result = meet_mod.list_meetings(status=status, page_size=page_size)
    output(result, f"Meetings ({status}):")


@meeting.command("info")
@click.argument("meeting_id")
@handle_error
def meeting_info(meeting_id):
    """Get meeting details."""
    result = meet_mod.get_meeting(meeting_id)
    output(result)


@meeting.command("update")
@click.argument("meeting_id")
@click.option("--topic", "-t", default=None, help="New topic")
@click.option("--start-time", "-s", default=None, help="New start time")
@click.option("--duration", "-d", type=int, default=None, help="New duration")
@click.option("--timezone", default=None, help="New timezone")
@click.option("--agenda", default=None, help="New agenda")
@click.option("--password", default=None, help="New password")
@click.option(
    "--auto-recording",
    type=click.Choice(["none", "local", "cloud"]),
    default=None,
    help="Auto-recording mode",
)
@handle_error
def meeting_update(
    meeting_id, topic, start_time, duration, timezone, agenda, password, auto_recording
):
    """Update a meeting."""
    result = meet_mod.update_meeting(
        meeting_id=meeting_id,
        topic=topic,
        start_time=start_time,
        duration=duration,
        timezone=timezone,
        agenda=agenda,
        password=password,
        auto_recording=auto_recording,
    )
    output(result, f"Meeting {meeting_id} updated.")


@meeting.command("delete")
@click.argument("meeting_id")
@click.option("--confirm", is_flag=True, help="Skip confirmation")
@handle_error
def meeting_delete(meeting_id, confirm):
    """Delete a meeting."""
    if not confirm and not _repl_mode:
        click.confirm(f"Delete meeting {meeting_id}?", abort=True)
    result = meet_mod.delete_meeting(meeting_id)
    output(result, f"Meeting {meeting_id} deleted.")


@meeting.command("join")
@click.argument("meeting_id")
@handle_error
def meeting_join(meeting_id):
    """Open meeting join URL in browser."""
    urls = meet_mod.get_join_url(meeting_id)
    join_url = urls.get("join_url", "")
    if not join_url:
        raise RuntimeError("No join URL available for this meeting.")
    webbrowser.open(join_url)
    output(urls, f"Opening meeting in browser...")
