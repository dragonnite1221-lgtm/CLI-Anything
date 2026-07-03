"""Recording download and deletion (split from recordings.py)."""

from pathlib import Path

from cli_anything.zoom.utils.zoom_backend import api_delete, api_request


def download_recording(
    download_url: str,
    output_path: str,
    overwrite: bool = False,
) -> dict:
    """Download a recording file.

    Args:
        download_url: The download URL from the recording file info.
        output_path: Local path to save the file.
        overwrite: Whether to overwrite existing files.

    Returns:
        Dict with download result.
    """
    out = Path(output_path)
    if out.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {output_path}")

    out.parent.mkdir(parents=True, exist_ok=True)

    # Download with streaming
    resp = api_request("GET", "", stream=True)
    # For recording downloads, we need to use the direct URL with token
    import requests
    from cli_anything.zoom.utils.zoom_backend import _get_valid_token

    token = _get_valid_token()
    resp = requests.get(
        download_url,
        headers={"Authorization": f"Bearer {token}"},
        stream=True,
        timeout=300,
    )
    resp.raise_for_status()

    total_size = int(resp.headers.get("content-length", 0))
    downloaded = 0

    with open(out, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)

    actual_size = out.stat().st_size

    return {
        "status": "downloaded",
        "path": str(out.resolve()),
        "size_bytes": actual_size,
        "size_mb": round(actual_size / (1024 * 1024), 2),
    }


def delete_recording(meeting_id: int | str) -> dict:
    """Delete all recordings for a meeting.

    Args:
        meeting_id: Zoom meeting ID or UUID.

    Returns:
        Confirmation dict.
    """
    mid = str(meeting_id)
    if mid.startswith("/"):
        from urllib.parse import quote
        mid = quote(quote(mid, safe=""), safe="")

    api_delete(f"/meetings/{mid}/recordings")
    return {"status": "deleted", "meeting_id": str(meeting_id)}


def delete_recording_file(
    meeting_id: int | str,
    recording_id: str,
) -> dict:
    """Delete a specific recording file.

    Args:
        meeting_id: Zoom meeting ID or UUID.
        recording_id: The recording file ID.

    Returns:
        Confirmation dict.
    """
    mid = str(meeting_id)
    if mid.startswith("/"):
        from urllib.parse import quote
        mid = quote(quote(mid, safe=""), safe="")

    api_delete(f"/meetings/{mid}/recordings/{recording_id}")
    return {
        "status": "deleted",
        "meeting_id": str(meeting_id),
        "recording_id": recording_id,
    }
