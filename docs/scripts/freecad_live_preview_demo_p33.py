# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p1 import SHOWCASE_DURATION_S, SHOWCASE_FRAME_COUNT, SHOWCASE_HOLD_S  # noqa: E402,E501
from .freecad_live_preview_demo_p29 import ensure_clean_dir, load_json, now_iso, run_cli, write_json  # noqa: E402,E501
from .freecad_live_preview_demo_p32 import _apply_curiosity_showcase_pose, _curiosity_showcase_project  # noqa: E402,E501
# fmt: on


def generate_curiosity_showcase_sequence(trajectory: Dict[str, Any], run_dir: Path) -> Optional[Dict[str, Any]]:
    if trajectory.get("scenario") != "curiosity":
        return None

    showcase_dir = run_dir / "showcase"
    manifest_path = showcase_dir / "sequence.json"
    if manifest_path.is_file():
        cached = load_json(manifest_path)
        frames = cached.get("frames") or []
        if frames and all(Path(frame.get("hero_path", "")).is_file() for frame in frames):
            return cached

    source_project_path = Path(trajectory["project_path"]).expanduser().resolve()
    if not source_project_path.is_file():
        return None

    ensure_clean_dir(showcase_dir)
    projects_dir = ensure_clean_dir(showcase_dir / "projects")
    captures_root = ensure_clean_dir(showcase_dir / "captures")

    base_project = _curiosity_showcase_project(load_json(source_project_path))
    write_json(projects_dir / "showcase_base.json", base_project)

    frames: List[Dict[str, Any]] = []
    for idx in range(SHOWCASE_FRAME_COUNT):
        progress = idx / max(1, SHOWCASE_FRAME_COUNT - 1)
        posed_project = _apply_curiosity_showcase_pose(copy.deepcopy(base_project), progress)
        posed_path = write_json(projects_dir / f"pose_{idx:02d}.json", posed_project)
        capture = run_cli(
            ["-p", str(posed_path), "preview", "capture", "--root-dir", str(captures_root)],
            timeout=180,
        )
        payload = capture.get("json") or {}
        bundle_dir = Path(payload.get("_bundle_dir", "")).expanduser()
        hero_path = bundle_dir / "artifacts" / "hero.png"
        if not hero_path.is_file():
            raise RuntimeError(f"Missing hero artifact for showcase frame {idx}: {bundle_dir}")
        frames.append(
            {
                "index": idx,
                "progress": round(progress, 4),
                "project_path": str(posed_path),
                "bundle_dir": str(bundle_dir),
                "hero_path": str(hero_path),
                "capture_cmd": capture["display_cmd"],
            }
        )

    manifest = {
        "protocol": "freecad-showcase-sequence/v1",
        "created_at": now_iso(),
        "scenario": "curiosity",
        "title": "Curiosity Showcase Drive",
        "subtitle": "real extra FreeCAD hero captures generated from the final Curiosity v6 project",
        "source_timeline": str(run_dir / "trajectory.json"),
        "source_project_path": str(source_project_path),
        "duration_s": SHOWCASE_DURATION_S,
        "hold_s": SHOWCASE_HOLD_S,
        "frames": frames,
        "notes": [
            "The ending showcase uses real preview captures from the final Curiosity v6 project.",
            "A staged ground and marker bed are added as extra geometry so whole-rover translation reads visually in hero view.",
            "No GUI screen recording or synthetic CAD viewport frames are used.",
        ],
    }
    write_json(manifest_path, manifest)
    return manifest
def _apply_curiosity_true_motion_pose(project: Dict[str, Any], progress: float) -> Dict[str, Any]:
    drive_x = -46.0 + 96.0 * progress
    drive_y = -10.0 + 15.0 * progress + 2.2 * math.sin(progress * math.pi * 1.2)
    bump_a = math.exp(-((progress - 0.28) ** 2) / (2 * 0.11 ** 2))
    bump_b = math.exp(-((progress - 0.71) ** 2) / (2 * 0.10 ** 2))
    body_heave = 1.15 + 0.45 * math.sin(progress * math.tau) + 0.85 * bump_a + 0.65 * bump_b
    arm_sway = 0.9 * math.sin(progress * math.tau)
    mast_sway = 0.45 * math.cos(progress * math.pi)
    dish_sway = 0.65 * math.cos(progress * math.tau)

    for part in project.get("parts", []):
        name = str(part.get("name", ""))
        if name.startswith("Showcase"):
            continue
        placement = part.setdefault("placement", {})
        position = placement.setdefault("position", [0.0, 0.0, 0.0])
        while len(position) < 3:
            position.append(0.0)

        position[0] = float(position[0]) + drive_x
        position[1] = float(position[1]) + drive_y
        position[2] = float(position[2]) + body_heave

        if name in {"ArmFore", "ToolTurret"}:
            position[1] += arm_sway
            position[2] += 0.35 * arm_sway
        elif name in {"ArmUpper", "ArmShoulder"}:
            position[1] += 0.35 * arm_sway
        elif name in {"HGADish", "HGAStem"}:
            position[1] += dish_sway
            position[2] += 0.18 * dish_sway
        elif name in {"MastColumn", "CameraBridge", "LeftCameraPod", "RightCameraPod", "ChemCamBarrel"}:
            position[1] += mast_sway
            position[2] += 0.12 * mast_sway
    return project
def _curiosity_motion_pivot(project: Dict[str, Any]) -> List[float]:
    xs: List[float] = []
    ys: List[float] = []
    zs: List[float] = []
    for part in project.get("parts", []):
        name = str(part.get("name", ""))
        if name.startswith("Showcase"):
            continue
        placement = part.get("placement") or {}
        position = placement.get("position") or [0.0, 0.0, 0.0]
        if len(position) >= 3:
            xs.append(float(position[0]))
            ys.append(float(position[1]))
            zs.append(float(position[2]))
    if not xs:
        return [0.0, 0.0, 0.0]
    return [
        (min(xs) + max(xs)) / 2.0,
        (min(ys) + max(ys)) / 2.0,
        (min(zs) + max(zs)) / 2.0,
    ]
def _rotate_xy(x: float, y: float, cx: float, cy: float, angle_deg: float) -> List[float]:
    angle = math.radians(angle_deg)
    dx = x - cx
    dy = y - cy
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return [
        cx + dx * cos_a - dy * sin_a,
        cy + dx * sin_a + dy * cos_a,
    ]
