# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def _render_html_fs0_1(artifact_cards, fact_cards, headline, manifest, trajectory_html, warning_html):
    return f"""      font-size: 1.1rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--muted);
    }}
    .artifact-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 18px;
    }}
    .artifact-card {{
      position: relative;
      border: 1px solid var(--edge);
      border-radius: 24px;
      background: rgba(255,255,255,0.78);
      padding: 16px;
      box-shadow: 0 16px 40px rgba(33,28,22,0.08);
      overflow: hidden;
    }}
    .artifact-role {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      padding: 6px 10px;
      font-size: 11px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      margin-bottom: 10px;
    }}
    .artifact-card h3 {{
      margin: 0 0 8px;
      font-size: 1.08rem;
    }}
    .artifact-meta {{
      color: var(--muted);
      font-size: 0.9rem;
      margin-bottom: 14px;
    }}
    .artifact-card img,
    .artifact-card video {{
      display: block;
      width: 100%;
      border-radius: 16px;
      border: 1px solid var(--edge);
      background: #ffffff;
    }}
    .artifact-file {{
      border: 1px dashed var(--edge);
      border-radius: 16px;
      padding: 14px;
      background: rgba(255,255,255,0.58);
      word-break: break-word;
    }}
    .artifact-file a {{
      color: var(--accent);
      text-decoration: none;
    }}
    .trajectory-list {{
      display: grid;
      gap: 12px;
      margin-top: 16px;
    }}
    .trajectory-item {{
      border: 1px solid var(--edge);
      border-radius: 18px;
      padding: 14px 16px;
      background: rgba(255,255,255,0.72);
    }}
    .trajectory-item strong {{
      display: block;
      font-size: 0.98rem;
    }}
    .trajectory-command {{
      margin-top: 10px;
      padding: 10px 12px;
      border-radius: 14px;
      background: rgba(23,23,23,0.05);
      overflow-x: auto;
    }}
    .trajectory-command code {{
      font-family: "SFMono-Regular", "Menlo", "Consolas", monospace;
      font-size: 12px;
      color: var(--ink);
    }}
    .trajectory-meta {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 0.88rem;
      word-break: break-word;
    }}
    @media (max-width: 720px) {{
      .shell {{ padding: 18px 12px 36px; }}
      .hero-top, .meta-grid {{ padding: 20px 18px; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="hero-top">
        <div class="kicker">CLI-Anything Preview Bundle</div>
        <h1>{headline}</h1>
        <div class="subtitle">Software: {html.escape(str(manifest.get("software", "unknown")))} · Recipe: {html.escape(str(manifest.get("recipe", "unknown")))} · Kind: {html.escape(str(manifest.get("bundle_kind", "capture")))}</div>
        <div class="facts">{fact_cards or '<div class="fact-card"><span>Artifacts</span><strong>' + str(len(manifest.get("artifacts", []))) + '</strong></div>'}</div>
        {"<div class='warning-box'><strong>Warnings</strong><ul>" + warning_html + "</ul></div>" if warning_html else ""}
      </div>
      <div class="meta-grid">
        <div class="meta-item">Bundle ID<strong>{html.escape(str(manifest.get("bundle_id", "unknown")))}</strong></div>
        <div class="meta-item">Status<strong>{html.escape(str(manifest.get("status", "unknown")))}</strong></div>
        <div class="meta-item">Created<strong>{html.escape(str(manifest.get("created_at", "unknown")))}</strong></div>
        <div class="meta-item">Source<strong>{html.escape(str(manifest.get("source", {}).get("project_path") or manifest.get("source", {}).get("capture_path") or "n/a"))}</strong></div>
      </div>
    </section>
    {trajectory_html}
    <section class="section">
      <h2>Artifacts</h2>
      <div class="artifact-grid">{artifact_cards}</div>
"""
def _render_html_fs0_2():
    return f"""    </section>
  </main>
</body>
</html>
"""
