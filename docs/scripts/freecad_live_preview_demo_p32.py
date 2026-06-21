# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403


def fit_image(img: Image.Image, box: tuple[int, int], *, background: str) -> Image.Image:
    target_w, target_h = box
    canvas = Image.new("RGB", (target_w, target_h), background)
    src = img.convert("RGB")
    scale = min(target_w / src.width, target_h / src.height)
    new_size = (max(1, int(src.width * scale)), max(1, int(src.height * scale)))
    resized = src.resize(new_size, Image.Resampling.LANCZOS)
    x = (target_w - resized.width) // 2
    y = (target_h - resized.height) // 2
    canvas.paste(resized, (x, y))
    return canvas
def _make_box_part(
    *,
    part_id: int,
    name: str,
    length: float,
    width: float,
    height: float,
    position: List[float],
) -> Dict[str, Any]:
    return {
        "id": part_id,
        "name": name,
        "type": "box",
        "params": {
            "length": float(length),
            "width": float(width),
            "height": float(height),
        },
        "placement": {
            "position": [float(v) for v in position],
            "rotation": [0.0, 0.0, 0.0],
        },
        "material_index": None,
        "visible": True,
    }
def _curiosity_showcase_project(base_project: Dict[str, Any]) -> Dict[str, Any]:
    project = copy.deepcopy(base_project)
    parts = [part for part in project.get("parts", []) if not str(part.get("name", "")).startswith("Showcase")]
    next_id = max((int(part.get("id", 0)) for part in parts), default=0) + 1
    extras = [
        _make_box_part(
            part_id=next_id,
            name="ShowcaseGround",
            length=184.0,
            width=96.0,
            height=4.0,
            position=[-72.0, -48.0, -4.0],
        ),
        _make_box_part(
            part_id=next_id + 1,
            name="ShowcaseMarkerA",
            length=12.0,
            width=8.0,
            height=2.0,
            position=[-18.0, -10.0, 0.0],
        ),
        _make_box_part(
            part_id=next_id + 2,
            name="ShowcaseMarkerB",
            length=16.0,
            width=10.0,
            height=3.0,
            position=[24.0, 10.0, 0.0],
        ),
        _make_box_part(
            part_id=next_id + 3,
            name="ShowcaseMarkerC",
            length=18.0,
            width=8.0,
            height=2.0,
            position=[58.0, -4.0, 0.0],
        ),
    ]
    project["parts"] = parts + extras
    return project
def _apply_curiosity_showcase_pose(project: Dict[str, Any], progress: float) -> Dict[str, Any]:
    rover_shift_x = -38.0 + 78.0 * progress
    rover_shift_y = -7.0 + 11.0 * progress
    bump_a = math.exp(-((progress - 0.32) ** 2) / (2 * 0.12 ** 2))
    bump_b = math.exp(-((progress - 0.74) ** 2) / (2 * 0.10 ** 2))
    rover_shift_z = 1.2 + 0.55 * math.sin(progress * math.tau) + 0.85 * bump_a + 0.65 * bump_b
    arm_sway = 0.75 * math.sin(progress * math.tau)
    mast_sway = 0.35 * math.cos(progress * math.pi)
    dish_sway = 0.55 * math.cos(progress * math.tau)

    for part in project.get("parts", []):
        name = str(part.get("name", ""))
        if name.startswith("Showcase"):
            continue
        placement = part.setdefault("placement", {})
        position = placement.setdefault("position", [0.0, 0.0, 0.0])
        while len(position) < 3:
            position.append(0.0)
        position[0] = float(position[0]) + rover_shift_x
        position[1] = float(position[1]) + rover_shift_y
        position[2] = float(position[2]) + rover_shift_z

        if name in {"ArmFore", "ToolTurret"}:
            position[1] += arm_sway
            position[2] += 0.35 * arm_sway
        elif name in {"ArmUpper", "ArmShoulder"}:
            position[1] += 0.35 * arm_sway
        elif name in {"HGADish", "HGAStem"}:
            position[1] += dish_sway
        elif name in {"MastColumn", "CameraBridge", "LeftCameraPod", "RightCameraPod", "ChemCamBarrel"}:
            position[1] += mast_sway
    return project
