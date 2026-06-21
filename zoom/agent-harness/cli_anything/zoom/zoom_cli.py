# ruff: noqa: F403, F405, E501
from .zoom_cli_base import *  # noqa: F403
from .zoom_cli_p5 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .zoom_cli_p1 import _print_dict, _print_list, output, handle_error, cli  # noqa: F401,E501
from .zoom_cli_p2 import repl, auth, auth_setup, auth_login, auth_status  # noqa: F401,E501
from .zoom_cli_p3 import auth_logout, meeting, meeting_create, meeting_list, meeting_info, meeting_update, meeting_delete, meeting_join  # noqa: F401,E501
from .zoom_cli_p4 import meeting_start, participant, participant_add, participant_add_batch, participant_list, participant_remove, participant_attended, recording, recording_list, recording_files  # noqa: F401,E501
from .zoom_cli_p5 import recording_download, recording_delete  # noqa: F401,E501
# fmt: on
