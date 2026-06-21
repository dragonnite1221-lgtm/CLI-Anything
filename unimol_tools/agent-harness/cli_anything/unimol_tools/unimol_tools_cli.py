# ruff: noqa: F403, F405, E501
from .unimol_tools_cli_base import *  # noqa: F403
from .unimol_tools_cli_p9 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .unimol_tools_cli_p1 import get_json_mode, output, handle_error, cli  # noqa: F401,E501
from .unimol_tools_cli_p2 import repl_cmd, project, project_new, project_info, project_set_dataset, train  # noqa: F401,E501
from .unimol_tools_cli_p3 import train_start, train_list, train_show, predict, predict_run  # noqa: F401,E501
from .unimol_tools_cli_p4 import predict_list, storage_analysis, models  # noqa: F401,E501
from .unimol_tools_cli_p5 import models_rank  # noqa: F401,E501
from .unimol_tools_cli_p6 import models_history, models_best  # noqa: F401,E501
from .unimol_tools_cli_p7 import models_compare  # noqa: F401,E501
from .unimol_tools_cli_p8 import cleanup_models  # noqa: F401,E501
from .unimol_tools_cli_p9 import archive_command  # noqa: F401,E501
# fmt: on
