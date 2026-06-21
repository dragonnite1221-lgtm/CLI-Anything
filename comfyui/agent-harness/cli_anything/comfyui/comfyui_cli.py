# ruff: noqa: F403, F405, E501
from .comfyui_cli_base import *  # noqa: F403
from .comfyui_cli_p3 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .comfyui_cli_p1 import _print_dict, _print_list, output, handle_error, cli, repl, workflow, workflow_list  # noqa: F401,E501
from .comfyui_cli_p2 import workflow_load, workflow_validate, queue, queue_prompt, queue_status, queue_clear, queue_history, queue_interrupt, models, models_checkpoints, models_loras, models_vaes, models_controlnets, models_node_info, models_list_nodes, images, images_list  # noqa: F401,E501
from .comfyui_cli_p3 import images_download, images_download_all, system, system_stats, system_info  # noqa: F401,E501
# fmt: on
