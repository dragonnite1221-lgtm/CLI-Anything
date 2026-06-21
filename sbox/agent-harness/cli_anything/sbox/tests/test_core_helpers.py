# ruff: noqa: F403, F405, E501
"""Unit tests for cli_anything.sbox.core modules.

Covers: project, scene, prefab, codegen, input_config, collision_config, session, export.
All tests are self-contained and use pytest's tmp_path fixture for file operations.
"""

import copy
import json
import os
import uuid
import pytest
from cli_anything.sbox.core.codegen import (
    generate_class,
    generate_component,
    generate_editor_menu,
    generate_gameresource,
    generate_panel_component,
    generate_razor,
)
from cli_anything.sbox.core.collision_config import (
    add_layer,
    add_rule,
    get_default_collision_config,
    list_layers,
    load_collision_config,
    remove_layer,
    remove_rule,
    save_collision_config,
)
from cli_anything.sbox.core.export import (
    ASSET_EXTENSIONS,
    find_asset_refs,
    find_project_dir,
    find_unused_assets,
    get_asset_info,
    list_assets,
    move_asset,
    rename_asset,
)
from cli_anything.sbox.core.input_config import (
    add_action,
    get_default_input_config,
    list_actions,
    load_input_config,
    remove_action,
    save_input_config,
    set_action,
)
from cli_anything.sbox.core.localization import (
    bulk_set,
    create_translation_file,
    get_key,
    list_keys,
    load_translations,
    remove_key,
    set_key,
)
from cli_anything.sbox.core.material import (
    create_material,
    list_materials,
    parse_material,
    update_material,
)
from cli_anything.sbox.core.prefab import (
    create_prefab,
    diff_prefabs,
    from_scene_object,
    get_prefab_info,
    load_prefab,
    save_prefab,
)
from cli_anything.sbox.core.prefab import (
    extract_asset_refs as prefab_extract_asset_refs,
)
from cli_anything.sbox.core.prefab import (
    modify_component as prefab_modify_component,
)
from cli_anything.sbox.core.project import (
    add_package,
    configure_project,
    create_project,
    find_sbproj,
    get_project_info,
    load_project,
    remove_package,
    save_project,
)
from cli_anything.sbox.core.scene import (
    COMPONENT_PRESETS,
    add_component,
    add_object,
    bulk_modify_objects,
    clone_object,
    create_scene,
    diff_scenes,
    extract_asset_refs,
    find_object,
    get_object,
    get_scene_info,
    instantiate_prefab,
    list_objects,
    load_scene,
    modify_component,
    modify_object,
    query_objects,
    remove_component,
    remove_object,
    save_scene,
    set_navmesh_properties,
    set_scene_properties,
)
from cli_anything.sbox.core.session import Session
from cli_anything.sbox.core.sound import (
    create_sound_event,
    parse_sound_event,
    update_sound_event,
)
from cli_anything.sbox.core.validate import validate_project


# fmt: off
__all__ = ['ASSET_EXTENSIONS', 'COMPONENT_PRESETS', 'Session', 'add_action', 'add_component', 'add_layer', 'add_object', 'add_package', 'add_rule', 'bulk_modify_objects', 'bulk_set', 'clone_object', 'configure_project', 'copy', 'create_material', 'create_prefab', 'create_project', 'create_scene', 'create_sound_event', 'create_translation_file', 'diff_prefabs', 'diff_scenes', 'extract_asset_refs', 'find_asset_refs', 'find_object', 'find_project_dir', 'find_sbproj', 'find_unused_assets', 'from_scene_object', 'generate_class', 'generate_component', 'generate_editor_menu', 'generate_gameresource', 'generate_panel_component', 'generate_razor', 'get_asset_info', 'get_default_collision_config', 'get_default_input_config', 'get_key', 'get_object', 'get_prefab_info', 'get_project_info', 'get_scene_info', 'instantiate_prefab', 'json', 'list_actions', 'list_assets', 'list_keys', 'list_layers', 'list_materials', 'list_objects', 'load_collision_config', 'load_input_config', 'load_prefab', 'load_project', 'load_scene', 'load_translations', 'modify_component', 'modify_object', 'move_asset', 'os', 'parse_material', 'parse_sound_event', 'prefab_extract_asset_refs', 'prefab_modify_component', 'pytest', 'query_objects', 'remove_action', 'remove_component', 'remove_key', 'remove_layer', 'remove_object', 'remove_package', 'remove_rule', 'rename_asset', 'save_collision_config', 'save_input_config', 'save_prefab', 'save_project', 'save_scene', 'set_action', 'set_key', 'set_navmesh_properties', 'set_scene_properties', 'update_material', 'update_sound_event', 'uuid', 'validate_project']  # noqa: E501
# fmt: on
