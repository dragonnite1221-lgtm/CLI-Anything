# ruff: noqa: F403, F405, E501
from .cloudanalyzer_cli_base import *  # noqa: F403
from .cloudanalyzer_cli_p6 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .cloudanalyzer_cli_p1 import _pretty, _out, _error, cli, _start_repl, evaluate, evaluate_run, evaluate_compare  # noqa: F401,E501
from .cloudanalyzer_cli_p2 import evaluate_diff, evaluate_ground, evaluate_batch, evaluate_pipeline, trajectory  # noqa: F401,E501
from .cloudanalyzer_cli_p3 import trajectory_evaluate, trajectory_batch, trajectory_run_evaluate, check, check_run  # noqa: F401,E501
from .cloudanalyzer_cli_p4 import check_init, baseline, baseline_decision, baseline_save, baseline_list, process, process_downsample, process_split, process_sample  # noqa: F401,E501
from .cloudanalyzer_cli_p5 import process_filter, process_merge, process_convert, inspect, inspect_view, inspect_web, inspect_web_export, info, info_show, info_version, session  # noqa: F401,E501
from .cloudanalyzer_cli_p6 import session_new, session_history  # noqa: F401,E501
# fmt: on
