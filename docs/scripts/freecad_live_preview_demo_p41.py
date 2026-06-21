# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p1 import COLORS  # noqa: E402,E501
from .freecad_live_preview_demo_p32 import fit_image  # noqa: E402,E501
from .freecad_live_preview_demo_p36 import _alpha_box, _draw_chip, _draw_panel, _draw_segment_bar, _rgba, _trim_middle  # noqa: E402,E501
from .freecad_live_preview_demo_p37 import pick_preview_event  # noqa: E402,E501
from .freecad_live_preview_demo_p42 import main  # noqa: E402,E501
# fmt: on


def _paste_preview_card(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    *,
    img_path: Optional[str],
    label: str,
    fonts: Dict[str, ImageFont.FreeTypeFont],
    main: bool = False,
) -> None:
    x0, y0, x1, y1 = box
    _alpha_box(canvas, box, radius=18 if main else 14, fill=_rgba(COLORS["paper"], 255), outline=_rgba(COLORS["paper_line"], 255), width=2)
    if img_path and Path(img_path).is_file():
        fit = fit_image(Image.open(img_path), (max(1, x1 - x0 - 18), max(1, y1 - y0 - 18)), background=COLORS["paper"])
        canvas.paste(fit.convert("RGBA"), (x0 + 9, y0 + 9))
    _draw_chip(
        canvas,
        (x0 + 12, y0 + 12, x0 + 100, y0 + 36),
        text=label,
        font=fonts["mono_small"],
        fill="#fffaf3",
        text_fill="#5b5145",
        outline=COLORS["paper_line"],
    )
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.line((x0 + 10, y0 + 10, x0 + 30, y0 + 10), fill=_rgba(COLORS["accent_warm"], 160), width=2)
    draw.line((x0 + 10, y0 + 10, x0 + 10, y0 + 30), fill=_rgba(COLORS["accent_warm"], 160), width=2)
    draw.line((x1 - 10, y1 - 10, x1 - 30, y1 - 10), fill=_rgba(COLORS["accent"], 160), width=2)
    draw.line((x1 - 10, y1 - 10, x1 - 10, y1 - 30), fill=_rgba(COLORS["accent"], 160), width=2)
    canvas.alpha_composite(overlay)
def compose_preview_dashboard(
    event: Dict[str, Any],
    size: tuple[int, int],
    *,
    scenario: str,
    fonts: Dict[str, ImageFont.FreeTypeFont],
) -> Image.Image:
    width, height = size
    canvas = Image.new("RGBA", size, _rgba(COLORS["preview_shell"], 255))
    _alpha_box(canvas, (0, 0, width - 1, height - 1), radius=22, fill=_rgba(COLORS["preview_shell"], 255), outline=_rgba(COLORS["panel_line"], 255), width=2)

    copied = event["copied_bundle"]["artifacts"]
    primary = "front" if scenario in {"empire-state-building", "taipei-101"} else "hero"
    secondary = ["hero", "right", "top"] if primary == "front" else ["front", "top", "right"]

    main_box = (18, 18, width - 18, int(height * 0.74))
    _paste_preview_card(canvas, main_box, img_path=copied.get(primary), label=primary.upper(), fonts=fonts, main=True)

    thumb_y = int(height * 0.77)
    thumb_h = height - thumb_y - 18
    thumb_w = (width - 48) // len(secondary)
    for idx, key in enumerate(secondary):
        x0 = 18 + idx * (thumb_w + 6)
        _paste_preview_card(
            canvas,
            (x0, thumb_y, x0 + thumb_w, thumb_y + thumb_h),
            img_path=copied.get(key),
            label=key.upper(),
            fonts=fonts,
        )
    return canvas
def draw_preview_panel(
    canvas: Image.Image,
    area: tuple[int, int, int, int],
    trajectory: Dict[str, Any],
    t_real: float,
    fonts: Dict[str, ImageFont.FreeTypeFont],
) -> None:
    x0, y0, x1, y1 = area
    draw = ImageDraw.Draw(canvas)
    _draw_panel(canvas, area, radius=30, fill=COLORS["panel"], outline=COLORS["panel_line"], accent=COLORS["accent_warm"])
    draw.text((x0 + 24, y0 + 24), "Preview Monitor", fill=COLORS["white"], font=fonts["title"])
    _draw_chip(
        canvas,
        (x1 - 140, y0 + 24, x1 - 24, y0 + 50),
        text="POLL MODE",
        font=fonts["mono_small"],
        fill="#351d17",
        text_fill=COLORS["accent_warm"],
        outline=COLORS["accent_warm"],
    )
    draw.text((x0 + 24, y0 + 58), "Bundle stream from the active FreeCAD live session", fill=COLORS["preview_muted"], font=fonts["body"])

    event = pick_preview_event(trajectory, t_real)
    if event is None:
        draw.text((x0 + 28, y0 + 96), "Waiting for first live preview bundle...", fill=COLORS["preview_muted"], font=fonts["body"])
        return

    command = trajectory["commands"][event["step_index"]]
    info_w = 246
    stage_area = (x0 + 20, y0 + 96, x1 - info_w - 18, y1 - 20)
    info_area = (x1 - info_w, y0 + 96, x1 - 20, y1 - 20)
    _alpha_box(canvas, info_area, radius=20, fill=_rgba(COLORS["panel_soft"], 252), outline=_rgba(COLORS["panel_line"], 255), width=1)

    scenario = trajectory.get("scenario")
    stage = compose_preview_dashboard(
        event,
        (stage_area[2] - stage_area[0], stage_area[3] - stage_area[1]),
        scenario=scenario or "",
        fonts=fonts,
    )
    canvas.paste(stage, (stage_area[0], stage_area[1]))

    meta_lines = [
        ("STEP", event["step_label"]),
        ("BUNDLE", _trim_middle(event["copied_bundle"]["bundle_id"], 18)),
        ("CAUSE", event.get("publish_reason") or "n/a"),
        ("LATENCY", f"{event['latency_s']:.2f}s"),
        ("CMD TIME", f"{command['duration_s']:.2f}s"),
        ("STREAM", f"{event.get('sequence_index', event['bundle_count']):02d}/{len(trajectory['preview_events']):02d}"),
    ]

    draw.text((info_area[0] + 16, info_area[1] + 16), "Telemetry", fill=COLORS["white"], font=fonts["body"])
    meta_y = info_area[1] + 46
    for label, value in meta_lines:
        _draw_chip(
            canvas,
            (info_area[0] + 16, meta_y, info_area[2] - 16, meta_y + 28),
            text=label,
            font=fonts["mono_small"],
            fill=COLORS["chip_bg"],
            text_fill=COLORS["chip_text"],
            outline=COLORS["panel_line"],
        )
        draw.text((info_area[0] + 18, meta_y + 36), value, fill=COLORS["white"], font=fonts["body"])
        meta_y += 74

    step_progress = event.get("sequence_index", event["bundle_count"])
    _draw_segment_bar(
        canvas,
        (info_area[0] + 16, info_area[3] - 52, info_area[2] - 16, info_area[3] - 38),
        done=step_progress,
        total=max(1, len(trajectory["preview_events"])),
        fill=COLORS["accent_warm"],
        empty=COLORS["panel_line"],
    )
    draw.text((info_area[0] + 16, info_area[3] - 80), "Real preview artifacts only. No synthetic viewport frames.", fill=COLORS["preview_muted"], font=fonts["small"])
