# ruff: noqa: F403, F405, E501
from .mermaid_cli_base import *  # noqa: F403
from .mermaid_cli_p2 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .mermaid_cli_p1 import get_session, emit, REPL_COMMANDS, cli, session, repl, project, project_new, project_open, project_save, project_info, project_samples, diagram, diagram_set  # noqa: F401,E501
from .mermaid_cli_p2 import diagram_show, export, export_render, export_share, session_status, session_undo, session_redo  # noqa: F401,E501
# fmt: on
