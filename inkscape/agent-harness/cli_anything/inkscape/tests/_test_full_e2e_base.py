# ruff: noqa: F403, F405, E501
"""End-to-end tests for Inkscape CLI.

These tests verify full workflows: document creation, manipulation,
SVG generation, SVG validation, export verification, and CLI subprocess
invocation. No actual Inkscape installation is required.
"""
import json
import os
import sys
import tempfile
import subprocess
import xml.etree.ElementTree as ET
import pytest
from cli_anything.inkscape.utils.svg_utils import (
    SVG_NS, INKSCAPE_NS, SODIPODI_NS, reset_id_counter,
    parse_style, serialize_svg,
)
from cli_anything.inkscape.core.document import (
    create_document, save_document, open_document, save_svg,
    get_document_info, project_to_svg,
)
from cli_anything.inkscape.core.shapes import (
    add_rect, add_circle, add_ellipse, add_line, add_polygon,
    add_path, add_star, remove_object, duplicate_object, list_objects,
)
from cli_anything.inkscape.core.text import add_text, set_text_property, list_text_objects
from cli_anything.inkscape.core.styles import set_fill, set_stroke, set_opacity, set_style, get_object_style
from cli_anything.inkscape.core.transforms import translate, rotate, scale, get_transform, clear_transform
from cli_anything.inkscape.core.layers import add_layer, remove_layer, move_to_layer, list_layers, get_layer
from cli_anything.inkscape.core.paths import (
    path_union, path_intersection, path_difference,
    convert_to_path,
)
from cli_anything.inkscape.core.gradients import add_linear_gradient, add_radial_gradient, apply_gradient
from cli_anything.inkscape.core.export import render_to_png, export_svg, list_presets
from cli_anything.inkscape.core.session import Session


# fmt: off
__all__ = ['ET', 'INKSCAPE_NS', 'SODIPODI_NS', 'SVG_NS', 'Session', 'add_circle', 'add_ellipse', 'add_layer', 'add_line', 'add_linear_gradient', 'add_path', 'add_polygon', 'add_radial_gradient', 'add_rect', 'add_star', 'add_text', 'apply_gradient', 'clear_transform', 'convert_to_path', 'create_document', 'duplicate_object', 'export_svg', 'get_document_info', 'get_layer', 'get_object_style', 'get_transform', 'json', 'list_layers', 'list_objects', 'list_presets', 'list_text_objects', 'move_to_layer', 'open_document', 'os', 'parse_style', 'path_difference', 'path_intersection', 'path_union', 'project_to_svg', 'pytest', 'remove_layer', 'remove_object', 'render_to_png', 'reset_id_counter', 'rotate', 'save_document', 'save_svg', 'scale', 'serialize_svg', 'set_fill', 'set_opacity', 'set_stroke', 'set_style', 'set_text_property', 'subprocess', 'sys', 'tempfile', 'translate']  # noqa: E501
# fmt: on
