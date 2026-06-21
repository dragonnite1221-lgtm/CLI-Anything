# ruff: noqa: F403, F405, E501
from .blender_orbital_relay_drone_demo_base import *  # noqa: F403
# fmt: off
from .blender_orbital_relay_drone_demo_p1 import _object_index  # noqa: E402,E501
# fmt: on


def _build_stage_00_launch_platform(project: Dict) -> None:
    add_object(project, mesh_type="plane", name="DeckFloor", mesh_params={"size": 22.0}, location=[0, 0, 0])
    add_object(
        project,
        mesh_type="cylinder",
        name="DisplayBase",
        location=[0, 0, 0.22],
        mesh_params={"radius": 3.2, "depth": 0.44, "vertices": 56},
    )
    add_modifier(project, "bevel", _object_index(project, "DisplayBase"), params={"width": 0.06, "segments": 2})
    add_object(
        project,
        mesh_type="cylinder",
        name="LaunchPad",
        location=[0, 0, 0.5],
        mesh_params={"radius": 2.08, "depth": 0.16, "vertices": 56},
    )
    add_modifier(project, "bevel", _object_index(project, "LaunchPad"), params={"width": 0.025, "segments": 2})
    add_object(
        project,
        mesh_type="torus",
        name="PadStripeRing",
        location=[0, 0, 0.59],
        rotation=[90, 0, 0],
        mesh_params={"major_radius": 1.62, "minor_radius": 0.032, "major_segments": 64, "minor_segments": 12},
    )
    add_object(
        project,
        mesh_type="cylinder",
        name="LiftColumn",
        location=[0, 0, 1.32],
        mesh_params={"radius": 0.18, "depth": 1.42, "vertices": 32},
    )
    add_modifier(project, "bevel", _object_index(project, "LiftColumn"), params={"width": 0.02, "segments": 2})
def _build_stage_01_hull_blockout(project: Dict) -> None:
    add_object(project, mesh_type="empty", name="DroneRoot", location=[0, 0, 0], rotation=[0, 0, 18])
    add_object(
        project,
        mesh_type="cylinder",
        name="HullCore",
        location=[0.12, 0, 2.82],
        rotation=[0, 90, 0],
        mesh_params={"radius": 0.58, "depth": 3.4, "vertices": 40},
    )
    add_modifier(project, "bevel", _object_index(project, "HullCore"), params={"width": 0.04, "segments": 2})
    add_object(
        project,
        mesh_type="cone",
        name="NoseCone",
        location=[2.04, 0, 2.82],
        rotation=[0, 90, 0],
        mesh_params={"radius1": 0.58, "radius2": 0.08, "depth": 1.05, "vertices": 40},
    )
    add_modifier(project, "bevel", _object_index(project, "NoseCone"), params={"width": 0.018, "segments": 2})
    add_object(
        project,
        mesh_type="sphere",
        name="BridgePod",
        location=[1.26, 0, 3.2],
        scale=[0.66, 0.48, 0.38],
        mesh_params={"radius": 1.0, "segments": 28, "rings": 16},
    )
    add_modifier(project, "subdivision_surface", _object_index(project, "BridgePod"), params={"levels": 2, "render_levels": 2})
    add_object(
        project,
        mesh_type="torus",
        name="DockRing",
        location=[2.54, 0, 2.82],
        rotation=[0, 90, 0],
        mesh_params={"major_radius": 0.54, "minor_radius": 0.07, "major_segments": 56, "minor_segments": 14},
    )
    add_object(
        project,
        mesh_type="cube",
        name="ServiceCabin",
        location=[0.08, 0, 3.44],
        scale=[0.56, 0.42, 0.3],
    )
    add_modifier(project, "bevel", _object_index(project, "ServiceCabin"), params={"width": 0.03, "segments": 2})
def _build_stage_02_wing_structure(project: Dict) -> None:
    add_object(
        project,
        mesh_type="cube",
        name="WingSpar",
        location=[-0.28, 0, 2.8],
        scale=[0.16, 1.24, 0.1],
    )
    add_modifier(project, "bevel", _object_index(project, "WingSpar"), params={"width": 0.015, "segments": 2})
    add_object(
        project,
        mesh_type="cube",
        name="PanelArmLeft",
        location=[-0.08, 1.08, 2.84],
        rotation=[0, 0, 18],
        scale=[0.56, 0.08, 0.06],
    )
    add_object(
        project,
        mesh_type="cube",
        name="PanelArmRight",
        location=[-0.08, -1.08, 2.84],
        rotation=[0, 0, -18],
        scale=[0.56, 0.08, 0.06],
    )
