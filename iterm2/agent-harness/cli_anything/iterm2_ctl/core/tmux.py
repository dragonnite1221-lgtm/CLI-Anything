# ruff: noqa: F403, F405, E501
from .tmux_base import *  # noqa: F403

# fmt: off
# re-export full surface
from .tmux_p1 import _ensure_app_and_connections, _resolve_connection, list_connections, send_command, create_window, set_window_visible  # noqa: F401,E501
from .tmux_p2 import list_tmux_tabs, bootstrap, run_session_tmux_command  # noqa: F401,E501
# fmt: on
from . import tmux_base as _coupbase  # noqa: E402

_coupbase._COUP_GLOBALS = globals()  # noqa: E402
