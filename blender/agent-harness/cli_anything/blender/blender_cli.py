# ruff: noqa: F403, F405, E501
from .blender_cli_base import *  # noqa: F403
from .blender_cli_p10 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .blender_cli_p1 import get_session, _print_dict, _print_list, output, _spawn_live_viewer, _spawn_live_poller  # noqa: F401,E501
from .blender_cli_p10 import preview_live_push, preview_live_status, preview_live_stop, preview_live_monitor, session, session_status, session_undo, session_redo, session_history  # noqa: F401,E501
from .blender_cli_p2 import handle_error, cli  # noqa: F401,E501
from .blender_cli_p3 import repl, auto_save_on_exit, scene  # noqa: F401,E501
from .blender_cli_p4 import scene_new, scene_open, scene_save, scene_info, scene_profiles, scene_json, object_group, object_add, object_remove  # noqa: F401,E501
from .blender_cli_p5 import object_duplicate, object_transform, object_set, object_list, object_get, material, material_create, material_assign, material_set  # noqa: F401,E501
from .blender_cli_p6 import material_list, material_get, modifier_group, modifier_list_available, modifier_info, modifier_add, modifier_remove, modifier_set, modifier_list, camera  # noqa: F401,E501
from .blender_cli_p7 import camera_add, camera_set, camera_set_active, camera_list, light, light_add, light_set, light_list, animation  # noqa: F401,E501
from .blender_cli_p8 import animation_keyframe, animation_remove_keyframe, animation_frame_range, animation_fps, animation_list_keyframes, render_group, render_settings, render_info, render_presets  # noqa: F401,E501
from .blender_cli_p9 import render_execute, render_script, preview_group, preview_live_group, preview_recipes, preview_capture, preview_latest, preview_live_start  # noqa: F401,E501
# fmt: on
