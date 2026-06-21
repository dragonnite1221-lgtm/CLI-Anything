# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_table, _output, _output_error, _resolve_input_config  # noqa: E402,E501
from .sbox_cli_p2 import cli  # noqa: E402,E501
from .sbox_cli_p12 import codegen  # noqa: E402,E501
# fmt: on


@codegen.command("panel-component")
@click.option("--name", required=True, help="PanelComponent class name (PascalCase)")
@click.option("--namespace", default=None, help="Optional C# namespace")
@click.option(
    "--properties", default=None, help="Properties as JSON array (same format as razor)"
)
@click.option(
    "--root-class", default=None, help="CSS root class (default: kebab-case of name)"
)
@click.option(
    "--z-index",
    "z_index",
    type=int,
    default=100,
    help="ScreenPanel ZIndex (default 100)",
)
@click.option(
    "--opacity", type=float, default=1.0, help="ScreenPanel Opacity (default 1.0)"
)
@click.option(
    "-o",
    "--output",
    "output_path",
    default=None,
    help="Output .razor file path (also writes .razor.scss)",
)
@click.option(
    "--scene",
    "scene_path",
    default=None,
    help="Optional scene to append the GameObject snippet to",
)
@click.pass_context
def codegen_panel_component(
    ctx,
    name,
    namespace,
    properties,
    root_class,
    z_index,
    opacity,
    output_path,
    scene_path,
):
    """Scaffold a PanelComponent + sibling ScreenPanel on the same GameObject.

    Handles the s&box quirk where PanelComponent input requires both components
    on the same GameObject. Emits .razor + .razor.scss + a paste-ready GameObject
    JSON snippet, and can optionally append the GameObject directly to a scene.
    """
    try:
        props = json.loads(properties) if properties else None
        result = codegen_mod.generate_panel_component(
            name,
            properties=props,
            namespace=namespace,
            z_index=z_index,
            opacity=opacity,
            root_class=root_class,
        )

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["content"])
            scss_path = os.path.join(
                os.path.dirname(output_path), result["scss_filename"]
            )
            with open(scss_path, "w", encoding="utf-8") as f:
                f.write(result["scss_content"])
            result["razor_path"] = os.path.abspath(output_path)
            result["scss_path"] = os.path.abspath(scss_path)

        if scene_path:
            scene_data = scene_mod.load_scene(scene_path)
            snippet_obj = json.loads(result["scene_snippet"])
            scene_data.setdefault("GameObjects", []).append(snippet_obj)
            scene_mod.save_scene(scene_path, scene_data)
            result["scene_appended_to"] = os.path.abspath(scene_path)

        def human(d):
            lines = [f"PanelComponent '{d['class_name']}' generated"]
            if d.get("razor_path"):
                lines.append(f"  razor: {d['razor_path']}")
                lines.append(f"  scss:  {d['scss_path']}")
            if d.get("scene_appended_to"):
                lines.append(
                    f"  scene: appended to {d['scene_appended_to']} (object_guid={d['object_guid']})"
                )
            else:
                lines.append(
                    "  Paste the snippet under GameObjects in your .scene to wire it up."
                )
            return "\n".join(lines)

        _output(ctx, result, human)
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@cli.group("input")
@click.pass_context
def input_group(ctx):
    """Manage s&box input action bindings."""
    pass


@input_group.command("list")
@click.argument("config_path", required=False, default=None)
@click.pass_context
def input_list(ctx, config_path):
    """List input actions."""
    try:
        resolved = _resolve_input_config(ctx, config_path)
        actions = input_config_mod.list_actions(resolved)
        if ctx.obj.get("json"):
            _output(ctx, actions)
        else:
            rows = []
            for a in actions:
                rows.append(
                    {
                        "name": a.get("Name", ""),
                        "group": a.get("GroupName", ""),
                        "keyboard": a.get("KeyboardCode", ""),
                        "gamepad": a.get("GamepadCode", ""),
                    }
                )
            click.echo(_format_table(rows, ["name", "group", "keyboard", "gamepad"]))
    except Exception as exc:
        _output_error(ctx, str(exc))


@input_group.command("add")
@click.option("--name", required=True, help="Action name")
@click.option("--group", default="Other", help="Group name")
@click.option("--keyboard", default="None", help="Keyboard binding")
@click.option("--gamepad", default="None", help="Gamepad binding")
@click.option("--title", default=None, help="Display title")
@click.pass_context
def input_add(ctx, name, group, keyboard, gamepad, title):
    """Add an input action."""
    try:
        resolved = _resolve_input_config(ctx)
        result = input_config_mod.add_action(
            config_path=resolved,
            name=name,
            group=group,
            keyboard_code=keyboard,
            gamepad_code=gamepad,
            title=title,
        )
        _output(
            ctx,
            result,
            lambda d: (
                f"Added action '{d.get('Name', '')}' in group '{d.get('GroupName', '')}'"
            ),
        )
    except Exception as exc:
        _output_error(ctx, str(exc))
