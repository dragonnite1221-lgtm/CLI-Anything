# ruff: noqa: F403, F405, E501
from .obsidian_cli_base import *  # noqa: F403
from .obsidian_cli_p4 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .obsidian_cli_p1 import _print_dict, _print_list, output, handle_error, _require_api_key, cli  # noqa: F401,E501
from .obsidian_cli_p2 import repl, vault, vault_list, vault_read, vault_create, vault_update, vault_delete  # noqa: F401,E501
from .obsidian_cli_p3 import vault_append, search, search_query, search_simple, note, note_active, note_open, command_group, command_list, command_execute, server, server_status  # noqa: F401,E501
from .obsidian_cli_p4 import session, session_status  # noqa: F401,E501
# fmt: on
