# ruff: noqa: F403, F405, E501
from .kdenlive_cli_base import *  # noqa: F403
from .kdenlive_cli_p6 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .kdenlive_cli_p1 import get_session, _print_dict, _print_list, output, handle_error, parse_time, cli  # noqa: F401,E501
from .kdenlive_cli_p2 import repl, auto_save_on_exit, project, project_new  # noqa: F401,E501
from .kdenlive_cli_p3 import project_open, project_save, project_info, project_profiles, project_json, bin_group, bin_import, bin_remove, bin_list, bin_get, timeline, timeline_add_track, timeline_remove_track  # noqa: F401,E501
from .kdenlive_cli_p4 import timeline_add_clip, timeline_remove_clip, timeline_trim, timeline_split, timeline_move, timeline_list, filter_group, filter_add, filter_remove  # noqa: F401,E501
from .kdenlive_cli_p5 import filter_set, filter_list, filter_available, transition, transition_add, transition_remove, transition_set, transition_list, guide  # noqa: F401,E501
from .kdenlive_cli_p6 import guide_add, guide_remove, guide_list, export, export_xml, export_presets, session, session_status, session_undo, session_redo, session_history  # noqa: F401,E501
# fmt: on
