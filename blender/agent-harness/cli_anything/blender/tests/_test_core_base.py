# ruff: noqa: F403, F405, E501
"""Unit tests for Blender CLI core modules.

Tests use synthetic data only — no real 3D files or Blender installation.
"""
import json
import os
import sys
import tempfile
from pathlib import Path
import pytest
from cli_anything.blender.core.scene import create_scene, open_scene, save_scene, get_scene_info, list_profiles
from cli_anything.blender.core.objects import (
    add_object, remove_object, duplicate_object, transform_object,
    set_object_property, get_object, list_objects, MESH_PRIMITIVES,
)
from cli_anything.blender.core.materials import (
    create_material, assign_material, set_material_property,
    list_materials, get_material, MATERIAL_PROPS,
)
from cli_anything.blender.core.modifiers import (
    list_available, get_modifier_info, validate_params, add_modifier,
    remove_modifier, set_modifier_param, list_modifiers, MODIFIER_REGISTRY,
)
from cli_anything.blender.core.lighting import (
    add_camera, set_camera, set_active_camera, list_cameras, get_camera,
    add_light, set_light, list_lights, get_light,
    CAMERA_TYPES, LIGHT_TYPES,
)
from cli_anything.blender.core.animation import (
    add_keyframe, remove_keyframe, set_frame_range, set_fps,
    set_current_frame, list_keyframes, ANIMATABLE_PROPERTIES,
)
from cli_anything.blender.core.render import (
    set_render_settings, get_render_settings, list_render_presets,
    render_scene, RENDER_PRESETS, VALID_ENGINES,
)
from cli_anything.blender.core import preview as preview_mod
from cli_anything.blender.utils import blender_backend
from cli_anything.blender.core.session import Session


# fmt: off
__all__ = ['ANIMATABLE_PROPERTIES', 'CAMERA_TYPES', 'LIGHT_TYPES', 'MATERIAL_PROPS', 'MESH_PRIMITIVES', 'MODIFIER_REGISTRY', 'Path', 'RENDER_PRESETS', 'Session', 'VALID_ENGINES', 'add_camera', 'add_keyframe', 'add_light', 'add_modifier', 'add_object', 'assign_material', 'blender_backend', 'create_material', 'create_scene', 'duplicate_object', 'get_camera', 'get_light', 'get_material', 'get_modifier_info', 'get_object', 'get_render_settings', 'get_scene_info', 'json', 'list_available', 'list_cameras', 'list_keyframes', 'list_lights', 'list_materials', 'list_modifiers', 'list_objects', 'list_profiles', 'list_render_presets', 'open_scene', 'os', 'preview_mod', 'pytest', 'remove_keyframe', 'remove_modifier', 'remove_object', 'render_scene', 'save_scene', 'set_active_camera', 'set_camera', 'set_current_frame', 'set_fps', 'set_frame_range', 'set_light', 'set_material_property', 'set_modifier_param', 'set_object_property', 'set_render_settings', 'sys', 'tempfile', 'transform_object', 'validate_params']  # noqa: E501
# fmt: on
