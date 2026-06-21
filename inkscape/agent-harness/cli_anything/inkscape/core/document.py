# ruff: noqa: F403, F405, E501
from .document_base import *  # noqa: F403

# fmt: off
# re-export full surface
from .document_p1 import create_document, open_document, save_document, _add_gradient_to_defs  # noqa: F401,E501
from .document_p2 import _object_to_svg_element  # noqa: F401,E501
from .document_p3 import project_to_svg, save_svg  # noqa: F401,E501
from .document_p4 import get_document_info, set_canvas_size, set_units, list_profiles  # noqa: F401,E501
# fmt: on
