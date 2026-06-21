# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403


_COMPONENT_PRESETS_PART0 = {
    "model": {
        "__type": "Sandbox.ModelRenderer",
        "Model": "models/dev/box.vmdl",
        "RenderType": "On",
        "Tint": "1,1,1,1",
    },
    "box_collider": {
        "__type": "Sandbox.BoxCollider",
        "Center": "0,0,0",
        "Scale": "50,50,50",
        "IsTrigger": False,
        "Static": False,
    },
    "sphere_collider": {
        "__type": "Sandbox.SphereCollider",
        "Center": "0,0,0",
        "Radius": 25,
        "IsTrigger": False,
    },
    "rigidbody": {
        "__type": "Sandbox.Rigidbody",
        "Gravity": True,
        "LinearDamping": 0,
        "AngularDamping": 0,
        "Locking": {},
        "MassOverride": 0,
        "MotionEnabled": True,
        "RigidbodyFlags": 0,
        "StartAsleep": False,
    },
    "camera": {
        "__type": "Sandbox.CameraComponent",
        "FieldOfView": 60,
        "ZNear": 10,
        "ZFar": 10000,
        "IsMainCamera": True,
        "BackgroundColor": "0.33333,0.46275,0.52157,1",
    },
    "light_directional": {
        "__type": "Sandbox.DirectionalLight",
        "LightColor": "0.94419,0.97767,1,1",
        "Shadows": True,
        "SkyColor": "0.2532,0.32006,0.35349,1",
    },
    "light_point": {
        "__type": "Sandbox.PointLight",
        "LightColor": "1,1,1,1",
        "Radius": 400,
    },
    "player_controller": {
        "__type": "Sandbox.PlayerController",
    },
    "spot_light": {
        "__type": "Sandbox.SpotLight",
        "LightColor": "1,1,1,1",
        "Radius": 500,
        "ConeInner": 15,
        "ConeOuter": 45,
        "Shadows": True,
    },
    "ambient_light": {
        "__type": "Sandbox.AmbientLight",
        "Color": "1,1,1,1",
        "Intensity": 1.0,
    },
    "capsule_collider": {
        "__type": "Sandbox.CapsuleCollider",
        "Start": "0,0,0",
        "End": "0,0,72",
        "Radius": 16,
        "IsTrigger": False,
    },
    "plane_collider": {
        "__type": "Sandbox.PlaneCollider",
        "Scale": "100,100",
        "IsTrigger": False,
        "Static": True,
    },
    "model_collider": {
        "__type": "Sandbox.ModelCollider",
        "Model": "models/dev/box.vmdl",
        "IsTrigger": False,
        "Static": False,
    },
    "sprite_renderer": {
        "__type": "Sandbox.SpriteRenderer",
        "Texture": "textures/dev/white.vtex",
        "Tint": "1,1,1,1",
        "Size": "64,64",
    },
    "skinned_model_renderer": {
        "__type": "Sandbox.SkinnedModelRenderer",
        "Model": "models/citizen/citizen.vmdl",
        "RenderType": "On",
        "Tint": "1,1,1,1",
    },
}
