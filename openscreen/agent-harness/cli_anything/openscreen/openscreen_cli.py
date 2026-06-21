# ruff: noqa: F403, F405, E501
from .openscreen_cli_base import *  # noqa: F403


if __name__ == "__main__":
    cli()

# fmt: off
# re-export full surface
from .openscreen_cli_p1 import _session, _json_output, _repl_mode, _auto_save, _dry_run, _print_dict, _print_list, output, handle_error, _repl_zoom, _repl_speed  # noqa: F401,E501
from .openscreen_cli_p2 import _repl_trim, cli  # noqa: F401,E501
from .openscreen_cli_p3 import repl  # noqa: F401,E501
from .openscreen_cli_p4 import project, project_new, project_open, project_save, project_info, project_set_video, project_set, zoom, zoom_list, zoom_add, zoom_remove, speed, speed_list, speed_add  # noqa: F401,E501
from .openscreen_cli_p5 import speed_remove, trim, trim_list, trim_add, trim_remove, crop, crop_get, crop_set, annotation, annotation_list, annotation_add_text, annotation_remove, media, media_probe, media_check, media_thumbnail  # noqa: F401,E501
from .openscreen_cli_p6 import export, preview, export_presets, export_render, preview_recipes, preview_capture, preview_latest, session_group, session_status, session_undo, session_redo, session_save_state, session_list  # noqa: F401,E501
# fmt: on
