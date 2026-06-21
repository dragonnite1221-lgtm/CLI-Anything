# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p1 import _COMPONENT_PRESETS_PART0  # noqa: E402,E501
# fmt: on


_COMPONENT_PRESETS_PART1 = {
    "text_renderer": {
        "__type": "Sandbox.TextRenderer",
        "Text": "Hello World",
        "FontSize": 64,
        "Color": "1,1,1,1",
    },
    "line_renderer": {
        "__type": "Sandbox.LineRenderer",
        "Color": "1,1,1,1",
        "Opaque": True,
        "Width": 2,
    },
    "decal_renderer": {
        "__type": "Sandbox.DecalRenderer",
        "Material": "materials/default.vmat",
        "Size": "128,128,128",
    },
    "particle_effect": {
        "__type": "Sandbox.ParticleEffect",
        "PlayOnStart": True,
        "Loop": True,
    },
    "sound_point": {
        "__type": "Sandbox.SoundPointComponent",
        "PlayOnStart": False,
        "StopOnDestroy": True,
    },
    "nav_mesh_agent": {
        "__type": "Sandbox.NavMeshAgent",
        "MaxSpeed": 200,
        "MaxAcceleration": 800,
        "AgentRadius": 16,
        "AgentHeight": 72,
    },
    "screen_panel": {
        "__type": "Sandbox.ScreenPanel",
        "ZIndex": 100,
        "Opacity": 1.0,
    },
    "world_panel": {
        "__type": "Sandbox.WorldPanel",
        "PanelSize": "1024,768",
        "LookAtCamera": False,
        "RenderScale": 1.0,
    },
    "fixed_joint": {
        "__type": "Sandbox.FixedJoint",
    },
    "hinge_joint": {
        "__type": "Sandbox.HingeJoint",
        "MinAngle": -45,
        "MaxAngle": 45,
    },
    "spring_joint": {
        "__type": "Sandbox.SpringJoint",
        "Frequency": 5,
        "Damping": 0.5,
    },
    "ball_socket_joint": {
        "__type": "Sandbox.BallSocketJoint",
    },
    "trail_renderer": {
        "__type": "Sandbox.TrailRenderer",
        "Color": "1,1,1,1",
        "Width": 5,
        "Lifetime": 1.0,
    },
    "character_controller": {
        "__type": "Sandbox.CharacterController",
        "Height": 72,
        "Radius": 16,
        "UseCollisionRules": True,
    },
}
COMPONENT_PRESETS: Dict[str, Dict[str, Any]] = {
    **_COMPONENT_PRESETS_PART0,
    **_COMPONENT_PRESETS_PART1,
}


def _new_guid() -> str:
    """Generate a new UUID v4 string."""
    return str(uuid.uuid4())


def _make_component(
    component_type: str, properties: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Build a component dict from a type string and optional properties.

    If *component_type* matches a key in COMPONENT_PRESETS, the preset values
    are used as defaults and *properties* are merged on top.  Otherwise, a
    bare component with the given __type is created.
    """
    if component_type in COMPONENT_PRESETS:
        comp = dict(COMPONENT_PRESETS[component_type])
    else:
        comp = {"__type": component_type}

    comp["__guid"] = _new_guid()

    if properties:
        comp.update(properties)

    return comp
