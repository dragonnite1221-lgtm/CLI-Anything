# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p2 import _make_component, _new_guid  # noqa: E402,E501
from .scene_p3 import _make_game_object  # noqa: E402,E501
# fmt: on


def _build_default_objects() -> List[Dict[str, Any]]:
    """Return the default set of GameObjects for a minimal scene.

    Includes: Sun (DirectionalLight), 2D Skybox (SkyBox2D + EnvmapProbe),
    Plane (ModelRenderer + BoxCollider), Camera (CameraComponent + post-processing).
    """
    sun = _make_game_object(
        name="Sun",
        position="0,0,0",
        rotation="-0.0591653,0.5160446,0.0340129,0.8537855",
        components=[
            _make_component("light_directional"),
        ],
    )

    skybox = _make_game_object(
        name="2D Skybox",
        tags="skybox",
        components=[
            {
                "__guid": _new_guid(),
                "__type": "Sandbox.SkyBox2D",
                "SkyMaterial": "materials/skybox/skybox_day_01.vmat",
                "Tint": "1,1,1,1",
            },
            {
                "__guid": _new_guid(),
                "__type": "Sandbox.EnvmapProbe",
                "Texture": "textures/cubemaps/default2.vtex",
                "Bounds": "512,512,512",
                "Feathering": 0.02,
            },
        ],
    )

    plane = _make_game_object(
        name="Plane",
        position="0,0,0",
        scale="5,5,5",
        components=[
            {
                "__guid": _new_guid(),
                "__type": "Sandbox.ModelRenderer",
                "Model": "models/dev/plane.vmdl",
                "RenderType": "On",
                "Tint": "0.39546,0.51320,0.27128,1",
                "MaterialOverride": "materials/default.vmat",
            },
            {
                "__guid": _new_guid(),
                "__type": "Sandbox.BoxCollider",
                "Center": "0,0,-5",
                "Scale": "100,100,10",
                "IsTrigger": False,
                "Static": True,
            },
        ],
    )

    camera = _make_game_object(
        name="Camera",
        position="0,-200,150",
        rotation="0.16307,0,0,0.98663",
        components=[
            _make_component("camera"),
            {
                "__guid": _new_guid(),
                "__type": "Sandbox.Bloom",
                "Threshold": 0.5,
                "ThresholdWidth": 0.5,
                "MaximumBloom": 0.5,
                "Mode": "Additive",
                "BlurWeight": 1,
            },
            {
                "__guid": _new_guid(),
                "__type": "Sandbox.Tonemapping",
                "Mode": "ACES",
                "ExposureCompensation": 0,
                "MinimumExposure": 1,
                "MaximumExposure": 2,
                "Rate": 1,
            },
            {
                "__guid": _new_guid(),
                "__type": "Sandbox.Sharpen",
                "Scale": 0.2,
            },
        ],
    )

    return [sun, skybox, plane, camera]
