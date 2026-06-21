# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403
# fmt: off
from .preview_p1 import _script_json  # noqa: E402,E501
# fmt: on


def _render_live_html_fs0_2(headline, poll_ms, session, trajectory_candidate_refs):
    return f"""      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 999px;
      background: rgba(17,18,21,0.06);
      color: var(--muted);
      padding: 4px 9px;
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-top: 8px;
      width: fit-content;
    }}
    .history-command {{
      margin-top: 8px;
      padding: 10px 12px;
      border-radius: 12px;
      background: rgba(17,18,21,0.05);
      font-family: var(--mono);
      font-size: 12px;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .empty {{
      padding: 28px;
      border: 1px dashed var(--edge);
      border-radius: 18px;
      background: rgba(255,255,255,0.46);
      color: var(--muted);
      text-align: center;
    }}
    @media (max-width: 1100px) {{
      .grid {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 700px) {{
      .shell {{ padding: 14px 10px 20px; }}
      .masthead, .panel-body, .panel-header {{ padding-left: 14px; padding-right: 14px; }}
      .command-chip {{ white-space: normal; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="masthead">
      <div class="eyebrow">CLI-Anything Live Preview Session</div>
      <div class="title-row">
        <h1>{headline}</h1>
        <div id="status-chip" class="status-chip">Watching</div>
      </div>
      <div id="subtitle" class="subtitle">Polling the latest preview bundle every {poll_ms} ms.</div>
      <div id="fact-row" class="fact-row"></div>
      <div id="command-strip" class="command-strip"></div>
    </section>
    <section class="grid">
      <div class="stack">
        <article class="panel">
          <div class="panel-header">
            <h2>Hero Frame</h2>
            <span id="hero-meta" class="subtitle">Waiting for the first bundle</span>
          </div>
          <div class="panel-body" id="hero-slot">
            <div class="empty">Run <code>{html.escape(session.get("publish_command", "shotcut preview live push"))}</code> to publish or refresh the session.</div>
          </div>
        </article>
        <article class="panel">
          <div class="panel-header">
            <h2>Gallery</h2>
            <span id="gallery-meta" class="subtitle">Sampled stills for fast visual checks</span>
          </div>
          <div class="panel-body">
            <div id="gallery" class="gallery"></div>
          </div>
        </article>
      </div>
      <div class="stack">
        <article class="panel">
          <div class="panel-header">
            <h2>Review Clip</h2>
            <span id="clip-meta" class="subtitle">Low-res preview render</span>
          </div>
          <div class="panel-body" id="clip-slot">
            <div class="empty">No preview clip has been published yet.</div>
          </div>
        </article>
        <article class="panel">
          <div class="panel-header">
            <h2>Session Notes</h2>
            <span class="subtitle">Agent-native summary + refresh state</span>
          </div>
          <div class="panel-body">
            <div id="notes" class="notes"></div>
          </div>
        </article>
        <article class="panel">
          <div class="panel-header">
            <h2 id="history-title">History / Timeline</h2>
            <span id="history-meta" class="subtitle">Trajectory-aware command to bundle view</span>
          </div>
          <div class="panel-body">
            <div id="history" class="history"></div>
          </div>
        </article>
      </div>
    </section>
  </main>
  <script>
    const POLL_MS = {poll_ms};
    const CURRENT_LINK = {_script_json(session.get("current_link", "current"))};
    const TRAJECTORY_CANDIDATES = {_script_json(trajectory_candidate_refs)};

    function escapeHtml(value) {{
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }}

    function firstDefined(...values) {{
      for (const value of values) {{
"""
