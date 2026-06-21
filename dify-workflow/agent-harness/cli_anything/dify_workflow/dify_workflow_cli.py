# ruff: noqa: F403, F405, E501
from .dify_workflow_cli_base import *  # noqa: F403
from .dify_workflow_cli_p2 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .dify_workflow_cli_p1 import _configure_stdio, _emit, _forward, cli, repl, guide, list_node_types, create, inspect, validate, checklist, export, import_cmd, diff, layout, edit, edit_add_node, edit_remove_node, edit_update_node, edit_add_edge  # noqa: F401,E501
from .dify_workflow_cli_p2 import edit_remove_edge, edit_set_title, config, config_set_model, config_set_prompt, config_add_variable, config_set_opening, config_add_question, config_add_tool, config_remove_tool  # noqa: F401,E501
# fmt: on
