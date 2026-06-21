# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
# re-export full surface
from .scene_p1 import _COMPONENT_PRESETS_PART0  # noqa: F401,E501
from .scene_p10 import modify_component, _regenerate_guids  # noqa: F401,E501
from .scene_p11 import clone_object, get_object, _resolve_component_type  # noqa: F401,E501
from .scene_p12 import _object_has_component, _object_has_tag, _parse_position_bounds, _object_in_bounds, query_objects  # noqa: F401,E501
from .scene_p13 import ASSET_REF_EXTENSIONS, _ASSET_PATH_FIELDS, _is_asset_ref, _category_for_ref, _walk_for_refs  # noqa: F401,E501
from .scene_p14 import extract_asset_refs, _object_summary, _diff_two_objects  # noqa: F401,E501
from .scene_p15 import diff_scenes  # noqa: F401,E501
from .scene_p16 import instantiate_prefab  # noqa: F401,E501
from .scene_p17 import bulk_modify_objects  # noqa: F401,E501
from .scene_p2 import _COMPONENT_PRESETS_PART1, COMPONENT_PRESETS, _new_guid, _make_component  # noqa: F401,E501
from .scene_p3 import _make_game_object  # noqa: F401,E501
from .scene_p4 import _build_default_objects  # noqa: F401,E501
from .scene_p5 import _flatten_objects, _remove_from_list, _write_json, create_scene, load_scene, save_scene  # noqa: F401,E501
from .scene_p6 import get_scene_info, list_objects, find_object  # noqa: F401,E501
from .scene_p7 import add_object, remove_object, add_component  # noqa: F401,E501
from .scene_p8 import remove_component, modify_object, _SCENE_PROPERTY_MAP  # noqa: F401,E501
from .scene_p9 import set_scene_properties, _NAVMESH_PROPERTY_MAP, set_navmesh_properties  # noqa: F401,E501
# fmt: on
