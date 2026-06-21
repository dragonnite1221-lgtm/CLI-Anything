# ruff: noqa: F403, F405, E501
from .meetings_base import *  # noqa: F403


def _format_meeting(data: dict) -> dict:
    """Format a full meeting response."""
    return {
        "id": data.get("id"),
        "uuid": data.get("uuid", ""),
        "topic": data.get("topic", ""),
        "type": data.get("type"),
        "status": data.get("status", ""),
        "start_time": data.get("start_time", ""),
        "duration": data.get("duration", 0),
        "timezone": data.get("timezone", ""),
        "agenda": data.get("agenda", ""),
        "join_url": data.get("join_url", ""),
        "start_url": data.get("start_url", ""),
        "password": data.get("password", ""),
        "settings": {
            "auto_recording": data.get("settings", {}).get("auto_recording", "none"),
            "waiting_room": data.get("settings", {}).get("waiting_room", False),
            "join_before_host": data.get("settings", {}).get("join_before_host", False),
            "mute_upon_entry": data.get("settings", {}).get("mute_upon_entry", True),
        },
        "created_at": data.get("created_at", ""),
    }


def create_meeting(
    topic: str,
    start_time: str | None = None,
    duration: int = 60,
    timezone: str = "UTC",
    meeting_type: int = 2,
    agenda: str = "",
    password: str | None = None,
    auto_recording: str = "none",
    waiting_room: bool = False,
    join_before_host: bool = False,
    mute_upon_entry: bool = True,
) -> dict:
    """Create a new Zoom meeting.

    Args:
        topic: Meeting subject/title.
        start_time: ISO 8601 datetime (e.g., '2025-01-15T10:00:00Z').
                    None for instant meeting.
        duration: Meeting duration in minutes.
        timezone: Timezone string (e.g., 'Asia/Shanghai', 'America/New_York').
        meeting_type: 1=instant, 2=scheduled, 3=recurring no fixed time,
                      8=recurring fixed time.
        agenda: Meeting description.
        password: Meeting password (auto-generated if None).
        auto_recording: 'none', 'local', or 'cloud'.
        waiting_room: Enable waiting room.
        join_before_host: Allow participants to join before host.
        mute_upon_entry: Mute participants on entry.

    Returns:
        Meeting details dict from Zoom API.
    """
    body: dict[str, Any] = {
        "topic": topic,
        "type": meeting_type,
        "duration": duration,
        "timezone": timezone,
        "settings": {
            "auto_recording": auto_recording,
            "waiting_room": waiting_room,
            "join_before_host": join_before_host,
            "mute_upon_entry": mute_upon_entry,
        },
    }

    if start_time:
        body["start_time"] = start_time

    if agenda:
        body["agenda"] = agenda

    if password:
        body["password"] = password

    result = api_post("/users/me/meetings", body)

    return _format_meeting(result)


def _format_meeting_summary(data: dict) -> dict:
    """Format a meeting list item."""
    return {
        "id": data.get("id"),
        "topic": data.get("topic", ""),
        "type": data.get("type"),
        "start_time": data.get("start_time", ""),
        "duration": data.get("duration", 0),
        "timezone": data.get("timezone", ""),
        "join_url": data.get("join_url", ""),
        "created_at": data.get("created_at", ""),
    }


def list_meetings(
    status: str = "upcoming",
    page_size: int = 30,
    page_number: int = 1,
) -> dict:
    """List meetings for the authenticated user.

    Args:
        status: 'upcoming', 'scheduled', 'live', or 'pending'.
        page_size: Number of results per page (max 300).
        page_number: Page number to return.

    Returns:
        Dict with meetings list and pagination info.
    """
    params = {
        "type": status,
        "page_size": min(page_size, 300),
        "page_number": page_number,
    }

    result = api_get("/users/me/meetings", params=params)

    meetings = [_format_meeting_summary(m) for m in result.get("meetings", [])]

    return {
        "total_records": result.get("total_records", 0),
        "page_count": result.get("page_count", 0),
        "page_number": result.get("page_number", 1),
        "page_size": result.get("page_size", page_size),
        "meetings": meetings,
    }
