# ruff: noqa: F403, F405, E501
from .krita_cli_base import *  # noqa: F403
from .krita_cli_p5 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .krita_cli_p1 import _output, handle_error, _load_project, _save_current, cli, project  # noqa: F401,E501
from .krita_cli_p2 import repl  # noqa: F401,E501
from .krita_cli_p3 import project_new, project_open, project_save, project_info_cmd, layer, layer_add, layer_remove, layer_list  # noqa: F401,E501
from .krita_cli_p4 import layer_set, filter, filter_apply, filter_list, canvas, canvas_resize, canvas_info, export_group, export_render  # noqa: F401,E501
from .krita_cli_p5 import export_anim, export_presets, export_formats, session, session_undo, session_redo, session_history, status  # noqa: F401,E501
# fmt: on
