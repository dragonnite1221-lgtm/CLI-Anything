# ruff: noqa: F403, F405, E501
from .blender_orbital_relay_drone_demo_base import *  # noqa: F403
# fmt: off
from .blender_orbital_relay_drone_demo_p1 import _assign, _object_index  # noqa: E402,E501
# fmt: on


def _build_stage_05_sensor_payload(project: Dict) -> None:
    add_object(project, mesh_type="empty", name="DishPivot", location=[0.62, 0, 4.18])
    add_object(
        project,
        mesh_type="cylinder",
        name="SensorMast",
        location=[0.46, 0, 3.72],
        mesh_params={"radius": 0.06, "depth": 0.92, "vertices": 18},
    )
    add_object(
        project,
        mesh_type="cone",
        name="RadarDish",
        location=[1.12, 0, 4.18],
        rotation=[0, 90, 0],
        mesh_params={"radius1": 0.58, "radius2": 0.06, "depth": 0.42, "vertices": 36},
    )
    add_modifier(project, "bevel", _object_index(project, "RadarDish"), params={"width": 0.015, "segments": 2})
    add_object(
        project,
        mesh_type="sphere",
        name="BeaconCore",
        location=[0.1, 0, 2.92],
        scale=[0.22, 0.22, 0.22],
        mesh_params={"radius": 1.0, "segments": 24, "rings": 12},
    )
    add_modifier(project, "subdivision_surface", _object_index(project, "BeaconCore"), params={"levels": 1, "render_levels": 2})
    add_object(
        project,
        mesh_type="sphere",
        name="NavLightLeft",
        location=[-0.14, 3.28, 2.98],
        scale=[0.11, 0.11, 0.11],
        mesh_params={"radius": 1.0, "segments": 18, "rings": 10},
    )
    add_object(
        project,
        mesh_type="sphere",
        name="NavLightRight",
        location=[-0.14, -3.28, 2.98],
        scale=[0.11, 0.11, 0.11],
        mesh_params={"radius": 1.0, "segments": 18, "rings": 10},
    )
def _build_stage_06_service_rig(project: Dict) -> None:
    add_object(
        project,
        mesh_type="cylinder",
        name="ServiceArmBase",
        location=[-0.2, -0.62, 2.18],
        rotation=[90, 0, 0],
        mesh_params={"radius": 0.07, "depth": 0.46, "vertices": 16},
    )
    add_object(
        project,
        mesh_type="cylinder",
        name="ServiceArmReach",
        location=[0.42, -0.92, 2.02],
        rotation=[0, 26, 42],
        mesh_params={"radius": 0.055, "depth": 1.15, "vertices": 16},
    )
    add_object(
        project,
        mesh_type="cone",
        name="ServiceTool",
        location=[0.92, -1.34, 1.88],
        rotation=[0, -65, 42],
        mesh_params={"radius1": 0.11, "radius2": 0.02, "depth": 0.36, "vertices": 18},
    )
    add_object(
        project,
        mesh_type="cube",
        name="CommFin",
        location=[-0.96, 0, 3.62],
        scale=[0.1, 0.62, 0.34],
    )
    add_modifier(project, "bevel", _object_index(project, "CommFin"), params={"width": 0.012, "segments": 2})
def _assign_materials(project: Dict) -> None:
    for object_name in ("DeckFloor", "DisplayBase", "LaunchPad", "LiftColumn"):
        if any(obj.get("name") == object_name for obj in project["objects"]):
            _assign(project, "DeckGraphite", object_name)
    for object_name in ("PadStripeRing",):
        if any(obj.get("name") == object_name for obj in project["objects"]):
            _assign(project, "DeckStripe", object_name)

    hull_white = ("HullCore", "NoseCone", "BridgePod", "ServiceCabin", "PanelArmLeft", "PanelArmRight", "SensorMast", "RadarDish")
    for object_name in hull_white:
        if any(obj.get("name") == object_name for obj in project["objects"]):
            _assign(project, "HullWhite", object_name)

    orange_parts = ("DockRing", "CommFin", "WingSpar", "ServiceArmBase", "ServiceArmReach", "ServiceTool")
    for object_name in orange_parts:
        if any(obj.get("name") == object_name for obj in project["objects"]):
            _assign(project, "SignalOrange", object_name)

    panel_parts = ("SolarPanelLeft", "SolarPanelRight", "SolarRibLeft", "SolarRibRight")
    for object_name in panel_parts:
        if any(obj.get("name") == object_name for obj in project["objects"]):
            _assign(project, "PanelBlue", object_name)

    engine_parts = (
        "EngineBlock",
        "ThrusterTopLeft",
        "ThrusterBottomLeft",
        "ThrusterTopRight",
        "ThrusterBottomRight",
        "NozzleTopLeft",
        "NozzleBottomLeft",
        "NozzleTopRight",
        "NozzleBottomRight",
    )
    for object_name in engine_parts:
        if any(obj.get("name") == object_name for obj in project["objects"]):
            _assign(project, "EngineDark", object_name)

    glow_parts = ("BeaconCore", "NavLightLeft", "NavLightRight")
    for object_name in glow_parts:
        if any(obj.get("name") == object_name for obj in project["objects"]):
            _assign(project, "GlowCyan", object_name)
