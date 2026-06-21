# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p1 import COLORS, FPS, VIDEO_H, VIDEO_W  # noqa: E402,E501
from .freecad_live_preview_demo_p29 import SCENARIOS  # noqa: E402,E501
from .freecad_live_preview_demo_p32 import fit_image  # noqa: E402,E501
from .freecad_live_preview_demo_p36 import _alpha_box, _draw_chip, _draw_panel, _draw_segment_bar, _rgba  # noqa: E402,E501
from .freecad_live_preview_demo_p38 import draw_global_header  # noqa: E402,E501
# fmt: on


def compose_showcase_frame(
    trajectory: Dict[str, Any],
    showcase: Dict[str, Any],
    showcase_t: float,
    final_t_real: float,
    fonts: Dict[str, ImageFont.FreeTypeFont],
    backdrop: Image.Image,
    image_cache: Dict[int, Image.Image],
) -> Image.Image:
    sequence = showcase.get("sequence") or {}
    frames = sequence.get("frames") or []
    if not frames:
        raise RuntimeError("Showcase sequence is empty")

    total_duration = float(showcase.get("duration_s") or 0.0)
    if total_duration <= 0.0:
        last_time = float(frames[-1].get("time") or 0.0)
        fps = int(sequence.get("fps") or FPS)
        total_duration = last_time if last_time > 0 else max(0.01, (len(frames) - 1) / max(1, fps))
    clamped_t = max(0.0, min(showcase_t, total_duration))
    sequence_pos = (clamped_t / max(0.01, total_duration)) * (len(frames) - 1)
    frame_index = min(len(frames) - 1, int(round(sequence_pos)))

    stage_size = (VIDEO_W - 180, VIDEO_H - 250)

    def _stage_image(idx: int) -> Image.Image:
        cached = image_cache.get(idx)
        if cached is not None:
            return cached
        sequence_path = Path(showcase["sequence_path"]).expanduser().resolve()
        source_path = sequence_path.parent / frames[idx]["path"]
        stage = fit_image(Image.open(source_path), stage_size, background=COLORS["paper"])
        cached = stage.convert("RGBA")
        image_cache[idx] = cached
        return cached

    stage = _stage_image(frame_index)

    canvas = backdrop.copy()
    overlay = Image.new("RGBA", canvas.size, _rgba("#050913", 138))
    canvas.alpha_composite(overlay)
    draw_global_header(canvas, trajectory, final_t_real, fonts)

    panel = (54, 118, VIDEO_W - 54, VIDEO_H - 54)
    _draw_panel(canvas, panel, radius=34, fill=COLORS["panel"], outline=COLORS["panel_line"], accent=COLORS["accent_warm"])

    draw = ImageDraw.Draw(canvas)
    draw.text((panel[0] + 26, panel[1] + 24), "Final Showcase", fill=COLORS["white"], font=fonts["title"])
    _draw_chip(
        canvas,
        (panel[2] - 246, panel[1] + 22, panel[2] - 24, panel[1] + 50),
        text="TRUE FREECAD MOTION",
        font=fonts["mono_small"],
        fill="#351d17",
        text_fill=COLORS["accent_warm"],
        outline=COLORS["accent_warm"],
    )

    subtitle = showcase.get("subtitle") or "real frame-by-frame FreeCAD motion render from the final project"
    draw.text((panel[0] + 26, panel[1] + 56), subtitle, fill=COLORS["preview_muted"], font=fonts["body"])

    stage_box = (panel[0] + 26, panel[1] + 92, panel[2] - 26, panel[3] - 88)
    _alpha_box(canvas, stage_box, radius=28, fill=_rgba(COLORS["preview_shell"], 255), outline=_rgba(COLORS["panel_line"], 255), width=2)
    inset = (stage_box[0] + 16, stage_box[1] + 16)
    canvas.paste(stage, inset, stage)

    frame_label = f"frame {frame_index + 1:03d}/{len(frames):03d}"
    progress_label = f"showcase {showcase_t:04.1f}s / {total_duration:04.1f}s"
    _draw_chip(
        canvas,
        (stage_box[0] + 20, stage_box[1] + 18, stage_box[0] + 150, stage_box[1] + 42),
        text=frame_label.upper(),
        font=fonts["mono_small"],
        fill="#fffaf3",
        text_fill="#5b5145",
        outline=COLORS["paper_line"],
    )
    _draw_chip(
        canvas,
        (stage_box[2] - 190, stage_box[1] + 18, stage_box[2] - 20, stage_box[1] + 42),
        text=progress_label.upper(),
        font=fonts["mono_small"],
        fill=COLORS["chip_bg"],
        text_fill=COLORS["chip_text"],
        outline=COLORS["panel_line"],
    )

    _draw_segment_bar(
        canvas,
        (panel[0] + 26, panel[3] - 52, panel[2] - 26, panel[3] - 38),
        done=max(1, frame_index + 1),
        total=max(1, len(frames)),
        fill=COLORS["accent_warm"],
        empty=COLORS["panel_line"],
    )

    footer = "Real ending sequence: final project JSON + cli-anything-freecad motion render-video + programmatic composition"
    draw.text((panel[0] + 26, panel[3] - 74), footer, fill=COLORS["preview_muted"], font=fonts["small"])
    return canvas
def parse_args() -> argparse.Namespace:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    default_output = Path.home() / "preview-artifacts" / today / "freecad-live-video"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode",
        choices=["collect", "render", "run-all", "motion-showcase"],
        help="Collect a real trajectory, render a video from an existing trajectory, or do both.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(default_output),
        help="Directory for collected artifacts, live preview state, trajectory.json, and rendered video.",
    )
    parser.add_argument(
        "--scenario",
        default="orbital-relay",
        choices=sorted(SCENARIOS),
        help="Demo scenario to collect.",
    )
    parser.add_argument(
        "--timeline",
        default=None,
        help="Existing trajectory.json path for render or motion-showcase mode.",
    )
    parser.add_argument("--fps", type=int, default=FPS, help="Output video framerate.")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier.")
    parser.add_argument("--no-frames", action="store_true", help="Delete intermediate frame PNGs after encoding.")
    parser.add_argument(
        "--motion-style",
        default="drive",
        choices=["drive", "spin", "combo"],
        help="Motion showcase style for motion-showcase mode.",
    )
    return parser.parse_args()
