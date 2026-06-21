# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403
from .sbox_cli_p23 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .sbox_cli_p1 import _output, _output_error, _format_table, _format_status_block, _resolve_project_path, _resolve_project_dir, _resolve_input_config  # noqa: F401,E501
from .sbox_cli_p10 import scene_instantiate_prefab, prefab, prefab_new, prefab_info, prefab_from_scene  # noqa: F401,E501
from .sbox_cli_p11 import prefab_add_component, prefab_remove_component, prefab_list, prefab_refs  # noqa: F401,E501
from .sbox_cli_p12 import prefab_modify_component, prefab_diff, codegen  # noqa: F401,E501
from .sbox_cli_p13 import codegen_component, codegen_gameresource  # noqa: F401,E501
from .sbox_cli_p14 import codegen_editor_menu, codegen_razor, codegen_class  # noqa: F401,E501
from .sbox_cli_p15 import codegen_panel_component, input_group, input_list, input_add  # noqa: F401,E501
from .sbox_cli_p16 import input_remove, input_set, collision_group, collision_list, collision_add_layer, collision_add_rule  # noqa: F401,E501
from .sbox_cli_p17 import collision_remove_rule, collision_remove_layer, server, server_start, server_info, asset, asset_list  # noqa: F401,E501
from .sbox_cli_p18 import asset_info, asset_compile, asset_find_refs, asset_find_unused  # noqa: F401,E501
from .sbox_cli_p19 import asset_rename, asset_move, material, material_new, material_info, material_list  # noqa: F401,E501
from .sbox_cli_p2 import _resolve_collision_config, _REPL_BANNER, _REPL_HELP, cli  # noqa: F401,E501
from .sbox_cli_p20 import material_set, sound, sound_list, sound_new, sound_info, sound_set, localization  # noqa: F401,E501
from .sbox_cli_p21 import localization_new, localization_list, localization_set, localization_get, localization_remove, localization_bulk_set, launch, session_group, session_status  # noqa: F401,E501
from .sbox_cli_p22 import session_undo, session_redo, test_group, test_setup  # noqa: F401,E501
from .sbox_cli_p23 import test_run  # noqa: F401,E501
from .sbox_cli_p3 import repl, project, project_new  # noqa: F401,E501
from .sbox_cli_p4 import project_info, project_config, project_add_package, project_remove_package  # noqa: F401,E501
from .sbox_cli_p5 import project_validate, scene, scene_new, scene_info, scene_list  # noqa: F401,E501
from .sbox_cli_p6 import scene_add_object, scene_remove_object, scene_add_component, scene_remove_component  # noqa: F401,E501
from .sbox_cli_p7 import scene_modify_object, scene_set_property, scene_clone_object, scene_get_object  # noqa: F401,E501
from .sbox_cli_p8 import scene_set_navmesh, scene_list_presets, scene_modify_component, scene_query  # noqa: F401,E501
from .sbox_cli_p9 import scene_refs, scene_bulk_modify, scene_diff  # noqa: F401,E501
# fmt: on
