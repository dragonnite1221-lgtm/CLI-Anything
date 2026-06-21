# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403
# fmt: off
from .preview_p1 import format_bytes  # noqa: E402,E501
from .preview_p5 import _render_trajectory_text_lines, inspect_bundle, inspect_session  # noqa: E402,E501
# fmt: on


def render_inspect_text(bundle_ref: str) -> str:
    payload = inspect_bundle(bundle_ref)
    bundle_dir = Path(payload["bundle_dir"])
    manifest = payload["manifest"]
    summary = payload["summary"]
    lines = [
        f"Bundle:      {bundle_dir}",
        f"Protocol:    {manifest.get('protocol_version', 'unknown')}",
        f"Software:    {manifest.get('software', 'unknown')}",
        f"Recipe:      {manifest.get('recipe', 'unknown')}",
        f"Kind:        {manifest.get('bundle_kind', 'unknown')}",
        f"Status:      {manifest.get('status', 'unknown')}",
        f"Created:     {manifest.get('created_at', 'unknown')}",
    ]
    source = manifest.get("source", {})
    if source:
        lines.append(
            "Source:      "
            + (
                source.get("project_path")
                or source.get("capture_path")
                or source.get("project_name")
                or "n/a"
            )
        )
        if source.get("project_fingerprint"):
            lines.append(f"Fingerprint: {source['project_fingerprint']}")
        elif source.get("capture_fingerprint"):
            lines.append(f"Fingerprint: {source['capture_fingerprint']}")
    if summary:
        lines.append("")
        lines.append("Summary")
        lines.append(f"  Headline: {summary.get('headline', '(none)')}")
        facts = summary.get("facts", {})
        for key, value in facts.items():
            lines.append(f"  {key}: {value}")
        for warning in summary.get("warnings", []):
            lines.append(f"  Warning: {warning}")
    lines.append("")
    lines.append("Artifacts")
    for artifact in manifest.get("artifacts", []):
        desc = (
            f"  - {artifact.get('artifact_id', '?')} "
            f"[{artifact.get('role', '?')}] {artifact.get('label', '')}"
        )
        desc += f" -> {artifact.get('path', '')}"
        if artifact.get("bytes") is not None:
            desc += f" ({format_bytes(int(artifact['bytes']))})"
        lines.append(desc)
    lines.extend(_render_trajectory_text_lines("Trajectory", payload.get("trajectory")))
    return "\n".join(lines) + "\n"
def render_session_text(session_ref: str) -> str:
    payload = inspect_session(session_ref)
    session_dir = Path(payload["session_dir"])
    session = payload["session"]
    trajectory = payload.get("trajectory")
    lines = [
        f"Live Session: {session_dir}",
        f"Protocol:     {session.get('protocol_version', 'unknown')}",
        f"Software:     {session.get('software', 'unknown')}",
        f"Recipe:       {session.get('recipe', 'unknown')}",
        f"Status:       {session.get('status', 'unknown')}",
        f"Updated:      {session.get('updated_at', 'unknown')}",
        f"Current:      {session.get('current_bundle_id', 'n/a')}",
        f"Project:      {session.get('project_path') or session.get('project_name') or 'n/a'}",
    ]
    if session.get("watch_command"):
        lines.append(f"Watch:        {session['watch_command']}")
    history_title = "History" if trajectory and trajectory.get("mode") == "legacy-history" else "Trajectory"
    lines.extend(_render_trajectory_text_lines(history_title, trajectory))
    if trajectory is None:
        history = session.get("history", [])
        if history:
            lines.append("")
            lines.append("History")
            for item in history:
                lines.append(
                    f"  - {item.get('bundle_id', '?')} "
                    f"[{item.get('status', 'unknown')}] {item.get('created_at', 'unknown')}"
                )
    return "\n".join(lines) + "\n"
def _artifact_href(output_dir: Path, bundle_dir: Path, artifact_path: str) -> str:
    target = (bundle_dir / artifact_path).resolve()
    return os.path.relpath(target, output_dir)
def _render_artifact_card(output_dir: Path, bundle_dir: Path, artifact: Dict[str, Any]) -> str:
    role = html.escape(artifact.get("role", "artifact"))
    label = html.escape(artifact.get("label", artifact.get("artifact_id", "artifact")))
    path_ref = _artifact_href(output_dir, bundle_dir, artifact.get("path", ""))
    media_type = artifact.get("media_type", "")
    size = artifact.get("bytes")
    meta = []
    if artifact.get("width") and artifact.get("height"):
        meta.append(f"{artifact['width']}×{artifact['height']}")
    if artifact.get("duration_s") is not None:
        meta.append(f"{artifact['duration_s']}s")
    if size is not None:
        meta.append(format_bytes(int(size)))
    meta_line = " · ".join(meta)

    if media_type.startswith("image/"):
        body = f'<img src="{html.escape(path_ref)}" alt="{label}" loading="lazy">'
    elif media_type.startswith("video/"):
        body = (
            f'<video controls preload="metadata" src="{html.escape(path_ref)}">'
            "Your browser does not support embedded video."
            "</video>"
        )
    else:
        body = (
            '<div class="artifact-file">'
            f'<a href="{html.escape(path_ref)}">{html.escape(artifact.get("path", ""))}</a>'
            "</div>"
        )

    badge = f'<span class="artifact-role">{role}</span>'
    details = f'<div class="artifact-meta">{html.escape(meta_line)}</div>' if meta_line else ""
    return (
        '<article class="artifact-card">'
        f"{badge}"
        f'<h3>{label}</h3>'
        f"{details}"
        f"{body}"
        "</article>"
    )
