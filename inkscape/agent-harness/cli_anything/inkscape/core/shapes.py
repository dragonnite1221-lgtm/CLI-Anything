# ruff: noqa: F403, F405, E501
from .shapes_base import *  # noqa: F403

# fmt: off
# re-export full surface
from .shapes_p1 import _default_layer_id, _add_object, add_rect, add_circle, add_ellipse, add_line  # noqa: F401,E501
from .shapes_p2 import add_polygon, add_path, _star_path, add_star, remove_object  # noqa: F401,E501
from .shapes_p3 import duplicate_object, list_objects, get_object  # noqa: F401,E501
# fmt: on
