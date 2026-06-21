# ruff: noqa: F403, F405, E501
from .musescore_cli_base import *  # noqa: F403
from .musescore_cli_p5 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .musescore_cli_p1 import _print_dict, _print_list, output, handle_error, _repl_help, cli  # noqa: F401,E501
from .musescore_cli_p2 import repl, auto_save_on_exit, project, project_open, project_info, project_save, transpose  # noqa: F401,E501
from .musescore_cli_p3 import transpose_by_key, transpose_by_interval, transpose_diatonic, parts, parts_list  # noqa: F401,E501
from .musescore_cli_p4 import parts_extract, parts_generate, export_group, _make_export_cmd, export_batch, export_verify, instruments, instruments_list, instruments_add  # noqa: F401,E501
from .musescore_cli_p5 import instruments_remove, instruments_reorder, media, media_probe, media_diff, media_stats, session_group, session_status, session_undo, session_redo, session_history  # noqa: F401,E501
# fmt: on
