# ruff: noqa: F403, F405, E501
from .drawio_cli_base import *  # noqa: F403


if __name__ == "__main__":
    cli()

# fmt: off
# re-export full surface
from .drawio_cli_p1 import get_session, _print_dict, _print_list, output, handle_error, REPL_COMMANDS  # noqa: F401,E501
from .drawio_cli_p2 import _run_repl  # noqa: F401,E501
from .drawio_cli_p3 import cli, repl, project, session, project_new, project_open, project_save, project_info, project_xml, project_presets, shape, page  # noqa: F401,E501
from .drawio_cli_p4 import shape_add, shape_remove, shape_list, shape_label, shape_move, shape_resize, shape_style, shape_info, shape_types, connect, connect_add, connect_remove, connect_label, connect_style  # noqa: F401,E501
from .drawio_cli_p5 import connect_list, connect_styles, page_add, page_remove, page_rename, page_list, export, export_render, export_formats, session_status, session_undo, session_redo, session_save, session_list  # noqa: F401,E501
# fmt: on
