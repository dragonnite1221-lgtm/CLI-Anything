# ruff: noqa: F403, F405, E501
from .session_server_base import *  # noqa: F403
from .session_server_p2 import main  # noqa: F401


if __name__ == "__main__":
    main(sys.argv[1:])

# fmt: off
# re-export full surface
from .session_server_p1 import _encode_token, _best_effort_chmod, _best_effort_restrict_windows_acl, _prepare_state_dir, _write_owner_only_json, _write_state_file, _remove_state_file, _recv_exact, _recv_message, _send_message, _validate_request  # noqa: F401,E501
from .session_server_p2 import SessionServer, serve  # noqa: F401,E501
# fmt: on
