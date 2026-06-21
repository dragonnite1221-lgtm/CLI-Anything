# ruff: noqa: F403, F405, E501
from .objects_base import *  # noqa: F403

# fmt: off
# re-export full surface
from .objects_p1 import _next_id, _unique_name, add_object, remove_object, duplicate_object  # noqa: F401,E501
from .objects_p2 import transform_object, set_object_property, get_object, list_objects  # noqa: F401,E501
# fmt: on
