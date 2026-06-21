# ruff: noqa: F403, F405, E501
from .blender_preview_story_demo_base import *  # noqa: F403
# fmt: off
from .blender_preview_story_demo_p1 import COLORS, STYLE  # noqa: E402,E501
from .blender_preview_story_demo_p3 import pick_preview_event, progress_snapshot  # noqa: E402,E501
from .blender_preview_story_demo_p5 import _paste_preview_card  # noqa: E402,E501
# fmt: on


def draw_preview_panel(
    canvas: Image.Image,
    area: tuple[int, int, int, int],
    trajectory: Dict[str, Any],
    t_real: float,
    fonts: Dict[str, ImageFont.FreeTypeFont],
    image_cache: Dict[str, Image.Image],
) -> None:
    x0, y0, x1, y1 = area
    draw = ImageDraw.Draw(canvas)
    snapshot = progress_snapshot(trajectory, t_real)
    STYLE._draw_panel(canvas, area, radius=30, fill=COLORS["panel"], outline=COLORS["panel_line"], accent=COLORS["accent_warm"])
    draw.text((x0 + 24, y0 + 24), "Preview Monitor", fill=COLORS["white"], font=fonts["title"])
    STYLE._draw_chip(
        canvas,
        (x1 - 152, y0 + 24, x1 - 24, y0 + 50),
        text="LIVE BUNDLES",
        font=fonts["mono_small"],
        fill="#351d17",
        text_fill=COLORS["accent_warm"],
        outline=COLORS["accent_warm"],
    )
    draw.text((x0 + 24, y0 + 58), "Real Blender quick-preview bundles from the active build run", fill=COLORS["preview_muted"], font=fonts["body"])

    event = pick_preview_event(trajectory, t_real)
    if event is None:
        draw.text((x0 + 28, y0 + 96), "Waiting for first Blender preview bundle...", fill=COLORS["preview_muted"], font=fonts["body"])
        return

    current = event["copied_bundle"]
    summary = current.get("summary") or {}
    facts = summary.get("facts") or {}
    previous_event = None
    if event["sequence_index"] > 1:
        previous_event = trajectory["preview_events"][event["sequence_index"] - 2]

    stage_area = (x0 + 20, y0 + 96, x1 - 260, y1 - 20)
    info_area = (x1 - 244, y0 + 96, x1 - 20, y1 - 20)
    STYLE._alpha_box(canvas, info_area, radius=20, fill=STYLE._rgba(COLORS["panel_soft"], 252), outline=STYLE._rgba(COLORS["panel_line"], 255), width=1)

    main_box = (stage_area[0], stage_area[1], stage_area[2], int(stage_area[1] + (stage_area[3] - stage_area[1]) * 0.73))
    _paste_preview_card(canvas, main_box, img_path=current["artifacts"].get("hero"), label="HERO", fonts=fonts, main=True)

    thumb_y = main_box[3] + 10
    thumb_h = stage_area[3] - thumb_y
    thumb_w = (stage_area[2] - stage_area[0] - 12) // 2
    _paste_preview_card(
        canvas,
        (stage_area[0], thumb_y, stage_area[0] + thumb_w, thumb_y + thumb_h),
        img_path=current["artifacts"].get("workbench"),
        label="WORKBENCH",
        fonts=fonts,
    )
    secondary_label = "FINAL STILL"
    secondary_img = trajectory.get("final_render")
    if previous_event is not None:
        secondary_label = "PREV HERO"
        secondary_img = previous_event["copied_bundle"]["artifacts"].get("hero")
    _paste_preview_card(
        canvas,
        (stage_area[0] + thumb_w + 12, thumb_y, stage_area[2], thumb_y + thumb_h),
        img_path=secondary_img,
        label=secondary_label,
        fonts=fonts,
    )

    draw.text((info_area[0] + 16, info_area[1] + 16), "Telemetry", fill=COLORS["white"], font=fonts["body"])
    meta_lines = [
        ("STAGE", event["stage_title"]),
        ("BUNDLE", STYLE._trim_middle(current["bundle_id"], 18)),
        ("CAUSE", STYLE._trim_middle(str(event.get("publish_reason") or "n/a"), 18)),
        ("LATENCY", f"{event.get('latency_s', 0.0):.2f}s"),
        ("FRAME", str(facts.get("frame_current", "n/a"))),
        ("STREAM", f"{event['sequence_index']:02d}/{len(trajectory['preview_events']):02d}"),
    ]
    meta_y = info_area[1] + 46
    for label, value in meta_lines:
        STYLE._draw_chip(
            canvas,
            (info_area[0] + 16, meta_y, info_area[2] - 16, meta_y + 28),
            text=label,
            font=fonts["mono_small"],
            fill=COLORS["chip_bg"],
            text_fill=COLORS["chip_text"],
            outline=COLORS["panel_line"],
        )
        draw.text((info_area[0] + 18, meta_y + 36), STYLE._trim_middle(str(value), 26), fill=COLORS["white"], font=fonts["body"])
        meta_y += 74

    story_lines = STYLE._wrap_trimmed(event["stage_story"], width_chars=24, max_lines=5)
    note_title = "Stage note"
    if snapshot["active_cmd"] and snapshot["active_cmd"]["id"] in {"final-still", "turntable"}:
        note_title = "Handoff note"
    draw.text((info_area[0] + 16, info_area[3] - 176), note_title, fill=COLORS["white"], font=fonts["body"])
    story_y = info_area[3] - 148
    for line in story_lines:
        draw.text((info_area[0] + 16, story_y), line, fill=COLORS["preview_muted"], font=fonts["small"])
        story_y += 18

    STYLE._draw_segment_bar(
        canvas,
        (info_area[0] + 16, info_area[3] - 32, info_area[2] - 16, info_area[3] - 18),
        done=max(1, event["sequence_index"]),
        total=max(1, len(trajectory["preview_events"])),
        fill=COLORS["accent_warm"],
        empty=COLORS["panel_line"],
    )
