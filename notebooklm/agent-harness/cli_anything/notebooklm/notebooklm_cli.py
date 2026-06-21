# ruff: noqa: F403, F405, E501
from .notebooklm_cli_base import *  # noqa: F403
from .notebooklm_cli_p2 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .notebooklm_cli_p1 import get_session, emit, handle_error, resolve_notebook_id, cli, repl, auth, auth_status, auth_login, auth_check, notebook, notebook_list, notebook_create, notebook_summary, source, source_list, source_add_url, chat  # noqa: F401,E501
from .notebooklm_cli_p2 import chat_ask, chat_history, artifact, artifact_list, artifact_generate_report, download, download_report, share, share_status  # noqa: F401,E501
# fmt: on
