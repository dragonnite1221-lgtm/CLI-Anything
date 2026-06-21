# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p1 import COMBO_MOTION_DURATION_S, COMBO_MOTION_KEYFRAME_COUNT, FPS, SPIN_MOTION_DURATION_S, SPIN_MOTION_KEYFRAME_COUNT, TRUE_MOTION_DURATION_S, TRUE_MOTION_KEYFRAME_COUNT  # noqa: E402,E501
from .freecad_live_preview_demo_p29 import _load_motion_module, ensure_clean_dir, load_json, now_iso, run_cli, write_json  # noqa: E402,E501
from .freecad_live_preview_demo_p32 import _curiosity_showcase_project  # noqa: E402,E501
from .freecad_live_preview_demo_p33 import _apply_curiosity_true_motion_pose  # noqa: E402,E501
from .freecad_live_preview_demo_p34 import _apply_curiosity_combo_motion_pose, _apply_curiosity_spin_motion_pose  # noqa: E402,E501
# fmt: on


def generate_curiosity_true_motion_showcase(
    timeline_path: Path,
    output_dir: Path,
    *,
    fps: int = FPS,
    keep_frames: bool = True,
    motion_style: str = "drive",
) -> Dict[str, Any]:
    trajectory = load_json(timeline_path)
    if trajectory.get("scenario") != "curiosity":
        raise ValueError("True motion showcase is currently implemented for the curiosity scenario only.")
    if motion_style not in {"drive", "spin", "combo"}:
        raise ValueError("motion_style must be 'drive', 'spin', or 'combo'")

    motion_mod = _load_motion_module()
    output_dir = output_dir.expanduser().resolve()
    ensure_clean_dir(output_dir)
    stills_dir = ensure_clean_dir(output_dir / "stills")
    source_project_path = Path(trajectory["project_path"]).expanduser().resolve()
    if not source_project_path.is_file():
        raise FileNotFoundError(f"Missing Curiosity project: {source_project_path}")

    base_project = _curiosity_showcase_project(load_json(source_project_path))
    motion_project = copy.deepcopy(base_project)
    if motion_style == "drive":
        duration_s = TRUE_MOTION_DURATION_S
        keyframe_count = TRUE_MOTION_KEYFRAME_COUNT
        motion_name = "CuriosityTrueDrive"
        motion_title = "Curiosity True Motion Showcase"
        motion_subtitle = "real frame-by-frame FreeCAD motion render from the final Curiosity v6 project"
        apply_pose = _apply_curiosity_true_motion_pose
        project_stem = "curiosity_true_motion"
        video_name = "curiosity_true_motion.mp4"
    elif motion_style == "spin":
        duration_s = SPIN_MOTION_DURATION_S
        keyframe_count = SPIN_MOTION_KEYFRAME_COUNT
        motion_name = "CuriosityTurntable"
        motion_title = "Curiosity Turntable Motion"
        motion_subtitle = "real frame-by-frame FreeCAD turntable render from the final Curiosity v6 project"
        apply_pose = _apply_curiosity_spin_motion_pose
        project_stem = "curiosity_turntable_motion"
        video_name = "curiosity_turntable_motion.mp4"
    else:
        duration_s = COMBO_MOTION_DURATION_S
        keyframe_count = COMBO_MOTION_KEYFRAME_COUNT
        motion_name = "CuriosityComboShowcase"
        motion_title = "Curiosity Rotation + Drive Motion"
        motion_subtitle = "real frame-by-frame FreeCAD combo motion: one full turntable rotation followed by forward travel"
        apply_pose = _apply_curiosity_combo_motion_pose
        project_stem = "curiosity_combo_motion"
        video_name = "curiosity_combo_motion.mp4"

    motion_mod.create_motion(
        motion_project,
        name=motion_name,
        duration=duration_s,
        fps=int(fps),
        camera="hero",
        width=1600,
        height=900,
        background="White",
        fit_mode="initial",
    )
    motion_index = len(motion_project.get("motions", [])) - 1

    keyframes: List[Dict[str, Any]] = []
    for idx in range(keyframe_count):
        progress = idx / max(1, keyframe_count - 1)
        time_value = round(progress * duration_s, 4)
        posed_project = apply_pose(copy.deepcopy(base_project), progress)
        for part_index, part in enumerate(posed_project.get("parts", [])):
            placement = part.get("placement") or {}
            motion_mod.add_keyframe(
                motion_project,
                motion_index,
                target_kind="part",
                target_index=part_index,
                time_value=time_value,
                position=placement.get("position"),
                rotation=placement.get("rotation"),
            )
        keyframes.append(
            {
                "index": idx,
                "progress": round(progress, 4),
                "time": time_value,
            }
        )

    project_path = write_json(output_dir / f"{project_stem}.json", motion_project)
    frames_dir = output_dir / "frames"
    video_path = output_dir / video_name
    cli_args = [
        "-p",
        str(project_path),
        "motion",
        "render-video",
        str(motion_index),
        str(video_path),
        "--overwrite",
    ]
    if keep_frames:
        cli_args += ["--frames-dir", str(frames_dir)]
    render = run_cli(cli_args, timeout=600)
    render_payload = render.get("json") or {}

    sequence_path = Path(render_payload.get("sequence_path", "")).expanduser()
    sequence: Dict[str, Any] = {}
    if sequence_path and sequence_path.is_file():
        sequence = load_json(sequence_path)
        frames = sequence.get("frames", [])
        if frames:
            still_indices = {
                "start": 0,
                "mid": len(frames) // 2,
                "final": len(frames) - 1,
            }
            for label, frame_index in still_indices.items():
                rel_path = frames[frame_index]["path"]
                source = sequence_path.parent / rel_path
                shutil.copy2(source, stills_dir / f"{label}.png")

    manifest = {
        "protocol": "freecad-true-motion-showcase/v1",
        "created_at": now_iso(),
        "scenario": "curiosity",
        "motion_style": motion_style,
        "title": motion_title,
        "subtitle": motion_subtitle,
        "source_timeline": str(timeline_path),
        "source_project_path": str(source_project_path),
        "motion_project_path": str(project_path),
        "video_path": str(video_path),
        "frames_dir": str(frames_dir) if keep_frames else None,
        "sequence_path": render_payload.get("sequence_path"),
        "duration_s": duration_s,
        "fps": int(fps),
        "keyframe_count": keyframe_count,
        "render": render_payload,
        "sequence": sequence,
        "keyframes": keyframes,
        "notes": [
            "This sequence uses the final Curiosity v6 project as source geometry.",
            "Motion is rendered frame-by-frame through cli-anything-freecad motion render-video.",
            "No synthetic in-between frames or blend-based motion are used.",
        ],
    }
    write_json(output_dir / "motion_manifest.json", manifest)
    return manifest
