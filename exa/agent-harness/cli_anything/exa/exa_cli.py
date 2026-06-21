# ruff: noqa: F403, F405, E501
from .exa_cli_base import *  # noqa: F403
from .exa_cli_p3 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .exa_cli_p1 import _print_results, _pretty, _out, _err, _handle_errors, cli  # noqa: F401,E501
from .exa_cli_p2 import repl, _SEARCH_TYPES, _CONTENT_CHOICES, _FRESHNESS_CHOICES, _CATEGORY_CHOICES  # noqa: F401,E501
from .exa_cli_p3 import search_cmd, contents_cmd, server_group, server_status  # noqa: F401,E501
# fmt: on
