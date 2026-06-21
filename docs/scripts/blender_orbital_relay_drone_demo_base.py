# ruff: noqa: E501
#!/usr/bin/env python3
"""Build a clear Blender orbital relay drone demo with live previews and motion.

Outputs:

- real staged preview bundles
- a persisted live `session.json`
- append-only `trajectory.json`
- `live.html` rendered through `cli-hub previews html`
- a final still render and turntable video
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List
from cli_anything.blender.core import preview as preview_mod
from cli_anything.blender.core.animation import add_keyframe, set_current_frame, set_frame_range, set_fps
from cli_anything.blender.core.lighting import add_camera, add_light
from cli_anything.blender.core.materials import assign_material, create_material, set_material_property
from cli_anything.blender.core.modifiers import add_modifier
from cli_anything.blender.core.objects import add_object
from cli_anything.blender.core.render import render_scene, set_render_settings
from cli_anything.blender.core.scene import create_scene, save_scene
from cli_anything.blender.core.session import Session
from cli_anything.blender.utils import blender_backend

__all__ = ['Dict', 'List', 'Path', 'Session', 'add_camera', 'add_keyframe', 'add_light', 'add_modifier', 'add_object', 'annotations', 'argparse', 'assign_material', 'blender_backend', 'copy', 'create_material', 'create_scene', 'json', 'os', 'preview_mod', 'render_scene', 'save_scene', 'set_current_frame', 'set_fps', 'set_frame_range', 'set_material_property', 'set_render_settings', 'shutil', 'subprocess', 'sys']
