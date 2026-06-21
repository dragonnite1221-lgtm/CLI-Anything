# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def _render_live_html_fs0_1():
    return f"""      border: 1px solid var(--edge);
      border-radius: 999px;
      padding: 10px 14px;
      background: rgba(255,255,255,0.72);
      font-family: var(--mono);
      font-size: 12px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
    }}
    .grid {{
      margin-top: 20px;
      display: grid;
      grid-template-columns: minmax(0, 1.9fr) minmax(320px, 0.9fr);
      gap: 18px;
    }}
    .panel {{
      border: 1px solid var(--edge);
      border-radius: 28px;
      background: var(--panel);
      box-shadow: var(--shadow);
      overflow: hidden;
      min-height: 220px;
    }}
    .panel-header {{
      padding: 16px 18px;
      border-bottom: 1px solid var(--edge);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      background: var(--panel-strong);
    }}
    .panel-header h2 {{
      margin: 0;
      font-size: 0.95rem;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--muted);
    }}
    .panel-body {{
      padding: 18px;
    }}
    .hero-frame {{
      display: block;
      width: 100%;
      border-radius: 20px;
      border: 1px solid var(--edge);
      background: #fff;
      min-height: 280px;
      object-fit: contain;
    }}
    video.hero-frame {{
      background: #0e1013;
    }}
    .stack {{
      display: grid;
      gap: 18px;
    }}
    .gallery {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
    }}
    .thumb {{
      border: 1px solid var(--edge);
      border-radius: 20px;
      padding: 10px;
      background: rgba(255,255,255,0.7);
    }}
    .thumb img {{
      display: block;
      width: 100%;
      border-radius: 14px;
      border: 1px solid var(--edge);
      background: #fff;
    }}
    .thumb .label {{
      margin-top: 10px;
      font-size: 0.9rem;
      font-weight: 600;
    }}
    .thumb .meta {{
      margin-top: 4px;
      color: var(--muted);
      font-size: 0.82rem;
    }}
    .notes {{
      display: grid;
      gap: 10px;
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .notes ul {{
      margin: 0;
      padding-left: 18px;
    }}
    .history {{
      display: grid;
      gap: 10px;
    }}
    .history-item {{
      border: 1px solid var(--edge);
      border-radius: 16px;
      background: rgba(255,255,255,0.72);
      padding: 12px 14px;
    }}
    .history-item strong {{
      display: block;
      font-size: 0.92rem;
    }}
    .history-item span {{
      display: block;
      margin-top: 4px;
      font-size: 0.82rem;
      color: var(--muted);
      word-break: break-word;
    }}
    .history-chip {{
"""
