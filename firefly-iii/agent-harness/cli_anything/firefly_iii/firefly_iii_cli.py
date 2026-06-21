# ruff: noqa: F403, F405, E501
from .firefly_iii_cli_base import *  # noqa: F403
from .firefly_iii_cli_p2 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .firefly_iii_cli_p1 import get_backend, output, cli  # noqa: F401,E501
from .firefly_iii_cli_p2 import repl  # noqa: F401,E501
# fmt: on
