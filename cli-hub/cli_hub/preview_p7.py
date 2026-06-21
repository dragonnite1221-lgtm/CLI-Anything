# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def _render_trajectory_html_section(trajectory: Optional[Dict[str, Any]]) -> str:
    if not trajectory:
        return ""

    summary_cards = [
        ("Source", trajectory.get("source_label") or trajectory.get("mode") or "unknown"),
        ("Steps", trajectory.get("step_count", 0)),
        ("Published", trajectory.get("published_bundle_count", 0)),
    ]
    if trajectory.get("recent_publish_reason"):
        summary_cards.append(("Recent publish", trajectory["recent_publish_reason"]))
    elif trajectory.get("recent_bundle_id"):
        summary_cards.append(("Recent bundle", trajectory["recent_bundle_id"]))

    cards_html = "".join(
        f'<div class="fact-card"><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>'
        for label, value in summary_cards
    )

    items = trajectory.get("entries", [])[-6:]
    items_html = "".join(
        (
            '<article class="trajectory-item">'
            f'<strong>{html.escape(str(item.get("step_label") or item.get("stage_label") or item.get("step_id") or "step"))}</strong>'
            + (
                f'<div class="trajectory-command"><code>{html.escape(str(item["command"]))}</code></div>'
                if item.get("command")
                else ""
            )
            + (
                f'<div class="trajectory-meta">Publish reason: {html.escape(str(item["publish_reason"]))}</div>'
                if item.get("publish_reason")
                else ""
            )
            + (
                f'<div class="trajectory-meta">Bundle: {html.escape(str(item["bundle_id"]))}</div>'
                if item.get("bundle_id")
                else ""
            )
            + "</article>"
        )
        for item in items
    )
    empty_timeline = '<div class="artifact-file">No step timeline entries yet.</div>'

    return (
        '<section class="section">'
        "<h2>Trajectory</h2>"
        f'<div class="facts">{cards_html}</div>'
        f'<div class="trajectory-list">{items_html or empty_timeline}</div>'
        "</section>"
    )
