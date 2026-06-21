# ruff: noqa: F403, F405, E501
from .zoom_cli_base import *  # noqa: F403

# fmt: off
from .zoom_cli_p1 import cli, handle_error, output  # noqa: E402,E501
from .zoom_cli_p3 import meeting  # noqa: E402,E501
# fmt: on


@meeting.command("start")
@click.argument("meeting_id")
@handle_error
def meeting_start(meeting_id):
    """Open meeting start URL in browser (host only)."""
    urls = meet_mod.get_join_url(meeting_id)
    start_url = urls.get("start_url", "")
    if not start_url:
        raise RuntimeError("No start URL available for this meeting.")
    webbrowser.open(start_url)
    output(urls, f"Starting meeting in browser...")


@cli.group()
def participant():
    """Participant management commands."""
    pass


@participant.command("add")
@click.argument("meeting_id")
@click.option("--email", "-e", required=True, help="Participant email")
@click.option("--first-name", default="", help="First name")
@click.option("--last-name", default="", help="Last name")
@handle_error
def participant_add(meeting_id, email, first_name, last_name):
    """Register a participant for a meeting."""
    result = part_mod.add_registrant(
        meeting_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    output(result, f"Registered: {email}")


@participant.command("add-batch")
@click.argument("meeting_id")
@click.argument("csv_file", type=click.Path(exists=True))
@handle_error
def participant_add_batch(meeting_id, csv_file):
    """Batch register participants from a CSV file.

    CSV format: email,first_name,last_name (header row required)
    """
    import csv

    registrants = []
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            registrants.append(
                {
                    "email": row.get("email", ""),
                    "first_name": row.get("first_name", ""),
                    "last_name": row.get("last_name", ""),
                }
            )

    result = part_mod.add_batch_registrants(meeting_id, registrants)
    output(
        result,
        f"Batch registration: {result['registered']} succeeded, {result['failed']} failed",
    )


@participant.command("list")
@click.argument("meeting_id")
@click.option(
    "--status",
    "-s",
    type=click.Choice(["approved", "pending", "denied"]),
    default="approved",
    help="Registration status filter",
)
@handle_error
def participant_list(meeting_id, status):
    """List registered participants."""
    result = part_mod.list_registrants(meeting_id, status=status)
    output(result, f"Registrants ({status}):")


@participant.command("remove")
@click.argument("meeting_id")
@click.argument("registrant_id")
@handle_error
def participant_remove(meeting_id, registrant_id):
    """Cancel a participant's registration."""
    result = part_mod.remove_registrant(meeting_id, registrant_id)
    output(result, "Registration cancelled.")


@participant.command("attended")
@click.argument("meeting_id", metavar="MEETING_UUID")
@handle_error
def participant_attended(meeting_id):
    """List participants who attended a past meeting.

    Requires the meeting UUID (not the numeric ID).
    """
    result = part_mod.list_past_participants(meeting_id)
    output(result, "Past participants:")


@cli.group()
def recording():
    """Cloud recording management."""
    pass


@recording.command("list")
@click.option("--from", "from_date", default="", help="Start date (YYYY-MM-DD)")
@click.option("--to", "to_date", default="", help="End date (YYYY-MM-DD)")
@click.option("--page-size", type=int, default=30, help="Results per page")
@handle_error
def recording_list(from_date, to_date, page_size):
    """List cloud recordings."""
    result = rec_mod.list_recordings(
        from_date=from_date,
        to_date=to_date,
        page_size=page_size,
    )
    output(result, "Cloud recordings:")


@recording.command("files")
@click.argument("meeting_id")
@handle_error
def recording_files(meeting_id):
    """List recording files for a specific meeting."""
    result = rec_mod.get_meeting_recordings(meeting_id)
    output(result)
