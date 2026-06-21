# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403
# fmt: off
from .preview_p2 import _trajectory_candidate_refs  # noqa: E402,E501
from .preview_p5 import inspect_session  # noqa: E402,E501
from .preview_p11 import _render_live_html_fs0_0  # noqa: E402,E501
from .preview_p12 import _render_live_html_fs0_1  # noqa: E402,E501
from .preview_p13 import _render_live_html_fs0_2  # noqa: E402,E501
from .preview_p14 import _render_live_html_fs0_3  # noqa: E402,E501
from .preview_p15 import _render_live_html_fs0_4  # noqa: E402,E501
from .preview_p16 import _render_live_html_fs0_5  # noqa: E402,E501
# fmt: on


def _render_live_html_fs0_6():
    return f"""        lines.push(`<div><strong>Suggested checks</strong><ul>${{actions.map((item) => `<li>${{escapeHtml(item)}}</li>`).join("")}}</ul></div>`);
      }}
      notes.innerHTML = lines.join("");
    }}

    function renderHistory(session, trajectory) {{
      const root = document.getElementById("history");
      const title = document.getElementById("history-title");
      const meta = document.getElementById("history-meta");
      const entries = Array.isArray(trajectory.entries) ? [...trajectory.entries].reverse() : [];
      if (!entries.length) {{
        title.textContent = "History / Timeline";
        meta.textContent = "No trajectory or publish history yet";
        root.innerHTML = '<div class="empty">No live preview publishes yet.</div>';
        return;
      }}
      title.textContent = trajectory.mode === "trajectory" ? "Trajectory Timeline" : "Recent Bundles";
      meta.textContent = `${{trajectory.stepCount || entries.length}} steps · ${{trajectory.publishedBundleCount || 0}} published bundles · ${{trajectory.sourceLabel || trajectory.mode}}`;
      root.innerHTML = entries.slice(0, 10).map((entry) => {{
        const titleText = entry.stepLabel || entry.stepId || entry.bundleId || "step";
        const chips = [];
        if (entry.stepId && entry.stepId === trajectory.currentStepId) chips.push("current-step");
        if (entry.bundleId && entry.bundleId === session.current_bundle_id) chips.push("current-bundle");
        if (entry.status) chips.push(entry.status);
        if (entry.cached === true) chips.push("cached");
        const detailLines = [
          entry.commandFinishedAt || entry.createdAt,
          entry.publishReason ? `publish=${{entry.publishReason}}` : null,
          entry.bundleId ? `bundle=${{entry.bundleId}}` : null,
          entry.sourceFingerprint ? `fp=${{entry.sourceFingerprint}}` : null,
          entry.bundleDir || entry.manifestPath || null,
        ].filter(Boolean);
        return `
          <article class="history-item">
            <strong>${{escapeHtml(titleText)}}</strong>
            ${{chips.map((chip) => `<div class="history-chip">${{escapeHtml(chip)}}</div>`).join("")}}
            ${{entry.command ? `<div class="history-command">${{escapeHtml(entry.command)}}</div>` : ""}}
            ${{detailLines.map((line) => `<span>${{escapeHtml(line)}}</span>`).join("")}}
          </article>
        `;
      }}).join("");
    }}

    async function refresh() {{
      try {{
        const session = await fetchJson("session.json");
        const manifest = await fetchJson(`${{CURRENT_LINK}}/manifest.json`);
        const trajectoryPayload = await fetchTrajectory(session);
        const trajectory = normalizeTrajectory(session, trajectoryPayload);
        let summary = {{}};
        const summaryPath = manifest.summary_path ? `${{CURRENT_LINK}}/${{manifest.summary_path}}` : `${{CURRENT_LINK}}/summary.json`;
        try {{
          summary = await fetchJson(summaryPath);
        }} catch (error) {{
          summary = {{}};
        }}

        document.getElementById("subtitle").textContent =
          (summary.headline || "Latest bundle loaded") +
          ` · ${{trajectory.stepCount || session.trajectory_step_count || 0}} tracked steps` +
          ` · polling every ${{POLL_MS}} ms`;

        renderFacts(session, manifest, summary, trajectory);
        renderCommands(session);
        renderHero(session, manifest);
        renderClip(session, manifest);
        renderGallery(session, manifest);
        renderNotes(session, manifest, summary, trajectory);
        renderHistory(session, trajectory);
        setStatus("Watching", false);
      }} catch (error) {{
        setStatus("Waiting", true);
        document.getElementById("notes").innerHTML = `<div><strong>Viewer state</strong><br>${{escapeHtml(error.message)}}</div>`;
      }}
    }}

    refresh();
    window.setInterval(refresh, POLL_MS);
  </script>
</body>
</html>
"""
def render_live_html(session_ref: str, output_path: str, poll_ms: int = 1500) -> str:
    payload = inspect_session(session_ref)
    session_dir = Path(payload["session_dir"])
    session = payload["session"]
    trajectory = payload.get("trajectory")
    output_file = Path(output_path).expanduser().resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    headline = html.escape(
        session.get("project_name")
        or session.get("project_path")
        or f"{session.get('software', 'Preview')} live preview"
    )
    poll_ms = max(250, int(poll_ms))
    trajectory_candidate_refs = _trajectory_candidate_refs(session_dir, session)
    html_text = _render_live_html_fs0_0(session) + _render_live_html_fs0_1() + _render_live_html_fs0_2(headline, poll_ms, session, trajectory_candidate_refs) + _render_live_html_fs0_3() + _render_live_html_fs0_4() + _render_live_html_fs0_5() + _render_live_html_fs0_6()
    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(html_text)
    return str(output_file)
class _NoCacheHandler(SimpleHTTPRequestHandler):
    """Serve preview assets without cache so live sessions refresh correctly."""

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        return
def start_static_server(directory: str, host: str = "127.0.0.1", port: int = 0) -> Tuple[ThreadingHTTPServer, str]:
    root = Path(directory).expanduser().resolve()
    handler = functools.partial(_NoCacheHandler, directory=str(root))
    server = ThreadingHTTPServer((host, int(port)), handler)
    base_url = f"http://{host}:{server.server_port}"
    return server, base_url
