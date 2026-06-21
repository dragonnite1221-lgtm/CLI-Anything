# ruff: noqa: F403, F405, E501
from .nsight_graphics_cli_base import *  # noqa: F403
from .nsight_graphics_cli_p6 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .nsight_graphics_cli_p1 import _output, _handle_exc, _common_kwargs, _print_gpu_trace_summary, _print_replay_analysis  # noqa: F401,E501
from .nsight_graphics_cli_p2 import cli, repl, doctor_group  # noqa: F401,E501
from .nsight_graphics_cli_p3 import doctor_info, doctor_versions, launch_group, launch_detached_cmd, launch_attach_cmd, frame_group  # noqa: F401,E501
from .nsight_graphics_cli_p4 import frame_capture_cmd, gpu_trace_group  # noqa: F401,E501
from .nsight_graphics_cli_p5 import gpu_trace_capture_cmd, gpu_trace_summarize_cmd, replay_group  # noqa: F401,E501
from .nsight_graphics_cli_p6 import replay_analyze_cmd, cpp_group, cpp_capture_cmd  # noqa: F401,E501
# fmt: on
