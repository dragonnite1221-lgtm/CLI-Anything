# ruff: noqa: F403, F405, E501
from .audacity_cli_base import *  # noqa: F403
from .audacity_cli_p7 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .audacity_cli_p1 import get_session, _print_dict, _print_list, output, handle_error, _repl_help, cli  # noqa: F401,E501
from .audacity_cli_p2 import repl, auto_save_on_exit, project, project_new, project_open  # noqa: F401,E501
from .audacity_cli_p3 import project_save, project_info, project_settings, project_json, track, track_add, track_remove, track_list, track_set, clip, clip_import  # noqa: F401,E501
from .audacity_cli_p4 import clip_add, clip_remove, clip_trim, clip_split, clip_move, clip_list, effect_group, effect_list_available, effect_info  # noqa: F401,E501
from .audacity_cli_p5 import effect_add, effect_remove, effect_set, effect_list, selection, selection_set, selection_all, selection_none, selection_info, label, label_add  # noqa: F401,E501
from .audacity_cli_p6 import label_remove, label_list, media, media_probe, media_check, export_group, export_presets, export_preset_info, export_render, session_group, session_status, session_undo, session_redo, session_history  # noqa: F401,E501
from .audacity_cli_p7 import eval_cmd  # noqa: F401,E501
# fmt: on
