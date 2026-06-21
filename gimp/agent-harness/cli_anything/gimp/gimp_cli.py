# ruff: noqa: F403, F405, E501
from .gimp_cli_base import *  # noqa: F403
from .gimp_cli_p6 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .gimp_cli_p1 import get_session, _print_dict, _print_list, output, handle_error, cli  # noqa: F401,E501
from .gimp_cli_p2 import repl, auto_save_on_exit, project, project_new, project_open  # noqa: F401,E501
from .gimp_cli_p3 import project_save, project_info, project_profiles, project_json, layer, layer_new, layer_add_from_file, layer_list, layer_remove, layer_duplicate, layer_move, layer_set  # noqa: F401,E501
from .gimp_cli_p4 import layer_flatten, layer_merge_down, canvas, canvas_info, canvas_resize, canvas_scale, canvas_crop, canvas_mode, canvas_dpi, filter_group, filter_list_available, filter_info, filter_add  # noqa: F401,E501
from .gimp_cli_p5 import filter_remove, filter_set, filter_list, media, media_probe, media_list, media_check, media_histogram, export_group, export_presets, export_preset_info, export_render, session, session_status, session_undo, session_redo  # noqa: F401,E501
from .gimp_cli_p6 import session_history, draw, draw_text, draw_rect  # noqa: F401,E501
# fmt: on
