# ruff: noqa: F403, F405, E501
"""
Comprehensive unit tests for the cli-anything-freecad core modules.

All tests use synthetic data and require no external dependencies
beyond pytest.
"""
import json
import math
import os
from pathlib import Path
import pytest
from cli_anything.freecad.core.document import (
    PROFILES,
    create_document,
    get_document_info,
    list_profiles,
    open_document,
    save_document,
)
from cli_anything.freecad.core.parts import (
    PRIMITIVES,
    add_part,
    align_part,
    boolean_op,
    get_part,
    list_parts,
    part_bounds,
    remove_part,
    transform_part,
)
from cli_anything.freecad.core.sketch import (
    add_arc,
    add_circle,
    add_constraint,
    add_line,
    add_rectangle,
    close_sketch,
    create_sketch,
    get_sketch,
    list_sketches,
)
from cli_anything.freecad.core.body import (
    additive_box,
    additive_cone,
    additive_cylinder,
    chamfer,
    create_body,
    datum_plane,
    datum_line,
    datum_point,
    fillet,
    get_body,
    hole_feature,
    linear_pattern,
    list_bodies,
    local_coordinate_system,
    pad,
    pocket,
    polar_pattern,
    revolution,
    subtractive_box,
    toggle_freeze,
)
from cli_anything.freecad.core.materials import (
    PRESETS,
    assign_material,
    create_material,
    get_material,
    list_materials,
    list_presets,
    set_material_property,
)
from cli_anything.freecad.core import preview as preview_mod
from cli_anything.freecad.core import motion as motion_mod
from cli_anything.freecad.core.session import Session
from cli_anything.freecad.utils import freecad_backend


# fmt: off
__all__ = ['PRESETS', 'PRIMITIVES', 'PROFILES', 'Path', 'Session', 'add_arc', 'add_circle', 'add_constraint', 'add_line', 'add_part', 'add_rectangle', 'additive_box', 'additive_cone', 'additive_cylinder', 'align_part', 'assign_material', 'boolean_op', 'chamfer', 'close_sketch', 'create_body', 'create_document', 'create_material', 'create_sketch', 'datum_line', 'datum_plane', 'datum_point', 'fillet', 'freecad_backend', 'get_body', 'get_document_info', 'get_material', 'get_part', 'get_sketch', 'hole_feature', 'json', 'linear_pattern', 'list_bodies', 'list_materials', 'list_parts', 'list_presets', 'list_profiles', 'list_sketches', 'local_coordinate_system', 'math', 'motion_mod', 'open_document', 'os', 'pad', 'part_bounds', 'pocket', 'polar_pattern', 'preview_mod', 'pytest', 'remove_part', 'revolution', 'save_document', 'set_material_property', 'subtractive_box', 'toggle_freeze', 'transform_part']  # noqa: E501
# fmt: on
