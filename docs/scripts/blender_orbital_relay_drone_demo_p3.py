# ruff: noqa: F403, F405, E501
from .blender_orbital_relay_drone_demo_base import *  # noqa: F403
# fmt: off
from .blender_orbital_relay_drone_demo_p1 import _object_index  # noqa: E402,E501
# fmt: on


def _build_stage_03_solar_arrays(project: Dict) -> None:
    add_object(
        project,
        mesh_type="cube",
        name="SolarPanelLeft",
        location=[-0.56, 2.26, 2.92],
        rotation=[0, 0, 16],
        scale=[1.22, 0.04, 0.68],
    )
    add_modifier(project, "bevel", _object_index(project, "SolarPanelLeft"), params={"width": 0.02, "segments": 2})
    add_object(
        project,
        mesh_type="cube",
        name="SolarPanelRight",
        location=[-0.56, -2.26, 2.92],
        rotation=[0, 0, -16],
        scale=[1.22, 0.04, 0.68],
    )
    add_modifier(project, "bevel", _object_index(project, "SolarPanelRight"), params={"width": 0.02, "segments": 2})
    add_object(
        project,
        mesh_type="cube",
        name="SolarRibLeft",
        location=[-1.52, 2.3, 2.92],
        rotation=[0, 0, 16],
        scale=[0.06, 0.012, 0.58],
    )
    add_modifier(
        project,
        "array",
        _object_index(project, "SolarRibLeft"),
        params={"count": 7, "relative_offset_x": 1.95, "relative_offset_y": 0.0, "relative_offset_z": 0.0},
    )
    add_object(
        project,
        mesh_type="cube",
        name="SolarRibRight",
        location=[-1.52, -2.3, 2.92],
        rotation=[0, 0, -16],
        scale=[0.06, 0.012, 0.58],
    )
    add_modifier(
        project,
        "array",
        _object_index(project, "SolarRibRight"),
        params={"count": 7, "relative_offset_x": 1.95, "relative_offset_y": 0.0, "relative_offset_z": 0.0},
    )
def _build_stage_04_propulsion(project: Dict) -> None:
    add_object(
        project,
        mesh_type="cube",
        name="EngineBlock",
        location=[-1.92, 0, 2.72],
        scale=[0.54, 0.68, 0.52],
    )
    add_modifier(project, "bevel", _object_index(project, "EngineBlock"), params={"width": 0.03, "segments": 2})

    thrusters = [
        ("ThrusterTopLeft", [-2.45, 0.34, 2.98]),
        ("ThrusterBottomLeft", [-2.45, 0.34, 2.36]),
        ("ThrusterTopRight", [-2.45, -0.34, 2.98]),
        ("ThrusterBottomRight", [-2.45, -0.34, 2.36]),
    ]
    for name, location in thrusters:
        add_object(
            project,
            mesh_type="cylinder",
            name=name,
            location=location,
            rotation=[0, 90, 0],
            mesh_params={"radius": 0.16, "depth": 0.28, "vertices": 28},
        )
    nozzles = [
        ("NozzleTopLeft", [-2.76, 0.34, 2.98]),
        ("NozzleBottomLeft", [-2.76, 0.34, 2.36]),
        ("NozzleTopRight", [-2.76, -0.34, 2.98]),
        ("NozzleBottomRight", [-2.76, -0.34, 2.36]),
    ]
    for name, location in nozzles:
        add_object(
            project,
            mesh_type="cone",
            name=name,
            location=location,
            rotation=[0, 90, 0],
            mesh_params={"radius1": 0.24, "radius2": 0.08, "depth": 0.42, "vertices": 24},
        )
