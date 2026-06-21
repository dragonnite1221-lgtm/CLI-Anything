# ruff: noqa: F403, F405, E501
from .svg_utils_base import *  # noqa: F403

# fmt: off
# re-export full surface
from .svg_utils_p1 import _ns, create_svg_element, parse_svg, parse_svg_file, serialize_svg, write_svg_file, parse_style, serialize_style, get_element_style, set_element_style, update_element_style, _id_counter, generate_id, reset_id_counter, find_defs, find_all_shapes, find_element_by_id  # noqa: F401,E501
from .svg_utils_p2 import remove_element_by_id, validate_color  # noqa: F401,E501
# fmt: on
