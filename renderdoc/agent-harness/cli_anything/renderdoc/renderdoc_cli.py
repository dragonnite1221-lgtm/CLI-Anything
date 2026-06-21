# ruff: noqa: F403, F405, E501
from .renderdoc_cli_base import *  # noqa: F403
from .renderdoc_cli_p9 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .renderdoc_cli_p1 import _capture_handle_b, _capture_handle_b_path, _close_all_captures, _get_export_dir, _get_handle, _output, cli  # noqa: F401,E501
from .renderdoc_cli_p2 import repl, capture_group, capture_info, capture_thumb, capture_convert, actions_group  # noqa: F401,E501
from .renderdoc_cli_p3 import actions_list, actions_summary, actions_find, actions_get, textures_group, textures_list, textures_get, textures_save  # noqa: F401,E501
from .renderdoc_cli_p4 import textures_save_outputs, textures_pick, pipeline_group, pipeline_state, pipeline_shader_export  # noqa: F401,E501
from .renderdoc_cli_p5 import pipeline_dump_shader_reflection, pipeline_dump  # noqa: F401,E501
from .renderdoc_cli_p6 import pipeline_cbuffer, resources_group, resources_list, resources_buffers, resources_read_buffer, mesh_group, mesh_inputs, mesh_outputs, counters_group, counters_list  # noqa: F401,E501
from .renderdoc_cli_p7 import counters_fetch, _get_handle_b  # noqa: F401,E501
from .renderdoc_cli_p8 import pipeline_diff_cmd, preview_group, preview_recipes  # noqa: F401,E501
from .renderdoc_cli_p9 import preview_capture_cmd, preview_diff_cmd, preview_latest_cmd, cleanup  # noqa: F401,E501
# fmt: on
