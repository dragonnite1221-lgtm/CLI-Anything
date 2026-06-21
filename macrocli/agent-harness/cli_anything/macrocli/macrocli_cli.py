# ruff: noqa: F403, F405, E501
from .macrocli_cli_base import *  # noqa: F403


if __name__ == "__main__":
    cli()

# fmt: off
# re-export full surface
from .macrocli_cli_p1 import get_runtime, get_session, _print_value, output, handle_error, _parse_params, cli  # noqa: F401,E501
from .macrocli_cli_p2 import repl, macro  # noqa: F401,E501
from .macrocli_cli_p3 import macro_run, macro_list  # noqa: F401,E501
from .macrocli_cli_p4 import macro_info, macro_validate, macro_dry_run  # noqa: F401,E501
from .macrocli_cli_p5 import macro_define  # noqa: F401,E501
from .macrocli_cli_p6 import macro_record  # noqa: F401,E501
from .macrocli_cli_p7 import macro_parameterize  # noqa: F401,E501
from .macrocli_cli_p8 import macro_assist, macro_capture_template, session  # noqa: F401,E501
from .macrocli_cli_p9 import session_status, session_history, session_save, session_list, backends  # noqa: F401,E501
# fmt: on
