# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p3 import __mars_rover_steps_lg0_0  # noqa: E402,E501
from .freecad_live_preview_demo_p4 import __mars_rover_steps_lg0_1  # noqa: E402,E501
from .freecad_live_preview_demo_p5 import __mars_rover_steps_lg0_2  # noqa: E402,E501
# fmt: on


def __mars_rover_steps_lg0_3():
    return [
        {
            "id": "antenna-mast",
            "label": "Add high-gain antenna mast",
            "argv": [
                "-p",
                "{project_path}",
                "part",
                "add",
                "cylinder",
                "--name",
                "AntennaMast",
                "-P",
                "radius=1.2",
                "-P",
                "height=12",
                "-pos",
                "-20,0,40",
            ],
            "wait_preview": True,
        },
        {
            "id": "antenna-dish",
            "label": "Add high-gain antenna dish",
            "argv": [
                "-p",
                "{project_path}",
                "part",
                "add",
                "cylinder",
                "--name",
                "AntennaDish",
                "-P",
                "radius=7",
                "-P",
                "height=2",
                "-pos",
                "-21,0,48",
                "-rot",
                "0,90,0",
            ],
            "wait_preview": True,
        },
        {
            "id": "science-boom",
            "label": "Add science boom",
            "argv": [
                "-p",
                "{project_path}",
                "part",
                "add",
                "cylinder",
                "--name",
                "ScienceBoom",
                "-P",
                "radius=1.4",
                "-P",
                "height=24",
                "-pos",
                "16,10,30",
                "-rot",
                "0,90,0",
            ],
            "wait_preview": True,
        },
        {
            "id": "sample-head",
            "label": "Add sample head",
            "argv": [
                "-p",
                "{project_path}",
                "part",
                "add",
                "sphere",
                "--name",
                "SampleHead",
                "-P",
                "radius=4.5",
                "-pos",
                "42,10,30",
            ],
            "wait_preview": True,
        },
    ]
def _mars_rover_steps() -> List[Dict[str, Any]]:
    """Return a modular Mars rover build trajectory tuned for live preview."""
    return (__mars_rover_steps_lg0_0() + __mars_rover_steps_lg0_1() + __mars_rover_steps_lg0_2() + __mars_rover_steps_lg0_3())
