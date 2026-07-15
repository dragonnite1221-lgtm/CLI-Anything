# ruff: noqa: F403, F405, E501
from .cli_base import *  # noqa: F403
from .cli_base import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .cli_p1 import _invocation_command, _source_tag, install, uninstall, update  # noqa: F401,E501
from .cli_p2 import list_clis, search  # noqa: F401,E501
from .cli_p3 import info, launch, previews, preview_inspect, preview_html  # noqa: F401,E501
from .cli_p4 import _serve_live_session, preview_watch, preview_open  # noqa: F401,E501
# fmt: on
