# ruff: noqa: F403, F405, E501
from .document_base import *  # noqa: F403

# fmt: off
# re-export full surface
from .document_p1 import _now_iso, _REQUIRED_COLLECTIONS, _OPTIONAL_COLLECTIONS, ALL_COLLECTIONS, ensure_collection, _validate_project, create_document  # noqa: F401,E501
from .document_p2 import open_document, save_document, get_document_info, list_profiles  # noqa: F401,E501
# fmt: on
