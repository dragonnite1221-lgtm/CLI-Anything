# ruff: noqa: F403, F405, E501
from .blender_preview_story_demo_base import *  # noqa: F403
# fmt: off
from .blender_preview_story_demo_p1 import COLORS, STYLE  # noqa: E402,E501
from .blender_preview_story_demo_p3 import build_command_cards, progress_snapshot  # noqa: E402,E501
# fmt: on


def draw_trace_panel(
    canvas: Image.Image,
    area: tuple[int, int, int, int],
    trajectory: Dict[str, Any],
    t_real: float,
    fonts: Dict[str, ImageFont.FreeTypeFont],
) -> None:
    x0, y0, x1, y1 = area
    draw = ImageDraw.Draw(canvas)
    snapshot = progress_snapshot(trajectory, t_real)
    STYLE._draw_panel(canvas, area, radius=30, fill=COLORS["panel"], outline=COLORS["panel_line"], accent=COLORS["accent"])

    draw.text((x0 + 24, y0 + 24), "Agent Build Trace", fill=COLORS["white"], font=fonts["title"])
    STYLE._draw_chip(
        canvas,
        (x1 - 178, y0 + 24, x1 - 24, y0 + 50),
        text="REAL SCRIPT TRACE",
        font=fonts["mono_small"],
        fill=COLORS["accent_soft"],
        text_fill=COLORS["accent"],
        outline=COLORS["accent"],
    )

    active_label = snapshot["active_cmd"]["label"] if snapshot["active_cmd"] else (
        snapshot["current_event"]["step_label"] if snapshot["current_event"] else "waiting for first build step"
    )
    draw.text((x0 + 24, y0 + 58), STYLE._trim_middle(active_label, 46), fill="#9bb4ce", font=fonts["body"])
    STYLE._draw_segment_bar(
        canvas,
        (x0 + 24, y0 + 90, x1 - 24, y0 + 101),
        done=snapshot["completed_cmds"],
        total=max(1, snapshot["total_cmds"]),
        fill=COLORS["accent"],
        empty=COLORS["panel_line"],
    )

    chip_y = y0 + 116
    chip_specs = [
        (f"step {snapshot['completed_cmds']:02d}/{snapshot['total_cmds']:02d}", COLORS["chip_bg"], COLORS["chip_text"]),
        (f"preview {snapshot['completed_previews']:02d}/{snapshot['total_previews']:02d}", COLORS["chip_bg"], COLORS["chip_text"]),
        ("manual live preview", COLORS["accent_soft"], COLORS["accent"]),
    ]
    chip_x = x0 + 24
    for text, fill, text_fill in chip_specs:
        bbox = draw.textbbox((0, 0), text, font=fonts["mono_small"])
        chip_w = (bbox[2] - bbox[0]) + 24
        STYLE._draw_chip(
            canvas,
            (chip_x, chip_y, chip_x + chip_w, chip_y + 24),
            text=text,
            font=fonts["mono_small"],
            fill=fill,
            text_fill=text_fill,
            outline=COLORS["panel_line"],
        )
        chip_x += chip_w + 10

    body_area = (x0 + 16, y0 + 154, x1 - 16, y1 - 44)
    STYLE._alpha_box(canvas, body_area, radius=22, fill=STYLE._rgba(COLORS["terminal_bg"], 246), outline=STYLE._rgba(COLORS["panel_line"], 255), width=1)

    draw.text((body_area[0] + 18, body_area[1] + 16), "Recent steps", fill=COLORS["white"], font=fonts["body"])
    draw.text((body_area[2] - 166, body_area[1] + 16), "scripted build flow", fill=COLORS["terminal_muted"], font=fonts["small"])

    cards = build_command_cards(trajectory, t_real, max_cards=6)
    card_gap = 10
    card_height = 82
    card_x0 = body_area[0] + 14
    card_x1 = body_area[2] - 14
    card_y = body_area[1] + 48
    for card in cards:
        status = card["status"]
        if status == "live":
            fill = "#0d2630"
            outline = COLORS["accent"]
            status_fill = COLORS["accent_soft"]
            status_text = COLORS["accent"]
            label_fill = COLORS["white"]
        elif status == "done":
            fill = "#0e1826"
            outline = COLORS["panel_line"]
            status_fill = "#123648"
            status_text = "#9ddfff"
            label_fill = "#dbe6f3"
        else:
            fill = "#0a111a"
            outline = "#173049"
            status_fill = "#111f30"
            status_text = "#6f87a2"
            label_fill = "#9bb0c7"

        box = (card_x0, card_y, card_x1, card_y + card_height)
        STYLE._alpha_box(canvas, box, radius=18, fill=STYLE._rgba(fill, 248), outline=STYLE._rgba(outline, 255), width=2 if status == "live" else 1)
        STYLE._alpha_box(canvas, (box[0] + 10, box[1] + 10, box[0] + 14, box[3] - 10), radius=2, fill=STYLE._rgba(outline, 255))
        if status == "live":
            STYLE._draw_soft_glow(canvas, center=(box[2] - 34, box[1] + 24), radius=26, color=COLORS["accent"], strength=34)

        STYLE._draw_chip(
            canvas,
            (box[0] + 22, box[1] + 12, box[0] + 74, box[1] + 34),
            text=f"{card['index'] + 1:02d}",
            font=fonts["mono_small"],
            fill=COLORS["chip_bg"],
            text_fill=COLORS["chip_text"],
            outline=COLORS["panel_line"],
        )
        STYLE._draw_chip(
            canvas,
            (box[2] - 114, box[1] + 12, box[2] - 18, box[1] + 34),
            text=status.upper(),
            font=fonts["mono_small"],
            fill=status_fill,
            text_fill=status_text,
            outline=outline,
        )
        draw.text((box[0] + 84, box[1] + 10), STYLE._trim_middle(card["label"], 38), fill=label_fill, font=fonts["body"])
        draw.text((box[2] - 182, box[3] - 26), f"{card['duration_s']:.2f}s", fill=COLORS["terminal_muted"], font=fonts["mono_small"])

        command_lines = STYLE._wrap_trimmed(STYLE._readable_command_text(card["command"]), width_chars=54, max_lines=2)
        cmd_y = box[1] + 38
        for line in command_lines:
            draw.text((box[0] + 22, cmd_y), line, fill=COLORS["terminal_cmd"] if status != "queued" else "#6e8aa6", font=fonts["mono_small"])
            cmd_y += 17

        card_y += card_height + card_gap

    footer = "Step-aligned build trace driven by the real Blender stage_log; preview captures remain real artifacts."
    draw.text((x0 + 24, y1 - 28), footer, fill=COLORS["terminal_muted"], font=fonts["small"])
