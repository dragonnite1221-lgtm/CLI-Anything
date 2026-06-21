# ruff: noqa: F403, F405, E501
from .blender_cli_base import *  # noqa: F403

# fmt: off
from .blender_cli_p1 import get_session, output  # noqa: E402,E501
from .blender_cli_p2 import cli, handle_error  # noqa: E402,E501
from .blender_cli_p5 import material  # noqa: E402,E501
# fmt: on


@material.command("list")
@handle_error
def material_list():
    """List all materials."""
    sess = get_session()
    materials = mat_mod.list_materials(sess.get_project())
    output(materials, "Materials:")


@material.command("get")
@click.argument("index", type=int)
@handle_error
def material_get(index):
    """Get detailed info about a material."""
    sess = get_session()
    mat = mat_mod.get_material(sess.get_project(), index)
    output(mat)


@cli.group("modifier")
def modifier_group():
    """Modifier management commands."""
    pass


@modifier_group.command("list-available")
@click.option(
    "--category",
    "-c",
    type=str,
    default=None,
    help="Filter by category: generate, deform",
)
@handle_error
def modifier_list_available(category):
    """List all available modifiers."""
    modifiers = mod_mod.list_available(category)
    output(modifiers, "Available modifiers:")


@modifier_group.command("info")
@click.argument("name")
@handle_error
def modifier_info(name):
    """Show details about a modifier."""
    info = mod_mod.get_modifier_info(name)
    output(info)


@modifier_group.command("add")
@click.argument("modifier_type")
@click.option(
    "--object", "-o", "object_index", type=int, default=0, help="Object index"
)
@click.option("--name", "-n", default=None, help="Custom modifier name")
@click.option("--param", "-p", multiple=True, help="Parameter: key=value")
@handle_error
def modifier_add(modifier_type, object_index, name, param):
    """Add a modifier to an object."""
    params = {}
    for p in param:
        if "=" not in p:
            raise ValueError(f"Invalid param format: '{p}'. Use key=value.")
        k, v = p.split("=", 1)
        try:
            v = float(v) if "." in v else int(v)
        except ValueError:
            pass
        params[k] = v

    sess = get_session()
    sess.snapshot(f"Add modifier {modifier_type} to object {object_index}")
    result = mod_mod.add_modifier(
        sess.get_project(),
        modifier_type,
        object_index,
        name=name,
        params=params,
    )
    output(result, f"Added modifier: {result['name']}")


@modifier_group.command("remove")
@click.argument("modifier_index", type=int)
@click.option("--object", "-o", "object_index", type=int, default=0)
@handle_error
def modifier_remove(modifier_index, object_index):
    """Remove a modifier by index."""
    sess = get_session()
    sess.snapshot(f"Remove modifier {modifier_index} from object {object_index}")
    result = mod_mod.remove_modifier(sess.get_project(), modifier_index, object_index)
    output(result, f"Removed modifier {modifier_index}")


@modifier_group.command("set")
@click.argument("modifier_index", type=int)
@click.argument("param")
@click.argument("value")
@click.option("--object", "-o", "object_index", type=int, default=0)
@handle_error
def modifier_set(modifier_index, param, value, object_index):
    """Set a modifier parameter."""
    try:
        value = float(value) if "." in str(value) else int(value)
    except ValueError:
        pass
    sess = get_session()
    sess.snapshot(f"Set modifier {modifier_index} {param}={value}")
    mod_mod.set_modifier_param(
        sess.get_project(), modifier_index, param, value, object_index
    )
    output(
        {"modifier": modifier_index, "param": param, "value": value},
        f"Set modifier {modifier_index} {param} = {value}",
    )


@modifier_group.command("list")
@click.option("--object", "-o", "object_index", type=int, default=0)
@handle_error
def modifier_list(object_index):
    """List modifiers on an object."""
    sess = get_session()
    modifiers = mod_mod.list_modifiers(sess.get_project(), object_index)
    output(modifiers, f"Modifiers on object {object_index}:")


@cli.group()
def camera():
    """Camera management commands."""
    pass
