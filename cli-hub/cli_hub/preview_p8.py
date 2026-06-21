# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def _render_html_fs0_0(manifest):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(manifest.get("software", "Preview"))} Preview Bundle</title>
  <style>
    :root {{
      --paper: #f6f1e8;
      --ink: #171717;
      --muted: #5b554c;
      --panel: rgba(255,255,255,0.68);
      --edge: rgba(23,23,23,0.14);
      --accent: #b23a2b;
      --accent-soft: rgba(178,58,43,0.1);
      --shadow: 0 20px 60px rgba(25,20,14,0.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Georgia", "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(178,58,43,0.12), transparent 28rem),
        radial-gradient(circle at bottom right, rgba(23,23,23,0.08), transparent 30rem),
        linear-gradient(180deg, #fbf7ef 0%, var(--paper) 100%);
      min-height: 100vh;
    }}
    .shell {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 32px 18px 60px;
    }}
    .hero {{
      border: 1px solid var(--edge);
      background: var(--panel);
      backdrop-filter: blur(10px);
      box-shadow: var(--shadow);
      border-radius: 28px;
      overflow: hidden;
    }}
    .hero-top {{
      padding: 28px 28px 18px;
      border-bottom: 1px solid var(--edge);
      display: grid;
      gap: 16px;
      background:
        linear-gradient(135deg, rgba(178,58,43,0.12), transparent 45%),
        linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,255,255,0.58));
    }}
    .kicker {{
      text-transform: uppercase;
      letter-spacing: 0.16em;
      font-size: 12px;
      color: var(--muted);
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2rem, 4vw, 4rem);
      line-height: 0.92;
      font-weight: 600;
    }}
    .subtitle {{
      color: var(--muted);
      font-size: 1rem;
      max-width: 60rem;
    }}
    .facts {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 12px;
    }}
    .fact-card {{
      border: 1px solid var(--edge);
      border-radius: 18px;
      background: rgba(255,255,255,0.72);
      padding: 14px 16px;
    }}
    .fact-card span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      margin-bottom: 8px;
    }}
    .fact-card strong {{
      font-size: 1.02rem;
    }}
    .warning-box {{
      margin-top: 16px;
      border: 1px solid rgba(178,58,43,0.28);
      background: var(--accent-soft);
      border-radius: 18px;
      padding: 14px 18px;
    }}
    .warning-box ul {{
      margin: 10px 0 0;
      padding-left: 18px;
    }}
    .meta-grid {{
      padding: 24px 28px 28px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
    }}
    .meta-item {{
      border-left: 2px solid var(--accent);
      padding-left: 12px;
      color: var(--muted);
    }}
    .meta-item strong {{
      color: var(--ink);
      display: block;
      margin-top: 4px;
    }}
    .section {{
      margin-top: 28px;
    }}
    .section h2 {{
      margin: 0 0 14px;
"""
