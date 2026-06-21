# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def _render_live_html_fs0_0(session):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(str(session.get("software", "Preview")))} Live Preview</title>
  <style>
    :root {{
      --paper: #efe8dc;
      --ink: #111215;
      --muted: #64615b;
      --panel: rgba(255,255,255,0.8);
      --panel-strong: rgba(255,255,255,0.92);
      --edge: rgba(17,18,21,0.12);
      --accent: #c24b2f;
      --accent-soft: rgba(194,75,47,0.12);
      --success: #147a4b;
      --shadow: 0 24px 60px rgba(27,22,18,0.14);
      --mono: "SFMono-Regular", "Menlo", "Consolas", monospace;
      --sans: "Avenir Next", "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: var(--sans);
      background:
        radial-gradient(circle at top left, rgba(194,75,47,0.18), transparent 24rem),
        radial-gradient(circle at bottom right, rgba(0,0,0,0.08), transparent 28rem),
        linear-gradient(180deg, #f8f2e8 0%, var(--paper) 100%);
      min-height: 100vh;
    }}
    .shell {{
      max-width: 1480px;
      margin: 0 auto;
      padding: 22px 18px 32px;
    }}
    .masthead {{
      display: grid;
      gap: 14px;
      padding: 20px 22px;
      border: 1px solid var(--edge);
      border-radius: 28px;
      background:
        linear-gradient(135deg, rgba(194,75,47,0.14), transparent 48%),
        linear-gradient(180deg, rgba(255,255,255,0.94), rgba(255,255,255,0.7));
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }}
    .eyebrow {{
      text-transform: uppercase;
      letter-spacing: 0.16em;
      font-size: 12px;
      color: var(--muted);
    }}
    .title-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
      align-items: baseline;
      justify-content: space-between;
    }}
    h1 {{
      margin: 0;
      font-family: "Iowan Old Style", "Georgia", serif;
      font-size: clamp(2rem, 4vw, 3.75rem);
      line-height: 0.94;
      font-weight: 600;
    }}
    .status-chip {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border-radius: 999px;
      padding: 9px 14px;
      background: rgba(20,122,75,0.12);
      color: var(--success);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }}
    .status-chip[data-state="error"] {{
      background: var(--accent-soft);
      color: var(--accent);
    }}
    .subtitle {{
      color: var(--muted);
      font-size: 1rem;
      max-width: 64rem;
    }}
    .fact-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 12px;
    }}
    .fact-card {{
      border: 1px solid var(--edge);
      border-radius: 18px;
      background: rgba(255,255,255,0.74);
      padding: 14px 16px;
    }}
    .fact-card span {{
      display: block;
      margin-bottom: 7px;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.14em;
    }}
    .fact-card strong {{
      display: block;
      font-size: 1rem;
      word-break: break-word;
    }}
    .command-strip {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .command-chip {{
"""
