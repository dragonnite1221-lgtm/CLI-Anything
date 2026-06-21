# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p1 import CLI_HUB, FREECAD_CLI  # noqa: E402,E501
# fmt: on


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)
def _hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[idx:idx + 2], 16) for idx in (0, 2, 4))
def _rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    r, g, b = _hex_rgb(value)
    return (r, g, b, alpha)
def _mix(color_a: str, color_b: str, t: float) -> tuple[int, int, int]:
    a = _hex_rgb(color_a)
    b = _hex_rgb(color_b)
    t = max(0.0, min(1.0, t))
    return tuple(int(a[idx] + (b[idx] - a[idx]) * t) for idx in range(3))
def _trim_middle(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    keep = max(4, (max_len - 1) // 2)
    return f"{text[:keep]}…{text[-keep:]}"
def _wrap_trimmed(text: str, *, width_chars: int, max_lines: int) -> List[str]:
    wrapped = textwrap.wrap(text, width=width_chars, replace_whitespace=False, drop_whitespace=False) or [text]
    if len(wrapped) > max_lines:
        wrapped = wrapped[:max_lines]
        wrapped[-1] = _trim_middle(wrapped[-1].strip(), width_chars)
    return [line.rstrip() for line in wrapped]
def _readable_command_text(cmd_text: str) -> str:
    normalized = cmd_text.strip()
    replacements = {
        str(Path(FREECAD_CLI)): "cli-anything-freecad",
        str(Path(CLI_HUB)): "cli-hub",
        "/root/miniconda3/bin/cli-anything-freecad": "cli-anything-freecad",
        "/root/miniconda3/bin/cli-hub": "cli-hub",
    }
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return normalized
def _draw_text_right(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    *,
    font: ImageFont.FreeTypeFont,
    fill: str,
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text((x - (bbox[2] - bbox[0]), y), text, fill=fill, font=font)
def _alpha_box(
    canvas: Image.Image,
    area: tuple[int, int, int, int],
    *,
    radius: int,
    fill: tuple[int, int, int, int],
    outline: Optional[tuple[int, int, int, int]] = None,
    width: int = 1,
) -> None:
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(area, radius=radius, fill=fill, outline=outline, width=width)
    canvas.alpha_composite(overlay)
def _draw_panel(
    canvas: Image.Image,
    area: tuple[int, int, int, int],
    *,
    radius: int,
    fill: str,
    outline: str,
    accent: Optional[str] = None,
) -> None:
    x0, y0, x1, y1 = area
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    for offset, alpha in ((20, 24), (10, 40), (4, 72)):
        draw.rounded_rectangle(
            (x0 + offset, y0 + offset, x1 + offset, y1 + offset),
            radius=radius,
            fill=(0, 0, 0, alpha),
        )
    canvas.alpha_composite(shadow)
    _alpha_box(canvas, area, radius=radius, fill=_rgba(fill, 238), outline=_rgba(outline, 255), width=2)
    if accent:
        _alpha_box(canvas, (x0 + 14, y0 + 12, x1 - 14, y0 + 18), radius=6, fill=_rgba(accent, 220))
def _draw_chip(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    *,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    text_fill: str,
    outline: Optional[str] = None,
) -> None:
    x0, y0, x1, y1 = box
    _alpha_box(
        canvas,
        box,
        radius=min(14, (y1 - y0) // 2),
        fill=_rgba(fill, 245),
        outline=_rgba(outline or fill, 255),
        width=1,
    )
    draw = ImageDraw.Draw(canvas)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((x0 + ((x1 - x0) - tw) / 2, y0 + ((y1 - y0) - th) / 2 - 1), text, fill=text_fill, font=font)
def _draw_segment_bar(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    *,
    done: int,
    total: int,
    fill: str,
    empty: str,
) -> None:
    x0, y0, x1, y1 = box
    if total <= 0:
        return
    available_w = max(1, x1 - x0)
    min_seg_w = 1 if total > 28 else 2
    target_gap = 4 if total <= 18 else 2
    if total > 1:
        max_gap = max(0, (available_w - total * min_seg_w) // (total - 1))
        gap = min(target_gap, max_gap)
    else:
        gap = 0
    seg_w = max(min_seg_w, int((available_w - gap * (total - 1)) / total))
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for idx in range(total):
        sx0 = x0 + idx * (seg_w + gap)
        if sx0 >= x1:
            break
        sx1 = min(x1, max(sx0 + 1, sx0 + seg_w))
        color = fill if idx < done else empty
        alpha = 235 if idx < done else 125
        draw.rounded_rectangle((sx0, y0, sx1, y1), radius=4, fill=_rgba(color, alpha))
    canvas.alpha_composite(overlay)
