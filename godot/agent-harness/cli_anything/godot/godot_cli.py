# ruff: noqa: F403, F405, E501
from .godot_cli_base import *  # noqa: F403
from .godot_cli_p3 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .godot_cli_p1 import _out, _handle_error, cli, project, _get_project, project_create, project_info, project_scenes, project_scripts, project_resources, project_reimport, scene, scene_create, scene_read  # noqa: F401,E501
from .godot_cli_p2 import scene_add_node, export_group, export_build, export_presets, script, script_run, script_inline, script_validate, engine, engine_version, engine_status  # noqa: F401,E501
from .godot_cli_p3 import session  # noqa: F401,E501
# fmt: on
