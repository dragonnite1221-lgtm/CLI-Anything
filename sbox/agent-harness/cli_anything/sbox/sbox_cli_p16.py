# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_table, _output, _output_error, _resolve_input_config  # noqa: E402,E501
from .sbox_cli_p2 import _resolve_collision_config, cli  # noqa: E402,E501
from .sbox_cli_p15 import input_group  # noqa: E402,E501
# fmt: on


@input_group.command("remove")
@click.option("--name", required=True, help="Action name to remove")
@click.pass_context
def input_remove(ctx, name):
    """Remove an input action."""
    try:
        resolved = _resolve_input_config(ctx)
        removed = input_config_mod.remove_action(resolved, name)
        result = {"removed": removed, "name": name}
        if removed:
            _output(ctx, result, lambda d: f"Removed action '{d['name']}'")
        else:
            _output(ctx, result, lambda d: f"Action '{d['name']}' not found")
    except Exception as exc:
        _output_error(ctx, str(exc))


@input_group.command("set")
@click.option("--name", required=True, help="Action name to modify")
@click.option("--keyboard", default=None, help="New keyboard binding")
@click.option("--gamepad", default=None, help="New gamepad binding")
@click.option("--group", default=None, help="New group name")
@click.pass_context
def input_set(ctx, name, keyboard, gamepad, group):
    """Modify an input action."""
    try:
        resolved = _resolve_input_config(ctx)
        result = input_config_mod.set_action(
            config_path=resolved,
            name=name,
            keyboard_code=keyboard,
            gamepad_code=gamepad,
            group=group,
        )
        _output(ctx, result, lambda d: f"Updated action '{d.get('Name', '')}'")
    except Exception as exc:
        _output_error(ctx, str(exc))


@cli.group("collision")
@click.pass_context
def collision_group(ctx):
    """Manage s&box collision layers and rules."""
    pass


@collision_group.command("list")
@click.pass_context
def collision_list(ctx):
    """List collision layers and rules."""
    try:
        resolved = _resolve_collision_config(ctx)
        result = collision_config_mod.list_layers(resolved)
        if ctx.obj.get("json"):
            _output(ctx, result)
        else:
            click.echo("Layers:")
            defaults = result.get("defaults", {})
            for layer_name, default_val in defaults.items():
                click.echo(f"  {layer_name}: {default_val}")

            click.echo("")
            click.echo("Pair Rules:")
            pairs = result.get("pairs", [])
            if pairs:
                rows = []
                for p in pairs:
                    rows.append(
                        {
                            "layer_a": p.get("a", p.get("A", "")),
                            "layer_b": p.get("b", p.get("B", "")),
                            "result": p.get("r", p.get("Collide", "")),
                        }
                    )
                click.echo(_format_table(rows, ["layer_a", "layer_b", "result"]))
            else:
                click.echo("  (none)")
    except Exception as exc:
        _output_error(ctx, str(exc))


@collision_group.command("add-layer")
@click.option("--name", required=True, help="Layer name")
@click.option(
    "--default",
    "default_val",
    type=click.Choice(["Collide", "Trigger", "Ignore"]),
    default="Collide",
    help="Default collision behavior",
)
@click.pass_context
def collision_add_layer(ctx, name, default_val):
    """Add a collision layer."""
    try:
        resolved = _resolve_collision_config(ctx)
        result = collision_config_mod.add_layer(resolved, name, default=default_val)
        _output(
            ctx, result, lambda d: f"Added layer '{name}' with default '{default_val}'"
        )
    except Exception as exc:
        _output_error(ctx, str(exc))


@collision_group.command("add-rule")
@click.option("--layer-a", required=True, help="First layer")
@click.option("--layer-b", required=True, help="Second layer")
@click.option(
    "--result",
    type=click.Choice(["Collide", "Trigger", "Ignore"]),
    default="Collide",
    help="Collision result",
)
@click.pass_context
def collision_add_rule(ctx, layer_a, layer_b, result):
    """Add a collision pair rule."""
    try:
        resolved = _resolve_collision_config(ctx)
        rule = collision_config_mod.add_rule(resolved, layer_a, layer_b, result=result)
        _output(ctx, rule, lambda d: f"Rule: {layer_a} <-> {layer_b} = {result}")
    except Exception as exc:
        _output_error(ctx, str(exc))
