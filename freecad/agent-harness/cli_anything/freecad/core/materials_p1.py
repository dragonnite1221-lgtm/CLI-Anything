# ruff: noqa: F403, F405, E501
from .materials_base import *  # noqa: F403


_PRESETS_PART0 = {
    "steel": {
        "color": [0.7, 0.7, 0.75, 1.0],
        "metallic": 0.9,
        "roughness": 0.3,
    },
    "aluminum": {
        "color": [0.8, 0.8, 0.85, 1.0],
        "metallic": 0.9,
        "roughness": 0.2,
    },
    "copper": {
        "color": [0.72, 0.45, 0.2, 1.0],
        "metallic": 1.0,
        "roughness": 0.25,
    },
    "brass": {
        "color": [0.78, 0.68, 0.35, 1.0],
        "metallic": 0.9,
        "roughness": 0.3,
    },
    "plastic_white": {
        "color": [0.95, 0.95, 0.95, 1.0],
        "metallic": 0.0,
        "roughness": 0.4,
    },
    "plastic_black": {
        "color": [0.1, 0.1, 0.1, 1.0],
        "metallic": 0.0,
        "roughness": 0.5,
    },
    "wood": {
        "color": [0.55, 0.35, 0.15, 1.0],
        "metallic": 0.0,
        "roughness": 0.7,
    },
    "glass": {
        "color": [0.85, 0.9, 0.95, 0.3],
        "metallic": 0.0,
        "roughness": 0.05,
    },
    "rubber": {
        "color": [0.15, 0.15, 0.15, 1.0],
        "metallic": 0.0,
        "roughness": 0.9,
    },
    "gold": {
        "color": [1.0, 0.84, 0.0, 1.0],
        "metallic": 1.0,
        "roughness": 0.1,
    },
    "titanium": {
        "color": [0.75, 0.75, 0.78, 1.0],
        "metallic": 0.9,
        "roughness": 0.25,
        "density": 4507,
        "youngs_modulus": 116,
        "poisson_ratio": 0.34,
        "yield_strength": 880,
        "ultimate_strength": 950,
    },
}
