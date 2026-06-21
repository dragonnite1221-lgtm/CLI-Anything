# ruff: noqa: F403, F405, E501
from .browser_cli_base import *  # noqa: F403
from .browser_cli_p3 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .browser_cli_p1 import get_session, _print_dict, _print_list, output, handle_error, cli  # noqa: F401,E501
from .browser_cli_p2 import repl, page, page_open, page_reload, page_back, page_forward, page_info, fs  # noqa: F401,E501
from .browser_cli_p3 import fs_ls, fs_cd, fs_cat, fs_grep, fs_pwd, act, act_click, act_type, session, session_status, session_daemon_start, session_daemon_stop  # noqa: F401,E501
# fmt: on
