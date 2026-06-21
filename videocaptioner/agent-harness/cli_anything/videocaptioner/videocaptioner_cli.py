# ruff: noqa: F403, F405, E501
from .videocaptioner_cli_base import *  # noqa: F403
from .videocaptioner_cli_p5 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .videocaptioner_cli_p1 import _json_output, _repl_mode, output, handle_error, cli  # noqa: F401,E501
from .videocaptioner_cli_p2 import repl, transcribe  # noqa: F401,E501
from .videocaptioner_cli_p3 import subtitle, synthesize  # noqa: F401,E501
from .videocaptioner_cli_p4 import process, styles, review, config, config_show, config_set  # noqa: F401,E501
from .videocaptioner_cli_p5 import download, session, session_status  # noqa: F401,E501
# fmt: on
