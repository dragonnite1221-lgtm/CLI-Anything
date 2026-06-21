# ruff: noqa: F403, F405, E501
from .obs_studio_cli_base import *  # noqa: F403
from .obs_studio_cli_p7 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .obs_studio_cli_p1 import get_session, _print_dict, _print_list, output, handle_error, _repl_help, cli  # noqa: F401,E501
from .obs_studio_cli_p2 import repl, auto_save_on_exit, project, project_new  # noqa: F401,E501
from .obs_studio_cli_p3 import project_open, project_save, project_info, project_json, scene_group, scene_add, scene_remove, scene_duplicate, scene_set_active, scene_list, source_group  # noqa: F401,E501
from .obs_studio_cli_p4 import source_add, source_remove, source_duplicate, source_set, source_transform, source_list  # noqa: F401,E501
from .obs_studio_cli_p5 import filter_group, filter_add, filter_remove, filter_set, filter_list, filter_list_available, audio_group, audio_add, audio_remove  # noqa: F401,E501
from .obs_studio_cli_p6 import audio_volume, audio_mute, audio_unmute, audio_monitor, audio_list, transition_group, transition_add, transition_remove, transition_set_active, transition_duration, transition_list, output_group  # noqa: F401,E501
from .obs_studio_cli_p7 import output_streaming, output_recording, output_settings, output_info, output_presets, session, session_status, session_undo, session_redo, session_history  # noqa: F401,E501
# fmt: on
