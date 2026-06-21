# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p24 import _mod_cg3_0  # noqa: E402,E501
from .freecad_live_preview_demo_p25 import _mod_cg4_0  # noqa: E402,E501
# fmt: on


def _mod_cg4_1():
    return [
        {
                "id": "port-wing",
                "label": "Add port wing",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "box",
                    "--name",
                    "PortWing",
                    "-P",
                    "length=18",
                    "-P",
                    "width=28",
                    "-P",
                    "height=5",
                    "-pos",
                    "-28,0,14",
                ],
                "wait_preview": True,
            },
        {
                "id": "starboard-wing",
                "label": "Add starboard wing",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "box",
                    "--name",
                    "StarboardWing",
                    "-P",
                    "length=18",
                    "-P",
                    "width=28",
                    "-P",
                    "height=5",
                    "-pos",
                    "28,0,14",
                ],
                "wait_preview": True,
            },
        {
                "id": "beacon-cone",
                "label": "Add beacon cone",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "cone",
                    "--name",
                    "BeaconCone",
                    "-P",
                    "radius1=10",
                    "-P",
                    "radius2=3",
                    "-P",
                    "height=16",
                    "-pos",
                    "0,18,8",
                ],
                "wait_preview": True,
            },
        {
                "id": "antenna",
                "label": "Add antenna mast",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "cylinder",
                    "--name",
                    "AntennaMast",
                    "-P",
                    "radius=2",
                    "-P",
                    "height=18",
                    "-pos",
                    "0,0,48",
                ],
                "wait_preview": True,
            },
        {
                "id": "halo-ring",
                "label": "Add halo ring",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "torus",
                    "--name",
                    "HaloRing",
                    "-P",
                    "radius1=20",
                    "-P",
                    "radius2=2.5",
                    "-pos",
                    "0,0,28",
                ],
                "wait_preview": True,
            },
    ]
def _mod_cg3_1():
    return {
        "steps": (_mod_cg4_0() + _mod_cg4_1()),
    }
def _mod_cg0_1():
    return {
        "orbital-relay": {**_mod_cg3_0(), **_mod_cg3_1()},
    }
def _mod_cg1_0():
    return {
        "title": "Empire State Building",
        "subtitle": "tiny iconic skyscraper model built with cli-anything-freecad",
        "project_name": "EmpireStateBuilding",
        "project_file": "empire_state_building.json",
    }
