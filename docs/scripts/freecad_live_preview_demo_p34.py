# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p33 import _curiosity_motion_pivot, _rotate_xy  # noqa: E402,E501
# fmt: on


def _apply_curiosity_spin_motion_pose(project: Dict[str, Any], progress: float) -> Dict[str, Any]:
    pivot = _curiosity_motion_pivot(project)
    target_center_x = 10.0
    target_center_y = 0.0
    shift_x = target_center_x - pivot[0]
    shift_y = target_center_y - pivot[1]
    spin_deg = -20.0 + 380.0 * progress
    body_heave = 1.05 + 0.25 * math.sin(progress * math.tau * 2.0)
    mast_sway = 0.35 * math.cos(progress * math.tau)
    arm_sway = 0.75 * math.sin(progress * math.tau * 1.5)
    dish_sway = 0.45 * math.sin(progress * math.tau + math.pi / 6.0)

    for part in project.get("parts", []):
        name = str(part.get("name", ""))
        if name.startswith("Showcase"):
            continue
        placement = part.setdefault("placement", {})
        position = placement.setdefault("position", [0.0, 0.0, 0.0])
        rotation = placement.setdefault("rotation", [0.0, 0.0, 0.0])
        while len(position) < 3:
            position.append(0.0)
        while len(rotation) < 3:
            rotation.append(0.0)

        base_x = float(position[0]) + shift_x
        base_y = float(position[1]) + shift_y
        rotated_x, rotated_y = _rotate_xy(base_x, base_y, target_center_x, target_center_y, spin_deg)
        position[0] = rotated_x
        position[1] = rotated_y
        position[2] = float(position[2]) + body_heave

        rotation[2] = float(rotation[2]) + spin_deg

        if name in {"ArmFore", "ToolTurret"}:
            position[1] += 0.6 * arm_sway
            position[2] += 0.25 * arm_sway
        elif name in {"ArmUpper", "ArmShoulder"}:
            position[1] += 0.3 * arm_sway
        elif name in {"HGADish", "HGAStem"}:
            position[1] += 0.35 * dish_sway
            position[2] += 0.12 * dish_sway
        elif name in {"MastColumn", "CameraBridge", "LeftCameraPod", "RightCameraPod", "ChemCamBarrel"}:
            position[1] += 0.3 * mast_sway
            position[2] += 0.10 * mast_sway
    return project
def _apply_curiosity_combo_motion_pose(project: Dict[str, Any], progress: float) -> Dict[str, Any]:
    pivot = _curiosity_motion_pivot(project)
    target_center_x = 10.0
    target_center_y = 0.0
    shift_x = target_center_x - pivot[0]
    shift_y = target_center_y - pivot[1]

    spin_phase = min(1.0, progress / 0.56)
    drive_phase = 0.0 if progress <= 0.56 else min(1.0, (progress - 0.56) / 0.44)
    spin_deg = -18.0 + 360.0 * spin_phase
    drive_ease = 1.0 - pow(1.0 - drive_phase, 2.2)
    drive_dx = 28.0 * drive_ease
    drive_dy = -11.0 * drive_ease
    body_heave = 0.95 + 0.18 * math.sin(progress * math.tau * 2.5)
    mast_sway = 0.25 * math.cos(progress * math.tau * 1.25)
    arm_sway = 0.42 * math.sin(progress * math.tau * 1.7)
    dish_sway = 0.24 * math.sin(progress * math.tau + math.pi / 5.0)

    for part in project.get("parts", []):
        name = str(part.get("name", ""))
        if name.startswith("Showcase"):
            continue
        placement = part.setdefault("placement", {})
        position = placement.setdefault("position", [0.0, 0.0, 0.0])
        rotation = placement.setdefault("rotation", [0.0, 0.0, 0.0])
        while len(position) < 3:
            position.append(0.0)
        while len(rotation) < 3:
            rotation.append(0.0)

        base_x = float(position[0]) + shift_x
        base_y = float(position[1]) + shift_y
        rotated_x, rotated_y = _rotate_xy(base_x, base_y, target_center_x, target_center_y, spin_deg)
        position[0] = rotated_x + drive_dx
        position[1] = rotated_y + drive_dy
        position[2] = float(position[2]) + body_heave

        rotation[2] = float(rotation[2]) + spin_deg

        if name in {"ArmFore", "ToolTurret"}:
            position[1] += 0.35 * arm_sway
            position[2] += 0.20 * arm_sway
        elif name in {"ArmUpper", "ArmShoulder"}:
            position[1] += 0.18 * arm_sway
        elif name in {"HGADish", "HGAStem"}:
            position[1] += 0.18 * dish_sway
            position[2] += 0.10 * dish_sway
        elif name in {"MastColumn", "CameraBridge", "LeftCameraPod", "RightCameraPod", "ChemCamBarrel"}:
            position[1] += 0.18 * mast_sway
            position[2] += 0.08 * mast_sway
    return project
