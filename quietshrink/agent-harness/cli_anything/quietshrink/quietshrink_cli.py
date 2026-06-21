# ruff: noqa: F403, F405, E501
from .quietshrink_cli_base import *  # noqa: F403


if __name__ == "__main__":
    cli()

# fmt: off
# re-export full surface
from .quietshrink_cli_p1 import find_bash_cli, emit, cli, compress, probe  # noqa: F401,E501
from .quietshrink_cli_p2 import presets, doctor  # noqa: F401,E501
# fmt: on
