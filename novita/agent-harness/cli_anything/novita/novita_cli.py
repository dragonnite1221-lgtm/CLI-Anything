# ruff: noqa: F403, F405, E501
from .novita_cli_base import *  # noqa: F403
from .novita_cli_p4 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .novita_cli_p1 import get_session, _print_dict, _print_list, output, handle_error, cli  # noqa: F401,E501
from .novita_cli_p2 import repl, session, chat  # noqa: F401,E501
from .novita_cli_p3 import stream, session_status, session_clear, session_history, config, config_set, config_get  # noqa: F401,E501
from .novita_cli_p4 import config_delete, config_path, test, models  # noqa: F401,E501
# fmt: on
