# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p1 import DISPLAY_FONT_PATH, FPS, HOLD_TAIL_S, LEFT_W, MONO_BOLD_FONT_PATH, MONO_FONT_PATH, SANS_FONT_PATH, SHOWCASE_DURATION_S, VIDEO_H, VIDEO_W  # noqa: E402,E501
from .freecad_live_preview_demo_p29 import ensure_clean_dir, load_json  # noqa: E402,E501
from .freecad_live_preview_demo_p31 import collect_demo  # noqa: E402,E501
from .freecad_live_preview_demo_p33 import generate_curiosity_showcase_sequence  # noqa: E402,E501
from .freecad_live_preview_demo_p35 import generate_curiosity_true_motion_showcase  # noqa: E402,E501
from .freecad_live_preview_demo_p36 import _draw_text_right, _trim_middle, load_font  # noqa: E402,E501
from .freecad_live_preview_demo_p37 import build_static_backdrop  # noqa: E402,E501
from .freecad_live_preview_demo_p38 import draw_global_header  # noqa: E402,E501
from .freecad_live_preview_demo_p39 import draw_terminal_panel  # noqa: E402,E501
from .freecad_live_preview_demo_p40 import compose_showcase_frame, parse_args  # noqa: E402,E501
from .freecad_live_preview_demo_p41 import draw_preview_panel  # noqa: E402,E501
# fmt: on


def render_video(timeline_path: Path, *, output_path: Optional[Path] = None, fps: int = FPS, speed: float = 1.0, keep_frames: bool = True) -> Path:
    trajectory = load_json(timeline_path)
    run_dir = timeline_path.parent
    output_file = output_path or (run_dir / "demo.mp4")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    frames_dir = run_dir / "frames"
    ensure_clean_dir(frames_dir)

    fonts = {
        "display": load_font(DISPLAY_FONT_PATH, 38),
        "title": load_font(DISPLAY_FONT_PATH, 24),
        "body": load_font(SANS_FONT_PATH, 17),
        "small": load_font(SANS_FONT_PATH, 13),
        "mono": load_font(MONO_FONT_PATH, 15),
        "mono_small": load_font(MONO_BOLD_FONT_PATH, 12),
    }
    backdrop = build_static_backdrop()
    if trajectory.get("scenario") == "curiosity":
        showcase = generate_curiosity_true_motion_showcase(
            timeline_path,
            run_dir / "showcase-motion",
            fps=fps,
            keep_frames=True,
            motion_style="combo",
        )
    else:
        showcase = generate_curiosity_showcase_sequence(trajectory, run_dir)
    showcase_cache: Dict[int, Image.Image] = {}

    last_t = 0.0
    if trajectory["commands"]:
        last_t = max(last_t, max(cmd["timeline_end_s"] for cmd in trajectory["commands"]))
    if trajectory["preview_events"]:
        last_t = max(last_t, max(event["timeline_ready_s"] for event in trajectory["preview_events"]))
    main_duration_s = (last_t + HOLD_TAIL_S) / max(speed, 0.01)
    showcase_duration_s = float(showcase.get("duration_s", SHOWCASE_DURATION_S)) if showcase else 0.0
    duration_s = main_duration_s + showcase_duration_s
    frame_count = int(math.ceil(duration_s * fps))

    for frame_idx in range(frame_count):
        t_display = frame_idx / fps
        if showcase and t_display >= main_duration_s:
            showcase_t = t_display - main_duration_s
            image = compose_showcase_frame(
                trajectory,
                showcase,
                showcase_t,
                last_t + HOLD_TAIL_S,
                fonts,
                backdrop,
                showcase_cache,
            )
            footer_left = "REAL CLI trajectory · REAL live preview bundles · REAL FreeCAD motion ending"
        else:
            t_real = t_display * speed
            image = backdrop.copy()
            draw_global_header(image, trajectory, t_real, fonts)
            draw_terminal_panel(image, (26, 116, LEFT_W - 14, VIDEO_H - 34), trajectory, t_real, fonts)
            draw_preview_panel(image, (LEFT_W + 10, 116, VIDEO_W - 26, VIDEO_H - 34), trajectory, t_real, fonts)
            footer_left = "REAL CLI trajectory · REAL live preview bundles · programmatic composition"

        draw = ImageDraw.Draw(image)
        footer_right = _trim_middle(str(timeline_path), 56)
        draw.text((34, VIDEO_H - 26), footer_left, fill="#7891ab", font=fonts["small"])
        _draw_text_right(draw, VIDEO_W - 34, VIDEO_H - 26, footer_right, font=fonts["mono_small"], fill="#7891ab")

        image.convert("RGB").save(frames_dir / f"frame_{frame_idx:05d}.png")

    ffmpeg_cmd = [
        shutil.which("ffmpeg") or "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(frames_dir / "frame_%05d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_file),
    ]
    subprocess.run(ffmpeg_cmd, cwd=run_dir, capture_output=True, text=True, timeout=600, check=True)

    if not keep_frames:
        shutil.rmtree(frames_dir)
    return output_file
def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if args.mode == "collect":
        timeline = collect_demo(output_dir, args.scenario)
        print(timeline)
        return 0

    if args.mode == "render":
        if not args.timeline:
            raise SystemExit("--timeline is required for render mode")
        output_path = render_video(
            Path(args.timeline).expanduser().resolve(),
            fps=args.fps,
            speed=args.speed,
            keep_frames=not args.no_frames,
        )
        print(output_path)
        return 0

    if args.mode == "motion-showcase":
        if not args.timeline:
            raise SystemExit("--timeline is required for motion-showcase mode")
        manifest = generate_curiosity_true_motion_showcase(
            Path(args.timeline).expanduser().resolve(),
            output_dir,
            fps=args.fps,
            keep_frames=not args.no_frames,
            motion_style=args.motion_style,
        )
        print(json.dumps(manifest, indent=2))
        return 0

    timeline = collect_demo(output_dir, args.scenario)
    output_path = render_video(
        timeline,
        fps=args.fps,
        speed=args.speed,
        keep_frames=not args.no_frames,
    )
    print(json.dumps({"timeline": str(timeline), "video": str(output_path)}, indent=2))
    return 0
