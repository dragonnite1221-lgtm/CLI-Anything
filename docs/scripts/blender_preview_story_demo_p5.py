# ruff: noqa: F403, F405, E501
from .blender_preview_story_demo_base import *  # noqa: F403
# fmt: off
from .blender_preview_story_demo_p1 import COLORS, FPS, STYLE, VIDEO_H, VIDEO_W  # noqa: E402,E501
from .blender_preview_story_demo_p7 import main  # noqa: E402,E501
# fmt: on


def transform_turntable(turntable_video: Path, output_dir: Path, fps: int) -> Path:
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    transformed = output_dir / "turntable-ending.mp4"
    vf = (
        f"fps={fps},"
        f"scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=decrease,"
        f"pad={VIDEO_W}:{VIDEO_H}:(ow-iw)/2:(oh-ih)/2:color=0x030b16"
    )
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(turntable_video),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(transformed),
    ]
    subprocess.run(cmd, cwd=output_dir, capture_output=True, text=True, timeout=600, check=True)
    return transformed
def concat_videos(process_video: Path, turntable_video: Path, output_path: Path) -> None:
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    concat_list = output_path.parent / "concat.txt"
    concat_list.write_text(
        f"file '{process_video.as_posix()}'\nfile '{turntable_video.as_posix()}'\n",
        encoding="utf-8",
    )
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_list),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]
    subprocess.run(cmd, cwd=output_path.parent, capture_output=True, text=True, timeout=600, check=True)
def parse_args() -> argparse.Namespace:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--build-manifest",
        default=f"/root/preview-artifacts/{today}/blender-orbital-relay-drone-v6/build_manifest.json",
        help="Existing Blender build_manifest.json path from the orbital relay drone demo.",
    )
    parser.add_argument(
        "--output-dir",
        default=f"/root/preview-artifacts/{today}/blender-orbital-relay-drone-story-v5",
        help="Directory for trajectory.json, process frames, stills, and the final polished video assembled from real preview bundles.",
    )
    parser.add_argument("--fps", type=int, default=FPS, help="Output video FPS.")
    parser.add_argument(
        "--discard-frames",
        action="store_true",
        help="Delete intermediate composed process frames after MP4 encoding.",
    )
    return parser.parse_args()
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
    STYLE._alpha_box(canvas, box, radius=18 if main else 14, fill=STYLE._rgba(COLORS["paper"], 255), outline=STYLE._rgba(COLORS["paper_line"], 255), width=2)
    if img_path and Path(img_path).is_file():
        fit = STYLE.fit_image(Image.open(img_path), (max(1, x1 - x0 - 18), max(1, y1 - y0 - 18)), background=COLORS["paper"])
        canvas.paste(fit.convert("RGBA"), (x0 + 9, y0 + 9))
    STYLE._draw_chip(
        canvas,
        (x0 + 12, y0 + 12, x0 + 112, y0 + 36),
        text=label,
        font=fonts["mono_small"],
        fill="#fffaf3",
        text_fill="#5b5145",
        outline=COLORS["paper_line"],
    )
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.line((x0 + 10, y0 + 10, x0 + 30, y0 + 10), fill=STYLE._rgba(COLORS["accent_warm"], 160), width=2)
    draw.line((x0 + 10, y0 + 10, x0 + 10, y0 + 30), fill=STYLE._rgba(COLORS["accent_warm"], 160), width=2)
    draw.line((x1 - 10, y1 - 10, x1 - 30, y1 - 10), fill=STYLE._rgba(COLORS["accent"], 160), width=2)
    draw.line((x1 - 10, y1 - 10, x1 - 10, y1 - 30), fill=STYLE._rgba(COLORS["accent"], 160), width=2)
    canvas.alpha_composite(overlay)
