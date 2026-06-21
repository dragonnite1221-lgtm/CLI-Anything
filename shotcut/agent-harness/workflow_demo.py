# ruff: noqa: F403, F405, E501
from .workflow_demo_base import *  # noqa: F403
from .workflow_demo_p2 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .workflow_demo_p1 import VIDEO, OUTPUT, PROJECT_FILE, _main_part0  # noqa: F401,E501
# fmt: on
