# ruff: noqa: F403, F405, E501
from .pm2_cli_base import *  # noqa: F403
from .pm2_cli_p3 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .pm2_cli_p1 import _output, lifecycle_mod, lifecycle_module, _repl_start, _repl_logs_view  # noqa: F401,E501
from .pm2_cli_p2 import _run_repl, process, process_list, process_describe, process_metrics, lifecycle, lifecycle_restart, lifecycle_stop  # noqa: F401,E501
from .pm2_cli_p3 import lifecycle_start, lifecycle_delete, _init_lifecycle_mod, logs_group, logs_view, logs_flush, system_group, system_save, system_startup, system_version  # noqa: F401,E501
# fmt: on
