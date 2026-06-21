# ruff: noqa: F403, F405, E501
from .anygen_cli_base import *  # noqa: F403
from .anygen_cli_p5 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .anygen_cli_p1 import get_session, _print_dict, _print_list, output, handle_error, cli  # noqa: F401,E501
from .anygen_cli_p2 import repl, task, task_create, task_status  # noqa: F401,E501
from .anygen_cli_p3 import task_poll, task_download, task_thumbnail, task_run, task_list  # noqa: F401,E501
from .anygen_cli_p4 import task_prepare, file, file_upload, config, config_set, config_get  # noqa: F401,E501
from .anygen_cli_p5 import config_delete, config_path, session, session_status, session_history, session_undo, session_redo  # noqa: F401,E501
# fmt: on
