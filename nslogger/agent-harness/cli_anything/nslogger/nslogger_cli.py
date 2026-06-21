# ruff: noqa: F403, F405, E501
from .nslogger_cli_base import *  # noqa: F403
from .nslogger_cli_p5 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .nslogger_cli_p1 import CONTEXT_SETTINGS, _level_option, _json_option, _parse_dt, _time_range_options, _listen_waiting_message, _format_live_output_message, _open_live_output_file, _REPL_COMMANDS, _FILE_COMMANDS, cli  # noqa: F401,E501
from .nslogger_cli_p2 import _run_repl, read  # noqa: F401,E501
from .nslogger_cli_p3 import filter_cmd, export, stats  # noqa: F401,E501
from .nslogger_cli_p4 import listen  # noqa: F401,E501
from .nslogger_cli_p5 import generate, tail, clients, blocks, merge, repl  # noqa: F401,E501
# fmt: on
