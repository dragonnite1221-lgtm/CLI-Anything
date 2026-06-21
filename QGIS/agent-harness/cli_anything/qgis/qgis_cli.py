# ruff: noqa: F403, F405, E501
from .qgis_cli_base import *  # noqa: F403
from .qgis_cli_p5 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .qgis_cli_p1 import get_session, _print_dict, _print_list, output, _error_payload, handle_error, _requested_project_path, _current_project_modified, _sync_session_project_path, cli, session  # noqa: F401,E501
from .qgis_cli_p2 import repl, _load_requested_project, _active_project_path, _auto_save_if_one_shot, _record, project, project_new  # noqa: F401,E501
from .qgis_cli_p3 import project_open, project_save, project_info, project_set_crs, layer, layer_create_vector, layer_list, layer_info, layer_remove, feature, feature_add, feature_list, layout  # noqa: F401,E501
from .qgis_cli_p4 import layout_create, layout_list, layout_info, layout_remove, layout_add_map, layout_add_label, export, export_presets  # noqa: F401,E501
from .qgis_cli_p5 import export_pdf, export_image, process, process_list, process_help, process_run, session_status, session_history  # noqa: F401,E501
# fmt: on
