# ruff: noqa: F403, F405, E501
from .meetings_base import *  # noqa: F403

# fmt: off
from .meetings_p1 import _format_meeting  # noqa: E402,E501
# fmt: on


def get_meeting(meeting_id: int | str) -> dict:
    """Get detailed information about a specific meeting.

    Args:
        meeting_id: The Zoom meeting ID.

    Returns:
        Meeting details dict.
    """
    result = api_get(f"/meetings/{meeting_id}")
    return _format_meeting(result)


def update_meeting(
    meeting_id: int | str,
    topic: str | None = None,
    start_time: str | None = None,
    duration: int | None = None,
    timezone: str | None = None,
    agenda: str | None = None,
    password: str | None = None,
    auto_recording: str | None = None,
    waiting_room: bool | None = None,
    join_before_host: bool | None = None,
    mute_upon_entry: bool | None = None,
) -> dict:
    """Update an existing meeting.

    Only provided fields are updated; None fields are left unchanged.

    Returns:
        Dict confirming the update.
    """
    body: dict[str, Any] = {}
    settings: dict[str, Any] = {}

    if topic is not None:
        body["topic"] = topic
    if start_time is not None:
        body["start_time"] = start_time
    if duration is not None:
        body["duration"] = duration
    if timezone is not None:
        body["timezone"] = timezone
    if agenda is not None:
        body["agenda"] = agenda
    if password is not None:
        body["password"] = password

    if auto_recording is not None:
        settings["auto_recording"] = auto_recording
    if waiting_room is not None:
        settings["waiting_room"] = waiting_room
    if join_before_host is not None:
        settings["join_before_host"] = join_before_host
    if mute_upon_entry is not None:
        settings["mute_upon_entry"] = mute_upon_entry

    if settings:
        body["settings"] = settings

    if not body:
        raise ValueError("No fields provided for update.")

    api_patch(f"/meetings/{meeting_id}", body)

    return {"status": "updated", "meeting_id": str(meeting_id)}


def delete_meeting(meeting_id: int | str) -> dict:
    """Delete a scheduled meeting.

    Args:
        meeting_id: The Zoom meeting ID.

    Returns:
        Dict confirming deletion.
    """
    api_delete(f"/meetings/{meeting_id}")
    return {"status": "deleted", "meeting_id": str(meeting_id)}


def get_join_url(meeting_id: int | str) -> dict:
    """Get the join URL for a meeting.

    Returns:
        Dict with join_url and start_url.
    """
    result = api_get(f"/meetings/{meeting_id}")
    return {
        "meeting_id": result.get("id"),
        "topic": result.get("topic", ""),
        "join_url": result.get("join_url", ""),
        "start_url": result.get("start_url", ""),
        "password": result.get("password", ""),
    }
