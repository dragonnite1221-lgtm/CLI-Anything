# ruff: noqa: F403, F405, E501
from .blender_cli_base import *  # noqa: F403

# fmt: off
from .blender_cli_p1 import get_session, output  # noqa: E402,E501
from .blender_cli_p2 import cli, handle_error  # noqa: E402,E501
from .blender_cli_p4 import object_group  # noqa: E402,E501
# fmt: on


@object_group.command("duplicate")
@click.argument("index", type=int)
@handle_error
def object_duplicate(index):
    """Duplicate an object."""
    sess = get_session()
    sess.snapshot(f"Duplicate object {index}")
    dup = obj_mod.duplicate_object(sess.get_project(), index)
    output(dup, f"Duplicated object {index}")


@object_group.command("transform")
@click.argument("index", type=int)
@click.option("--translate", "-t", default=None, help="Translate dx,dy,dz")
@click.option("--rotate", "-r", default=None, help="Rotate rx,ry,rz (degrees)")
@click.option("--scale", "-s", default=None, help="Scale sx,sy,sz (multiplier)")
@handle_error
def object_transform(index, translate, rotate, scale):
    """Transform an object (translate, rotate, scale)."""
    trans = [float(x) for x in translate.split(",")] if translate else None
    rot = [float(x) for x in rotate.split(",")] if rotate else None
    scl = [float(x) for x in scale.split(",")] if scale else None

    sess = get_session()
    sess.snapshot(f"Transform object {index}")
    obj = obj_mod.transform_object(
        sess.get_project(), index, translate=trans, rotate=rot, scale=scl
    )
    output(obj, f"Transformed object {index}: {obj['name']}")


@object_group.command("set")
@click.argument("index", type=int)
@click.argument("prop")
@click.argument("value")
@handle_error
def object_set(index, prop, value):
    """Set an object property (name, visible, location, rotation, scale, parent)."""
    sess = get_session()
    sess.snapshot(f"Set object {index} {prop}={value}")
    # Handle vector properties
    if prop in ("location", "rotation", "scale"):
        value = [float(x) for x in value.split(",")]
    obj_mod.set_object_property(sess.get_project(), index, prop, value)
    output(
        {"object": index, "property": prop, "value": value},
        f"Set object {index} {prop} = {value}",
    )


@object_group.command("list")
@handle_error
def object_list():
    """List all objects."""
    sess = get_session()
    objects = obj_mod.list_objects(sess.get_project())
    output(objects, "Objects:")


@object_group.command("get")
@click.argument("index", type=int)
@handle_error
def object_get(index):
    """Get detailed info about an object."""
    sess = get_session()
    obj = obj_mod.get_object(sess.get_project(), index)
    output(obj)


@cli.group()
def material():
    """Material management commands."""
    pass


@material.command("create")
@click.option("--name", "-n", default="Material", help="Material name")
@click.option("--color", "-c", default=None, help="Base color R,G,B,A (0.0-1.0)")
@click.option("--metallic", type=float, default=0.0, help="Metallic factor")
@click.option("--roughness", type=float, default=0.5, help="Roughness factor")
@click.option("--specular", type=float, default=0.5, help="Specular factor")
@handle_error
def material_create(name, color, metallic, roughness, specular):
    """Create a new material."""
    col = [float(x) for x in color.split(",")] if color else None
    sess = get_session()
    sess.snapshot(f"Create material: {name}")
    mat = mat_mod.create_material(
        sess.get_project(),
        name=name,
        color=col,
        metallic=metallic,
        roughness=roughness,
        specular=specular,
    )
    output(mat, f"Created material: {mat['name']}")


@material.command("assign")
@click.argument("material_index", type=int)
@click.argument("object_index", type=int)
@handle_error
def material_assign(material_index, object_index):
    """Assign a material to an object."""
    sess = get_session()
    sess.snapshot(f"Assign material {material_index} to object {object_index}")
    result = mat_mod.assign_material(sess.get_project(), material_index, object_index)
    output(result, f"Assigned {result['material']} to {result['object']}")


@material.command("set")
@click.argument("index", type=int)
@click.argument("prop")
@click.argument("value")
@handle_error
def material_set(index, prop, value):
    """Set a material property (color, metallic, roughness, specular, alpha, etc.)."""
    # Handle color properties
    if prop in ("color", "emission_color"):
        value = [float(x) for x in value.split(",")]
    elif prop == "use_backface_culling":
        pass  # handled by set_material_property
    else:
        try:
            value = float(value)
        except ValueError:
            pass
    sess = get_session()
    sess.snapshot(f"Set material {index} {prop}")
    mat_mod.set_material_property(sess.get_project(), index, prop, value)
    output(
        {"material": index, "property": prop, "value": value},
        f"Set material {index} {prop}",
    )
