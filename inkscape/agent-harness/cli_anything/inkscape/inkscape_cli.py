# ruff: noqa: F403, F405, E501
from .inkscape_cli_base import *  # noqa: F403
from .inkscape_cli_p8 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .inkscape_cli_p1 import get_session, _load_or_seed_project, _print_dict, _print_list, output, handle_error, _repl_help, _auto_save_callback  # noqa: F401,E501
from .inkscape_cli_p2 import cli, repl, document, document_new, document_open  # noqa: F401,E501
from .inkscape_cli_p3 import document_save, document_info, document_profiles, document_canvas_size, document_units, document_json, shape, style, shape_add_rect, shape_add_circle, shape_add_ellipse, shape_add_line, shape_add_polygon  # noqa: F401,E501
from .inkscape_cli_p4 import shape_add_path, shape_add_star, shape_remove, shape_duplicate, shape_list, shape_get, text, text_add, text_set, text_list, style_set_fill  # noqa: F401,E501
from .inkscape_cli_p5 import style_set_stroke, style_set_opacity, style_set, style_get, style_list_properties, transform, transform_translate, transform_rotate, transform_scale, transform_skew_x, transform_skew_y, transform_get, transform_clear  # noqa: F401,E501
from .inkscape_cli_p6 import layer, layer_add, layer_remove, layer_move_object, layer_set, layer_list, layer_reorder, layer_get, path_group, path_union, path_intersection, path_difference, path_exclusion, path_convert  # noqa: F401,E501
from .inkscape_cli_p7 import path_list_ops, gradient, gradient_add_linear, gradient_add_radial, gradient_apply, gradient_list, export_group, export_png, export_svg, export_pdf, export_presets, session, session_status, session_undo  # noqa: F401,E501
from .inkscape_cli_p8 import session_redo, session_history  # noqa: F401,E501
# fmt: on
