# ruff: noqa: F403, F405, E501
"""Unit tests for Inkscape CLI core modules.

Tests use synthetic data only — no real SVG files or Inkscape installation.
"""

import json
import os
import sys
import tempfile
import pytest
from click.testing import CliRunner

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from cli_anything.inkscape.utils.svg_utils import (
    parse_style,
    serialize_style,
    validate_color,
    generate_id,
    reset_id_counter,
    create_svg_element,
    serialize_svg,
    find_defs,
    find_element_by_id,
    remove_element_by_id,
    SVG_NS,
    INKSCAPE_NS,
)
from cli_anything.inkscape.core.document import (
    create_document,
    open_document,
    save_document,
    get_document_info,
    set_canvas_size,
    set_units,
    list_profiles,
    PROFILES,
    VALID_UNITS,
    project_to_svg,
    save_svg,
)
from cli_anything.inkscape.core.shapes import (
    add_rect,
    add_circle,
    add_ellipse,
    add_line,
    add_polygon,
    add_path,
    add_star,
    remove_object,
    duplicate_object,
    list_objects,
    get_object,
    SHAPE_TYPES,
)
from cli_anything.inkscape.core.text import (
    add_text,
    set_text_property,
    list_text_objects,
    layout_text_lines,
    TEXT_PROPERTIES,
)
from cli_anything.inkscape.core.styles import (
    set_fill,
    set_stroke,
    set_opacity,
    set_style,
    list_style_properties,
    get_object_style,
    STYLE_PROPERTIES,
)
from cli_anything.inkscape.core.transforms import (
    translate,
    rotate,
    scale,
    skew_x,
    skew_y,
    get_transform,
    set_transform,
    clear_transform,
    parse_transform_string,
    serialize_transform_string,
)
from cli_anything.inkscape.core.layers import (
    add_layer,
    remove_layer,
    move_to_layer,
    set_layer_property,
    list_layers,
    reorder_layers,
    get_layer,
)
from cli_anything.inkscape.core.paths import (
    path_union,
    path_intersection,
    path_difference,
    path_exclusion,
    convert_to_path,
    list_path_operations,
    PATH_OPERATIONS,
    CONVERTIBLE_TYPES,
)
from cli_anything.inkscape.core.gradients import (
    add_linear_gradient,
    add_radial_gradient,
    apply_gradient,
    list_gradients,
    get_gradient,
    remove_gradient,
)
from cli_anything.inkscape.core.export import EXPORT_PRESETS, list_presets
from cli_anything.inkscape.core.session import Session
from cli_anything.inkscape import inkscape_cli


@pytest.fixture(autouse=True)
def reset_ids():
    """Reset the ID counter before each test."""
    reset_id_counter()


# fmt: off
__all__ = ['CONVERTIBLE_TYPES', 'CliRunner', 'EXPORT_PRESETS', 'INKSCAPE_NS', 'PATH_OPERATIONS', 'PROFILES', 'SHAPE_TYPES', 'STYLE_PROPERTIES', 'SVG_NS', 'Session', 'TEXT_PROPERTIES', 'VALID_UNITS', 'add_circle', 'add_ellipse', 'add_layer', 'add_line', 'add_linear_gradient', 'add_path', 'add_polygon', 'add_radial_gradient', 'add_rect', 'add_star', 'add_text', 'apply_gradient', 'clear_transform', 'convert_to_path', 'create_document', 'create_svg_element', 'duplicate_object', 'find_defs', 'find_element_by_id', 'generate_id', 'get_document_info', 'get_gradient', 'get_layer', 'get_object', 'get_object_style', 'get_transform', 'inkscape_cli', 'json', 'layout_text_lines', 'list_gradients', 'list_layers', 'list_objects', 'list_path_operations', 'list_presets', 'list_profiles', 'list_style_properties', 'list_text_objects', 'move_to_layer', 'open_document', 'os', 'parse_style', 'parse_transform_string', 'path_difference', 'path_exclusion', 'path_intersection', 'path_union', 'project_to_svg', 'pytest', 'remove_element_by_id', 'remove_gradient', 'remove_layer', 'remove_object', 'reorder_layers', 'reset_id_counter', 'reset_ids', 'rotate', 'save_document', 'save_svg', 'scale', 'serialize_style', 'serialize_svg', 'serialize_transform_string', 'set_canvas_size', 'set_fill', 'set_layer_property', 'set_opacity', 'set_stroke', 'set_style', 'set_text_property', 'set_transform', 'set_units', 'skew_x', 'skew_y', 'sys', 'tempfile', 'translate', 'validate_color']  # noqa: E501
# fmt: on
