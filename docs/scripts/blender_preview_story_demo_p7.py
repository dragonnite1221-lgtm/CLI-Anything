# ruff: noqa: F403, F405, E501
from .blender_preview_story_demo_base import *  # noqa: F403
# fmt: off
from .blender_preview_story_demo_p1 import FPS, HOLD_TAIL_S, LEFT_W, STYLE, VIDEO_H, VIDEO_W, load_json, write_json  # noqa: E402,E501
from .blender_preview_story_demo_p2 import build_trajectory  # noqa: E402,E501
from .blender_preview_story_demo_p3 import _draw_text_right, _fonts, draw_global_header  # noqa: E402,E501
from .blender_preview_story_demo_p4 import draw_trace_panel  # noqa: E402,E501
from .blender_preview_story_demo_p5 import concat_videos, parse_args, transform_turntable  # noqa: E402,E501
from .blender_preview_story_demo_p6 import draw_preview_panel  # noqa: E402,E501
# fmt: on


def render_process_video(
    trajectory: Dict[str, Any],
    *,
    output_dir: Path,
    fps: int,
    keep_frames: bool,
) -> Dict[str, Any]:
    frames_dir = STYLE.ensure_clean_dir(output_dir / "process-frames")
    stills_dir = STYLE.ensure_clean_dir(output_dir / "stills")
    process_video_path = output_dir / "process.mp4"

    fonts = _fonts()
    backdrop = STYLE.build_static_backdrop()
    image_cache: Dict[str, Image.Image] = {}

    last_t = max(cmd["timeline_end_s"] for cmd in trajectory["commands"])
    duration_s = last_t + HOLD_TAIL_S
    frame_count = int(math.ceil(duration_s * fps))

    early_idx = max(0, min(frame_count - 1, fps * 2))
    mid_idx = max(0, min(frame_count - 1, frame_count // 2))
    late_idx = max(0, frame_count - fps)
    still_targets = {
        early_idx: stills_dir / "early-command-stream.png",
        mid_idx: stills_dir / "mid-preview-monitor.png",
        late_idx: stills_dir / "late-build-state.png",
    }

    for frame_idx in range(frame_count):
        t_real = frame_idx / fps
        image = backdrop.copy()
        draw_global_header(image, trajectory, t_real, fonts)
        draw_trace_panel(image, (26, 116, LEFT_W - 14, VIDEO_H - 34), trajectory, t_real, fonts)
        draw_preview_panel(image, (LEFT_W + 10, 116, VIDEO_W - 26, VIDEO_H - 34), trajectory, t_real, fonts, image_cache)

        draw = ImageDraw.Draw(image)
        footer_left = "STEP-ALIGNED build trace · REAL Blender preview bundles · real turntable ending appended"
        footer_right = STYLE._trim_middle(str(output_dir / "trajectory.json"), 64)
        draw.text((34, VIDEO_H - 26), footer_left, fill="#7891ab", font=fonts["small"])
        _draw_text_right(draw, VIDEO_W - 34, VIDEO_H - 26, footer_right, font=fonts["mono_small"], fill="#7891ab")

        frame_path = frames_dir / f"frame_{frame_idx:05d}.png"
        rgb = image.convert("RGB")
        rgb.save(frame_path)
        target = still_targets.get(frame_idx)
        if target is not None:
            rgb.save(target)

    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    process_cmd = [
        ffmpeg,
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(frames_dir / "frame_%05d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(process_video_path),
    ]
    subprocess.run(process_cmd, cwd=output_dir, capture_output=True, text=True, timeout=600, check=True)

    if not keep_frames:
        shutil.rmtree(frames_dir)

    return {
        "process_video": str(process_video_path),
        "frames_dir": str(frames_dir) if keep_frames else None,
        "duration_s": duration_s,
        "frame_count": frame_count,
        "stills": {key.stem: str(key) for key in sorted(stills_dir.glob("*.png"))},
    }
def render_story(build_manifest_path: Path, output_dir: Path, *, fps: int = FPS, keep_frames: bool = True) -> Dict[str, Any]:
    build_manifest = load_json(build_manifest_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    trajectory = build_trajectory(build_manifest_path, output_dir)
    process_payload = render_process_video(trajectory, output_dir=output_dir, fps=fps, keep_frames=keep_frames)
    turntable_src = Path(trajectory["turntable_video"]).expanduser().resolve()
    transformed_turntable = transform_turntable(turntable_src, output_dir, fps)
    final_video = output_dir / "demo-polished.mp4"
    concat_videos(Path(process_payload["process_video"]), transformed_turntable, final_video)

    showcase_turntable = Path(build_manifest["motion"]["stills"]["mid"]).expanduser().resolve()
    showcase_turntable_copy = output_dir / "stills" / "showcase-turntable.png"
    shutil.copy2(showcase_turntable, showcase_turntable_copy)
    process_payload["stills"]["showcase-turntable"] = str(showcase_turntable_copy)

    manifest = {
        "protocol": "blender-preview-story/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "build_manifest_path": str(build_manifest_path.resolve()),
        "trajectory_path": str((output_dir / "trajectory.json").resolve()),
        "process": process_payload,
        "turntable_source": str(turntable_src),
        "turntable_transformed": str(transformed_turntable),
        "final_video": str(final_video),
        "notes": [
            "The process section is a programmatic composition of a scripted agent build trace and real Blender preview bundles.",
            "The ending is the existing real turntable video from the same Blender run, transformed only for resolution consistency before concatenation.",
        ],
    }
    write_json(output_dir / "story_manifest.json", manifest)
    return manifest
def main() -> None:
    args = parse_args()
    manifest = render_story(
        Path(args.build_manifest).expanduser().resolve(),
        Path(args.output_dir).expanduser().resolve(),
        fps=int(args.fps),
        keep_frames=not args.discard_frames,
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
