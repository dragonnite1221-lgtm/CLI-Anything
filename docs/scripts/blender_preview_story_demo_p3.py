# ruff: noqa: F403, F405, E501
from .blender_preview_story_demo_base import *  # noqa: F403
# fmt: off
from .blender_preview_story_demo_p1 import COLORS, DISPLAY_FONT_PATH, MONO_BOLD_FONT_PATH, MONO_FONT_PATH, SANS_FONT_PATH, STYLE, VIDEO_W  # noqa: E402,E501
# fmt: on


def _fonts() -> Dict[str, ImageFont.FreeTypeFont]:
    return {
        "display": STYLE.load_font(DISPLAY_FONT_PATH, 38),
        "title": STYLE.load_font(DISPLAY_FONT_PATH, 24),
        "body": STYLE.load_font(SANS_FONT_PATH, 17),
        "small": STYLE.load_font(SANS_FONT_PATH, 13),
        "mono": STYLE.load_font(MONO_FONT_PATH, 15),
        "mono_small": STYLE.load_font(MONO_BOLD_FONT_PATH, 12),
    }
def _draw_text_right(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, *, font: ImageFont.FreeTypeFont, fill: str) -> None:
    STYLE._draw_text_right(draw, x, y, text, font=font, fill=fill)
def progress_snapshot(trajectory: Dict[str, Any], t_real: float) -> Dict[str, Any]:
    return STYLE.progress_snapshot(trajectory, t_real)
def pick_preview_event(trajectory: Dict[str, Any], t_real: float) -> Optional[Dict[str, Any]]:
    return STYLE.pick_preview_event(trajectory, t_real)
def build_command_cards(trajectory: Dict[str, Any], t_real: float, *, max_cards: int = 6) -> List[Dict[str, Any]]:
    return STYLE.build_command_cards(trajectory, t_real, max_cards=max_cards)
def draw_global_header(
    canvas: Image.Image,
    trajectory: Dict[str, Any],
    t_real: float,
    fonts: Dict[str, ImageFont.FreeTypeFont],
) -> None:
    draw = ImageDraw.Draw(canvas)
    snapshot = progress_snapshot(trajectory, t_real)
    title = trajectory.get("scenario_title", "Blender Live Demo").upper()
    subtitle = trajectory.get("scenario_subtitle", "scripted build trace + real preview bundles")

    draw.text((34, 20), "CLI-ANYTHING / BLENDER / LIVE PREVIEW PROTOCOL", fill="#88a9c8", font=fonts["small"])
    draw.text((34, 36), title, fill=COLORS["white"], font=fonts["display"])
    draw.text((34, 68), subtitle, fill="#97abc2", font=fonts["body"])

    chip_y = 20
    chips = [
        f"T+ {t_real:05.1f}s",
        f"{snapshot['completed_cmds']:02d}/{snapshot['total_cmds']:02d} steps",
        f"{snapshot['completed_previews']:02d}/{snapshot['total_previews']:02d} bundles",
    ]
    x = VIDEO_W - 34
    for text in reversed(chips):
        bbox = draw.textbbox((0, 0), text, font=fonts["mono_small"])
        chip_w = (bbox[2] - bbox[0]) + 26
        STYLE._draw_chip(
            canvas,
            (x - chip_w, chip_y, x, chip_y + 26),
            text=text,
            font=fonts["mono_small"],
            fill=COLORS["chip_bg"],
            text_fill=COLORS["chip_text"],
            outline=COLORS["panel_line"],
        )
        x -= chip_w + 10

    draw.line((30, 98, VIDEO_W - 30, 98), fill=STYLE._rgba(COLORS["grid"], 120), width=1)
