# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p12 import body_group  # noqa: E402,E501
# fmt: on


@body_group.command("toggle-freeze")
@click.argument("body_index", type=int)
@click.argument("feature_index", type=int)
@handle_error
def body_toggle_freeze(body_index, feature_index):
    """Toggle frozen state of a feature (FreeCAD 1.1)."""
    sess = get_session()
    proj = sess.get_project()
    result = body_mod.toggle_freeze(proj, body_index, feature_index)
    state = "frozen" if result.get("frozen") else "unfrozen"
    output_fn(result, f"Feature {feature_index} is now {state}.")


@cli.group("material")
def material_group():
    """Material management commands."""
    pass


@material_group.command("create")
@click.option("--name", "-n", default="Material", help="Material name.")
@click.option("--preset", help="Use a material preset.")
@click.option("--color", help="Color as r,g,b,a (0.0-1.0).")
@click.option("--metallic", type=float, help="Metallic factor (0-1).")
@click.option("--roughness", type=float, help="Roughness factor (0-1).")
@handle_error
def material_create(
    name: str,
    preset: Optional[str],
    color: Optional[str],
    metallic: Optional[float],
    roughness: Optional[float],
) -> None:
    """Create a new material."""
    sess = get_session()
    sess.snapshot(f"Create material: {name}")
    proj = sess.get_project()
    c = [float(x) for x in color.split(",")] if color else None
    kwargs: dict[str, Any] = {"name": name}
    if preset:
        kwargs["preset"] = preset
    if c:
        kwargs["color"] = c
    if metallic is not None:
        kwargs["metallic"] = metallic
    if roughness is not None:
        kwargs["roughness"] = roughness
    result = mat_mod.create_material(proj, **kwargs)
    output_fn(result, f"Created material: {result.get('name', name)}")


@material_group.command("assign")
@click.argument("material_index", type=int)
@click.argument("part_index", type=int)
@handle_error
def material_assign(material_index: int, part_index: int) -> None:
    """Assign a material to a part."""
    sess = get_session()
    sess.snapshot(f"Assign material #{material_index} to part #{part_index}")
    proj = sess.get_project()
    result = mat_mod.assign_material(proj, material_index, part_index)
    output_fn(result, "Material assigned")


@material_group.command("list")
@handle_error
def material_list() -> None:
    """List all materials."""
    sess = get_session()
    proj = sess.get_project()
    result = mat_mod.list_materials(proj)
    output_fn(result, f"{len(result)} material(s):")


@material_group.command("get")
@click.argument("index", type=int)
@handle_error
def material_get(index: int) -> None:
    """Get material details."""
    sess = get_session()
    proj = sess.get_project()
    result = mat_mod.get_material(proj, index)
    output_fn(result, f"Material #{index}:")


@material_group.command("set")
@click.argument("index", type=int)
@click.argument("prop")
@click.argument("value")
@handle_error
def material_set(index: int, prop: str, value: str) -> None:
    """Set a material property."""
    sess = get_session()
    sess.snapshot(f"Set material #{index} {prop}")
    proj = sess.get_project()
    if prop == "color":
        val: Any = [float(x) for x in value.split(",")]
    elif prop in ("metallic", "roughness"):
        val = float(value)
    else:
        val = value
    mat_mod.set_material_property(proj, index, prop, val)
    result = mat_mod.get_material(proj, index)
    output_fn(result, f"Updated material #{index}")


@material_group.command("presets")
@handle_error
def material_presets() -> None:
    """List available material presets."""
    result = mat_mod.list_presets()
    output_fn(result, "Available presets:")


@material_group.command("import-material")
@click.argument("path", type=click.Path())
@handle_error
def material_import(path: str) -> None:
    """Import a material from a JSON file."""
    sess = get_session()
    sess.snapshot("Import material")
    proj = sess.get_project()
    result = mat_mod.import_material(proj, path)
    output_fn(result, f"Imported material: {result.get('name', '')}")
