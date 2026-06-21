# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p1 import _taipei_extend  # noqa: E402,E501
# fmt: on


def _taipei_loop(steps, z):
    for index in range(8):
        module_no = index + 1
        core_len = 24.0 - index * 1.3
        core_w = 15.0 - index * 0.5
        core_h = 8.4
        arm_w = max(5.0, core_w - 7.0)
        arm_h = 1.8
        arm_lo_len = core_len + 8.0
        arm_hi_len = core_len + 12.0

        steps.append(
            {
                "id": f"module-{module_no}",
                "label": f"Add tower module {module_no}",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "box",
                    "--name",
                    f"Core{module_no}",
                    "-P",
                    f"length={core_len:.2f}",
                    "-P",
                    f"width={core_w:.2f}",
                    "-P",
                    f"height={core_h:.2f}",
                    "-pos",
                    f"{-core_len / 2:.2f},{-core_w / 2:.2f},{z:.2f}",
                ],
                "wait_preview": True,
            }
        )
        steps.append(
            {
                "id": f"arm-low-{module_no}",
                "label": f"Add lower shoulder {module_no}",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "box",
                    "--name",
                    f"ArmLo{module_no}",
                    "-P",
                    f"length={arm_lo_len:.2f}",
                    "-P",
                    f"width={arm_w:.2f}",
                    "-P",
                    f"height={arm_h:.2f}",
                    "-pos",
                    f"{-arm_lo_len / 2:.2f},{-arm_w / 2:.2f},{z + 2.0:.2f}",
                ],
                "wait_preview": True,
            }
        )
        steps.append(
            {
                "id": f"arm-high-{module_no}",
                "label": f"Add upper shoulder {module_no}",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "box",
                    "--name",
                    f"ArmHi{module_no}",
                    "-P",
                    f"length={arm_hi_len:.2f}",
                    "-P",
                    f"width={arm_w:.2f}",
                    "-P",
                    f"height={arm_h:.2f}",
                    "-pos",
                    f"{-arm_hi_len / 2:.2f},{-arm_w / 2:.2f},{z + 5.1:.2f}",
                ],
                "wait_preview": True,
            }
        )
        z += core_h
    return z
def _taipei_101_steps() -> List[Dict[str, Any]]:
    """Return a more legible tiny Taipei 101 build trajectory."""
    steps: List[Dict[str, Any]] = [
        {
            "id": "create-project",
            "label": "Create FreeCAD project",
            "argv": ["document", "new", "--name", "Taipei101", "-o", "{project_path}"],
            "wait_preview": False,
        },
        {
            "id": "start-live-preview",
            "label": "Start poll-mode live preview",
            "argv": [
                "-p",
                "{project_path}",
                "preview",
                "live",
                "start",
                "--recipe",
                "quick",
                "--mode",
                "poll",
                "--source-poll-ms",
                "500",
                "--poll-ms",
                "700",
                "--root-dir",
                "{live_root}",
            ],
            "wait_preview": True,
            "manual_session_payload": True,
        },
        {
            "id": "podium",
            "label": "Add podium",
            "argv": [
                "-p",
                "{project_path}",
                "part",
                "add",
                "box",
                "--name",
                "Podium",
                "-P",
                "length=58",
                "-P",
                "width=46",
                "-P",
                "height=16",
                "-pos",
                "-29,-23,0",
            ],
            "wait_preview": True,
        },
    ]

    z = 16.0
    z = _taipei_loop(steps, z)

    _taipei_extend(steps, z)
    return steps
