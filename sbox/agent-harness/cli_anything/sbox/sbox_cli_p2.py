# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _resolve_project_dir  # noqa: E402,E501
# fmt: on


def _resolve_collision_config(
    ctx: click.Context, config_path: Optional[str] = None
) -> str:
    """Resolve the Collision.config path from explicit arg, --project, or cwd."""
    if config_path:
        return config_path
    proj_dir = _resolve_project_dir(ctx)
    if proj_dir:
        return os.path.join(proj_dir, "ProjectSettings", "Collision.config")
    raise click.ClickException(
        "No project found. Use --project or run from a project directory."
    )


_REPL_BANNER = """
  ___  _  _____  __  __  ___ _    ___
 / __|| |/ _ \\ \\/ / / _|| | |_ _|
 \\__ \\| | (_) >  < | (__ | |_ | |
 |___/|_|\\___/_/\\_\\ \\___||___|___|

 cli-anything-sbox - interactive REPL
 Type 'help' for commands, 'quit' to exit.
"""
_REPL_HELP = """Available command groups:
  project      - Manage s&box projects (new, info, config, add-package, remove-package, validate)
  scene        - Manage scenes (new, info, list, add-object, remove-object, add-component,
                   remove-component, modify-object, set-property, clone-object, get-object,
                   set-navmesh, list-presets, modify-component, query, refs, bulk-modify,
                   diff, instantiate-prefab)
  prefab       - Manage prefabs (new, info, from-scene, add-component, remove-component, list,
                   refs, modify-component, diff)
  codegen      - Generate C# code (component, gameresource, editor-menu, razor, class,
                   panel-component)
  input        - Manage input bindings (list, add, remove, set)
  collision    - Manage collision layers (list, add-layer, add-rule, remove-rule, remove-layer)
  material     - Manage materials (new, info, list, set)
  sound        - Manage sound events (new, info, list, set)
  localization - Manage translation files (new, list, set, get, remove, bulk-set)
  server       - Server management (start, info)
  asset        - Asset management (list, info, compile, find-refs, find-unused, rename, move)
  session      - Session state (status, undo, redo)
  test         - Run automated map generation tests (setup, run)
  launch       - Open project in s&box editor

  help         - Show this help
  quit/exit    - Exit the REPL

Example: project info
         scene list Assets/scenes/minimal.scene
         codegen component --name PlayerMovement --methods OnUpdate,OnStart
"""


@click.group(invoke_without_command=True)
@click.option("--json", "json_output", is_flag=True, help="Output in JSON format")
@click.option("--project", "project_path", default=None, help="Project directory path")
@click.pass_context
def cli(ctx, json_output, project_path):
    """cli-anything-sbox - CLI harness for the s&box game engine."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output
    ctx.obj["project_path"] = project_path
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# fmt: off — deferred to break import cycle
from .sbox_cli_p3 import repl  # noqa: E402,E501
