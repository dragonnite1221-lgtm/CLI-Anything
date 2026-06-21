# ruff: noqa: F403, F405, E501
from .unrealinsights_cli_base import *  # noqa: F403
from .unrealinsights_cli_p9 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .unrealinsights_cli_p1 import _repl_mode, _get_session, _output, _handle_exc, _resolve_insights, _resolve_trace_server, _require_trace, _human_backend, _human_ensure_insights, _human_trace_info, _human_export_result, _human_capture_result  # noqa: F401,E501
from .unrealinsights_cli_p2 import _human_capture_status, _human_snapshot_result, _human_stop_result, _human_store_info, _human_store_list, _human_store_latest, _human_processes, _human_live_result, _human_gui_status, _human_gui_open, _human_analyze_summary  # noqa: F401,E501
from .unrealinsights_cli_p3 import cli, repl, backend_group, backend_info  # noqa: F401,E501
from .unrealinsights_cli_p4 import backend_ensure_insights, trace_group, trace_set, trace_info, store_group, store_info, store_list, store_latest, capture_group  # noqa: F401,E501
from .unrealinsights_cli_p5 import capture_run, _prepare_capture_start, capture_start, capture_status_cmd  # noqa: F401,E501
from .unrealinsights_cli_p6 import capture_stop_cmd, capture_snapshot_cmd, live_group, live_processes, _run_live_command, live_exec, live_trace_status_cmd, live_bookmark, live_screenshot, live_snapshot, live_stop_trace, gui_group  # noqa: F401,E501
from .unrealinsights_cli_p7 import gui_status_cmd, gui_open_cmd, gui_open_latest, export_group, _run_export, export_threads, export_timers, export_timing_events  # noqa: F401,E501
from .unrealinsights_cli_p8 import export_timer_stats, export_timer_callees, export_counters, export_counter_values, batch_group, batch_run_rsp, analyze_group  # noqa: F401,E501
from .unrealinsights_cli_p9 import analyze_summary_cmd  # noqa: F401,E501
# fmt: on
