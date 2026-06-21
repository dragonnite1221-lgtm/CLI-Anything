# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p6 import _mars_rover_steps  # noqa: E402,E501
from .freecad_live_preview_demo_p7 import __curiosity_steps_lg0_0  # noqa: E402,E501
from .freecad_live_preview_demo_p8 import __curiosity_steps_lg0_1  # noqa: E402,E501
from .freecad_live_preview_demo_p9 import __curiosity_steps_lg0_2  # noqa: E402,E501
from .freecad_live_preview_demo_p10 import __curiosity_steps_lg0_3  # noqa: E402,E501
from .freecad_live_preview_demo_p11 import __curiosity_steps_lg0_4  # noqa: E402,E501
from .freecad_live_preview_demo_p12 import __curiosity_steps_lg0_5  # noqa: E402,E501
from .freecad_live_preview_demo_p13 import __curiosity_steps_lg0_6  # noqa: E402,E501
from .freecad_live_preview_demo_p14 import __curiosity_steps_lg0_7  # noqa: E402,E501
from .freecad_live_preview_demo_p15 import __curiosity_steps_lg0_8  # noqa: E402,E501
from .freecad_live_preview_demo_p16 import __curiosity_steps_lg0_9  # noqa: E402,E501
from .freecad_live_preview_demo_p17 import __curiosity_steps_lg0_10  # noqa: E402,E501
from .freecad_live_preview_demo_p18 import __curiosity_steps_lg0_11  # noqa: E402,E501
from .freecad_live_preview_demo_p19 import __curiosity_steps_lg0_12  # noqa: E402,E501
from .freecad_live_preview_demo_p20 import __curiosity_steps_lg0_13  # noqa: E402,E501
from .freecad_live_preview_demo_p21 import __curiosity_steps_lg0_14  # noqa: E402,E501
from .freecad_live_preview_demo_p22 import __curiosity_steps_lg0_15  # noqa: E402,E501
from .freecad_live_preview_demo_p23 import __curiosity_steps_lg0_16  # noqa: E402,E501
# fmt: on


def __curiosity_steps_lg0_17():
    return [
        {
            "id": "align-arm-fore",
            "label": "Attach forearm",
            "argv": [
                "-p",
                "{project_path}",
                "part",
                "align",
                "41",
                "40",
                "--x",
                "min",
                "--to-x",
                "max",
                "--dx",
                "-1.5",
                "--y",
                "center",
                "--to-y",
                "center",
                "--z",
                "center",
                "--to-z",
                "center",
                "--dz",
                "-2.5",
            ],
            "wait_preview": True,
        },
        {
            "id": "align-turret",
            "label": "Attach tool turret",
            "argv": [
                "-p",
                "{project_path}",
                "part",
                "align",
                "42",
                "41",
                "--x",
                "min",
                "--to-x",
                "max",
                "--dx",
                "-0.5",
                "--y",
                "center",
                "--to-y",
                "center",
                "--z",
                "center",
                "--to-z",
                "center",
                "--dz",
                "-1.5",
            ],
            "wait_preview": True,
        },
        {
            "id": "align-sensor-pack",
            "label": "Seat sensor pack on deck",
            "argv": [
                "-p",
                "{project_path}",
                "part",
                "align",
                "43",
                "1",
                "--x",
                "center",
                "--to-x",
                "center",
                "--dx",
                "-7.0",
                "--y",
                "center",
                "--to-y",
                "center",
                "--z",
                "min",
                "--to-z",
                "max",
            ],
            "wait_preview": True,
        },
    ]
def _curiosity_steps() -> List[Dict[str, Any]]:
    """Return a higher-fidelity tiny Curiosity rover build trajectory."""
    return (__curiosity_steps_lg0_0() + __curiosity_steps_lg0_1() + __curiosity_steps_lg0_2() + __curiosity_steps_lg0_3() + __curiosity_steps_lg0_4() + __curiosity_steps_lg0_5() + __curiosity_steps_lg0_6() + __curiosity_steps_lg0_7() + __curiosity_steps_lg0_8() + __curiosity_steps_lg0_9() + __curiosity_steps_lg0_10() + __curiosity_steps_lg0_11() + __curiosity_steps_lg0_12() + __curiosity_steps_lg0_13() + __curiosity_steps_lg0_14() + __curiosity_steps_lg0_15() + __curiosity_steps_lg0_16() + __curiosity_steps_lg0_17())
def _mod_cg0_0():
    return {
        "curiosity": {
        "title": "Curiosity",
        "subtitle": "high-fidelity tiny Curiosity rover built with cli-anything-freecad and live preview",
        "project_name": "Curiosity",
        "project_file": "curiosity.json",
        "steps": _curiosity_steps(),
    },
        "mars-rover": {
        "title": "Mars Rover",
        "subtitle": "modular six-wheel rover built with cli-anything-freecad and live preview",
        "project_name": "MarsRover",
        "project_file": "mars_rover.json",
        "steps": _mars_rover_steps(),
    },
    }
def _mod_cg3_0():
    return {
        "title": "Orbital Relay",
        "subtitle": "fictional sci-fi station built with FreeCAD primitives",
        "project_name": "OrbitalRelay",
        "project_file": "orbital_relay.json",
    }
