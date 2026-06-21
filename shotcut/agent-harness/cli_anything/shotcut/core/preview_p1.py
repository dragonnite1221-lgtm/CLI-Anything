# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def list_recipes() -> List[Dict[str, Any]]:
    """Return available preview recipes."""
    recipes = []
    for name, config in RECIPES.items():
        recipes.append(
            {
                "name": name,
                "description": config["description"],
                "bundle_kind": "capture",
                "artifacts": ["preview-clip", "hero", "gallery"],
                "resolution": f"{config['width']}x{config['height']}",
            }
        )
    return recipes


def _seconds_to_timecode(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    hours, rem = divmod(total_ms, 3600 * 1000)
    minutes, rem = divmod(rem, 60 * 1000)
    whole_seconds, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{ms:03d}"


def _project_fingerprint(session: Session) -> str:
    if not session.is_open:
        raise RuntimeError("No project is open")
    if (
        session.project_path
        and not session.is_modified
        and os.path.isfile(session.project_path)
    ):
        return fingerprint_data(
            {
                "project_path": os.path.abspath(session.project_path),
                "project_file": fingerprint_file(session.project_path),
            }
        )
    payload: Dict[str, Any] = {
        "project_path": os.path.abspath(session.project_path)
        if session.project_path
        else "",
        "xml": mlt_xml.mlt_to_string(session.root),
    }
    if not session.project_path:
        payload["session_id"] = session.session_id
    return fingerprint_data(payload)


def _metrics(session: Session) -> Dict[str, Any]:
    tractor = session.get_main_tractor()
    producers = mlt_xml.get_all_producers(session.root)
    filters = mlt_xml.get_all_filters(session.root)
    renderable_producers = [
        producer
        for producer in producers
        if mlt_xml.get_property(producer, "resource", "") not in ("", "0")
        and mlt_xml.get_property(producer, "mlt_service", "") not in ("color", "colour")
    ]
    return {
        "track_count": len(mlt_xml.get_tractor_tracks(tractor)),
        "producer_count": len(renderable_producers),
        "filter_count": len(filters),
        "profile": session.get_profile(),
    }
