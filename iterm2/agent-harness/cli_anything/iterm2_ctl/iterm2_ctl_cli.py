# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403
from .iterm2_ctl_cli_p13 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .iterm2_ctl_cli_p1 import get_state, save_state_now, _print_data, output, handle_iterm2_error, cli  # noqa: F401,E501
from .iterm2_ctl_cli_p10 import session_wait_command_end, profile_list, profile_get, profile_color_presets, profile_apply_preset, arrangement, arrangement_list, arrangement_save, arrangement_restore, arrangement_save_window  # noqa: F401,E501
from .iterm2_ctl_cli_p11 import tmux, tmux_list, tmux_send, tmux_create_window, tmux_set_visible, tmux_tabs, tmux_bootstrap  # noqa: F401,E501
from .iterm2_ctl_cli_p12 import broadcast, broadcast_list, broadcast_set, broadcast_add, broadcast_clear, broadcast_all_panes, menu, menu_select, menu_state, menu_list_common, pref, pref_get, pref_set  # noqa: F401,E501
from .iterm2_ctl_cli_p13 import pref_tmux_get, pref_tmux_set, pref_list_keys, pref_theme  # noqa: F401,E501
from .iterm2_ctl_cli_p2 import repl  # noqa: F401,E501
from .iterm2_ctl_cli_p3 import app, app_status, app_current, app_context, app_set_context, app_clear_context, app_get_var, app_set_var  # noqa: F401,E501
from .iterm2_ctl_cli_p4 import app_alert, app_text_input, app_file_panel, app_save_panel, app_snapshot  # noqa: F401,E501
from .iterm2_ctl_cli_p5 import window, window_list, profile, window_create, window_close, window_activate, window_set_title, window_frame, window_set_frame  # noqa: F401,E501
from .iterm2_ctl_cli_p6 import window_fullscreen, tab, tab_list, tab_create, tab_close, tab_activate, tab_info, tab_select_pane, session  # noqa: F401,E501
from .iterm2_ctl_cli_p7 import session_list, session_send, session_screen, session_scrollback  # noqa: F401,E501
from .iterm2_ctl_cli_p8 import session_split, session_close, session_activate, session_set_name, session_restart, session_get_var, session_set_var, session_resize  # noqa: F401,E501
from .iterm2_ctl_cli_p9 import session_run_tmux_cmd, session_selection, session_inject, session_get_prompt, session_wait_prompt  # noqa: F401,E501
# fmt: on
