# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p1 import COLORS, VIDEO_W  # noqa: E402,E501
from .freecad_live_preview_demo_p36 import _draw_chip, _readable_command_text, _rgba  # noqa: E402,E501
from .freecad_live_preview_demo_p37 import progress_snapshot  # noqa: E402,E501
# fmt: on


def build_command_cards(trajectory: Dict[str, Any], t_real: float, *, max_cards: int = 6) -> List[Dict[str, Any]]:
    commands = trajectory.get("commands", [])
    if not commands:
        return []

    active_idx: Optional[int] = None
    completed = 0
    for idx, cmd in enumerate(commands):
        if t_real >= cmd["timeline_end_s"]:
            completed += 1
        elif cmd["timeline_start_s"] <= t_real < cmd["timeline_end_s"]:
            active_idx = idx
            break

    if active_idx is None:
        focus_idx = min(len(commands) - 1, completed)
    else:
        focus_idx = active_idx

    start = max(0, focus_idx - 2)
    start = min(start, max(0, len(commands) - max_cards))
    selected = commands[start:start + max_cards]

    cards: List[Dict[str, Any]] = []
    for idx, cmd in enumerate(selected, start=start):
        if t_real >= cmd["timeline_end_s"]:
            status = "done"
        elif cmd["timeline_start_s"] <= t_real < cmd["timeline_end_s"]:
            status = "live"
        else:
            status = "queued"

        cards.append(
            {
                "index": idx,
                "status": status,
                "label": cmd.get("label") or cmd.get("id") or f"Step {idx + 1}",
                "command": _readable_command_text(cmd.get("display_cmd", "")),
                "duration_s": float(cmd.get("duration_s") or 0.0),
            }
        )
    return cards
def draw_global_header(
    canvas: Image.Image,
    trajectory: Dict[str, Any],
    t_real: float,
    fonts: Dict[str, ImageFont.FreeTypeFont],
) -> None:
    draw = ImageDraw.Draw(canvas)
    snapshot = progress_snapshot(trajectory, t_real)
    title = trajectory.get("scenario_title", "FreeCAD Live Demo").upper()
    subtitle = trajectory.get("scenario_subtitle", "real CLI trajectory + real preview bundles")

    draw.text((34, 20), "CLI-ANYTHING / FREECAD / LIVE PREVIEW PROTOCOL", fill="#88a9c8", font=fonts["small"])
    draw.text((34, 36), title, fill=COLORS["white"], font=fonts["display"])
    draw.text((34, 68), subtitle, fill="#97abc2", font=fonts["body"])

    chip_y = 20
    chips = [
        f"T+ {t_real:05.1f}s",
        f"{snapshot['completed_cmds']:02d}/{snapshot['total_cmds']:02d} cmds",
        f"{snapshot['completed_previews']:02d}/{snapshot['total_previews']:02d} bundles",
    ]
    x = VIDEO_W - 34
    for text in reversed(chips):
        bbox = draw.textbbox((0, 0), text, font=fonts["mono_small"])
        chip_w = (bbox[2] - bbox[0]) + 26
        _draw_chip(
            canvas,
            (x - chip_w, chip_y, x, chip_y + 26),
            text=text,
            font=fonts["mono_small"],
            fill=COLORS["chip_bg"],
            text_fill=COLORS["chip_text"],
            outline=COLORS["panel_line"],
        )
        x -= chip_w + 10

    draw.line((30, 98, VIDEO_W - 30, 98), fill=_rgba(COLORS["grid"], 120), width=1)
