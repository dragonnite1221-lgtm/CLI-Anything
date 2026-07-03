"""Recording management — list, download, and delete cloud recordings.

Handles:
- List recordings for a date range
- Get recording files for a specific meeting
- Download recording files
- Delete recordings
"""

from cli_anything.zoom.utils.zoom_backend import api_get
# Re-exported for backward compatibility (moved to recordings_io.py).
from cli_anything.zoom.core.recordings_io import (  # noqa: F401
    download_recording,
    delete_recording,
    delete_recording_file,
)


def list_recordings(
    from_date: str = "",
    to_date: str = "",
    page_size: int = 30,
) -> dict:
    """List cloud recordings for the authenticated user.

    Args:
        from_date: Start date (YYYY-MM-DD). Defaults to 30 days ago.
        to_date: End date (YYYY-MM-DD). Defaults to today.
        page_size: Results per page (max 300).

    Returns:
        Dict with recording list.
    """
    params = {"page_size": min(page_size, 300)}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    result = api_get("/users/me/recordings", params=params)

    meetings = []
    for m in result.get("meetings", []):
        files = []
        for f in m.get("recording_files", []):
            files.append({
                "id": f.get("id", ""),
                "file_type": f.get("file_type", ""),
                "file_extension": f.get("file_extension", ""),
                "file_size": f.get("file_size", 0),
                "status": f.get("status", ""),
                "recording_start": f.get("recording_start", ""),
                "recording_end": f.get("recording_end", ""),
                "download_url": f.get("download_url", ""),
            })
        meetings.append({
            "meeting_id": m.get("id"),
            "uuid": m.get("uuid", ""),
            "topic": m.get("topic", ""),
            "start_time": m.get("start_time", ""),
            "duration": m.get("duration", 0),
            "total_size": m.get("total_size", 0),
            "recording_count": m.get("recording_count", 0),
            "recording_files": files,
        })

    return {
        "total_records": result.get("total_records", 0),
        "meetings": meetings,
    }


def get_meeting_recordings(meeting_id: int | str) -> dict:
    """Get recording files for a specific meeting.

    Args:
        meeting_id: Zoom meeting ID or UUID.

    Returns:
        Dict with recording files.
    """
    # Double-encode UUID if needed
    mid = str(meeting_id)
    if mid.startswith("/"):
        from urllib.parse import quote
        mid = quote(quote(mid, safe=""), safe="")

    result = api_get(f"/meetings/{mid}/recordings")

    files = []
    for f in result.get("recording_files", []):
        files.append({
            "id": f.get("id", ""),
            "file_type": f.get("file_type", ""),
            "file_extension": f.get("file_extension", ""),
            "file_size": f.get("file_size", 0),
            "status": f.get("status", ""),
            "download_url": f.get("download_url", ""),
            "play_url": f.get("play_url", ""),
            "recording_start": f.get("recording_start", ""),
            "recording_end": f.get("recording_end", ""),
        })

    return {
        "meeting_id": result.get("id"),
        "uuid": result.get("uuid", ""),
        "topic": result.get("topic", ""),
        "start_time": result.get("start_time", ""),
        "duration": result.get("duration", 0),
        "total_size": result.get("total_size", 0),
        "recording_files": files,
    }
