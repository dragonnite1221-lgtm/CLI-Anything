# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403
# fmt: off
from .preview_p5 import inspect_bundle  # noqa: E402,E501
from .preview_p6 import _render_artifact_card  # noqa: E402,E501
from .preview_p7 import _render_trajectory_html_section  # noqa: E402,E501
from .preview_p8 import _render_html_fs0_0  # noqa: E402,E501
from .preview_p9 import _render_html_fs0_1, _render_html_fs0_2  # noqa: E402,E501
# fmt: on


def render_html(bundle_ref: str, output_path: str) -> str:
    payload = inspect_bundle(bundle_ref)
    bundle_dir = Path(payload["bundle_dir"])
    manifest = payload["manifest"]
    summary = payload["summary"]
    trajectory = payload.get("trajectory")
    output_file = Path(output_path).expanduser().resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    headline = html.escape(
        summary.get("headline", f"{manifest.get('software', 'Preview')} preview bundle")
    )
    warnings = summary.get("warnings", [])
    facts = summary.get("facts", {})
    fact_cards = "".join(
        f'<div class="fact-card"><span>{html.escape(str(key))}</span><strong>{html.escape(str(value))}</strong></div>'
        for key, value in facts.items()
    )
    warning_html = "".join(f"<li>{html.escape(str(item))}</li>" for item in warnings)
    artifact_cards = "".join(
        _render_artifact_card(output_file.parent, bundle_dir, artifact)
        for artifact in manifest.get("artifacts", [])
    )
    trajectory_html = _render_trajectory_html_section(trajectory)

    html_text = _render_html_fs0_0(manifest) + _render_html_fs0_1(artifact_cards, fact_cards, headline, manifest, trajectory_html, warning_html) + _render_html_fs0_2()
    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(html_text)
    return str(output_file)
