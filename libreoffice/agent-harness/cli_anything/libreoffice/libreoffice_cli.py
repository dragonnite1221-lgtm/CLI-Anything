# ruff: noqa: F403, F405, E501
from .libreoffice_cli_base import *  # noqa: F403
from .libreoffice_cli_p5 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .libreoffice_cli_p1 import get_session, _print_dict, _print_list, output, handle_error, _repl_help, cli  # noqa: F401,E501
from .libreoffice_cli_p2 import repl, auto_save_on_exit, document, document_new, document_open, document_import  # noqa: F401,E501
from .libreoffice_cli_p3 import document_import_formats, document_save, document_info, document_profiles, document_json, writer, writer_add_paragraph, writer_add_heading, writer_add_list, writer_add_table, writer_add_page_break, writer_remove, writer_list, writer_set_text, calc  # noqa: F401,E501
from .libreoffice_cli_p4 import calc_add_sheet, calc_remove_sheet, calc_rename_sheet, calc_set_cell, calc_get_cell, calc_list_sheets, impress, impress_add_slide, impress_remove_slide, impress_set_content, impress_list_slides, impress_add_element, style_group, _parse_props  # noqa: F401,E501
from .libreoffice_cli_p5 import style_create, style_modify, style_list, style_apply, style_remove, export_group, export_presets, export_preset_info, export_render, session, session_status, session_undo, session_redo, session_history  # noqa: F401,E501
# fmt: on
