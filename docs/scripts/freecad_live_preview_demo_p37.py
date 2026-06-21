# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p1 import COLORS, VIDEO_H, VIDEO_W  # noqa: E402,E501
from .freecad_live_preview_demo_p36 import _mix, _rgba  # noqa: E402,E501
# fmt: on


def _draw_soft_glow(
    canvas: Image.Image,
    *,
    center: tuple[int, int],
    radius: int,
    color: str,
    strength: int,
) -> None:
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = center
    for idx, scale in enumerate((1.0, 0.72, 0.45)):
        r = int(radius * scale)
        alpha = max(0, strength - idx * (strength // 3))
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=_rgba(color, alpha))
    canvas.alpha_composite(overlay)
def build_static_backdrop() -> Image.Image:
    image = Image.new("RGBA", (VIDEO_W, VIDEO_H), _rgba(COLORS["bg_bottom"]))
    pixels = image.load()
    for y in range(VIDEO_H):
        row = _mix(COLORS["bg_top"], COLORS["bg_bottom"], y / max(1, VIDEO_H - 1))
        for x in range(VIDEO_W):
            pixels[x, y] = (*row, 255)

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for x in range(0, VIDEO_W, 42):
        draw.line((x, 0, x, VIDEO_H), fill=_rgba(COLORS["grid_soft"], 48), width=1)
    for y in range(0, VIDEO_H, 42):
        draw.line((0, y, VIDEO_W, y), fill=_rgba(COLORS["grid_soft"], 40), width=1)

    for x in range(0, VIDEO_W, 168):
        draw.line((x, 0, x, VIDEO_H), fill=_rgba(COLORS["grid"], 42), width=1)
    for y in range(0, VIDEO_H, 168):
        draw.line((0, y, VIDEO_W, y), fill=_rgba(COLORS["grid"], 38), width=1)

    draw.arc((-180, 560, 430, 1170), start=272, end=18, fill=_rgba(COLORS["accent"], 46), width=2)
    draw.arc((1180, -220, 1840, 420), start=156, end=292, fill=_rgba(COLORS["accent_warm"], 38), width=2)
    draw.line((0, VIDEO_H - 88, VIDEO_W, VIDEO_H - 88), fill=_rgba(COLORS["grid"], 55), width=1)
    draw.line((0, 74, VIDEO_W, 74), fill=_rgba(COLORS["grid"], 32), width=1)
    image.alpha_composite(overlay)

    _draw_soft_glow(image, center=(270, 180), radius=180, color=COLORS["accent"], strength=26)
    _draw_soft_glow(image, center=(1310, 160), radius=240, color=COLORS["accent_warm"], strength=22)
    _draw_soft_glow(image, center=(1130, 710), radius=200, color=COLORS["panel_glow"], strength=16)
    return image
def text_lines(text: str, width_chars: int) -> List[str]:
    lines: List[str] = []
    for raw in text.splitlines():
        if not raw:
            lines.append("")
            continue
        wrapped = textwrap.wrap(raw, width=width_chars, replace_whitespace=False, drop_whitespace=False)
        lines.extend(wrapped or [""])
    return lines
def build_terminal_lines(trajectory: Dict[str, Any], t_real: float, *, width_chars: int) -> List[Dict[str, str]]:
    lines: List[Dict[str, str]] = []
    active_cmd: Optional[Dict[str, Any]] = None

    for cmd in trajectory["commands"]:
        if cmd["timeline_start_s"] > t_real:
            break
        lines.append({"text": f"$ {cmd['display_cmd']}", "kind": "cmd"})
        if t_real < cmd["timeline_end_s"]:
            active_cmd = cmd
            dots = "." * (1 + (int(t_real * 3) % 3))
            lines.append({"text": f"# running{dots}", "kind": "muted"})
            break
        stdout = cmd.get("stdout", "")
        stderr = cmd.get("stderr", "")
        if stdout.strip():
            for line in text_lines(stdout.rstrip(), width_chars):
                stripped = line.strip()
                kind = "json" if stripped.startswith(("{", "}", "[", "]", "\"")) else "out"
                lines.append({"text": line, "kind": kind})
        if stderr.strip():
            for line in text_lines(stderr.rstrip(), width_chars):
                lines.append({"text": line, "kind": "err"})
        lines.append({"text": "", "kind": "out"})

    if active_cmd is None and trajectory["commands"]:
        last_cmd = trajectory["commands"][-1]
        if t_real > last_cmd["timeline_end_s"] + 0.8:
            lines.append({"text": "# trajectory complete", "kind": "success"})
    return lines[-30:]
def pick_preview_event(trajectory: Dict[str, Any], t_real: float) -> Optional[Dict[str, Any]]:
    latest = None
    for event in trajectory["preview_events"]:
        if event["timeline_ready_s"] <= t_real:
            latest = event
        else:
            break
    return latest
def progress_snapshot(trajectory: Dict[str, Any], t_real: float) -> Dict[str, Any]:
    completed_cmds = sum(1 for cmd in trajectory["commands"] if cmd["timeline_end_s"] <= t_real)
    completed_previews = sum(1 for event in trajectory["preview_events"] if event["timeline_ready_s"] <= t_real)
    active_cmd = None
    for cmd in trajectory["commands"]:
        if cmd["timeline_start_s"] <= t_real < cmd["timeline_end_s"]:
            active_cmd = cmd
            break
    return {
        "completed_cmds": completed_cmds,
        "total_cmds": len(trajectory["commands"]),
        "completed_previews": completed_previews,
        "total_previews": len(trajectory["preview_events"]),
        "active_cmd": active_cmd,
        "current_event": pick_preview_event(trajectory, t_real),
    }
