# ruff: noqa: F403, F405, E501
from .prefab_base import *  # noqa: F403

# fmt: off
# re-export full surface
from .prefab_p1 import _new_guid, _write_json, _build_root_object, create_prefab, load_prefab, save_prefab  # noqa: F401,E501
from .prefab_p2 import get_prefab_info, from_scene_object  # noqa: F401,E501
from .prefab_p3 import diff_prefabs, extract_asset_refs  # noqa: F401,E501
from .prefab_p4 import modify_component  # noqa: F401,E501
# fmt: on
