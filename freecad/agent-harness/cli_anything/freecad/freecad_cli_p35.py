# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_indices, _parse_params, _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p34 import assembly_group  # noqa: E402,E501
# fmt: on


@assembly_group.command("constrain")
@click.argument("asm_index", type=int)
@click.argument("constraint_type", type=str)
@click.option(
    "--components", "-c", required=True, help="Component indices (comma-sep)."
)
@click.option("--param", "-P", multiple=True, help="Param as key=value.")
@handle_error
def assembly_constrain(
    asm_index: int, constraint_type: str, components: str, param: tuple
) -> None:
    """Add a constraint between assembly components."""
    sess = get_session()
    sess.snapshot(f"Constrain assembly #{asm_index}")
    proj = sess.get_project()
    comp_indices = _parse_indices(components)
    params = {}
    for p in param:
        if "=" not in p:
            raise ValueError(f"Param must be key=value, got: {p}")
        k, v = p.split("=", 1)
        try:
            params[k.strip()] = float(v.strip())
        except ValueError:
            params[k.strip()] = v.strip()
    result = asm_mod.add_assembly_constraint(
        proj, asm_index, constraint_type, comp_indices, **params
    )
    output_fn(result, f"Added constraint: {constraint_type}")


@assembly_group.command("solve")
@click.argument("asm_index", type=int)
@handle_error
def assembly_solve(asm_index: int) -> None:
    """Solve assembly constraints."""
    sess = get_session()
    sess.snapshot(f"Solve assembly #{asm_index}")
    proj = sess.get_project()
    result = asm_mod.solve_assembly(proj, asm_index)
    output_fn(result, "Assembly solved")


@assembly_group.command("dof")
@click.argument("asm_index", type=int)
@handle_error
def assembly_dof(asm_index: int) -> None:
    """Estimate degrees of freedom for an assembly."""
    sess = get_session()
    proj = sess.get_project()
    result = asm_mod.degrees_of_freedom(proj, asm_index)
    output_fn(result, f"DOF: {result.get('dof', 'N/A')}")


@assembly_group.command("bom")
@click.argument("asm_index", type=int)
@handle_error
def assembly_bom(asm_index: int) -> None:
    """Generate bill of materials for an assembly."""
    sess = get_session()
    proj = sess.get_project()
    result = asm_mod.generate_bom(proj, asm_index)
    output_fn(result, "Bill of Materials:")


@assembly_group.command("explode")
@click.argument("asm_index", type=int)
@click.option("--factor", default=2.0, type=float, help="Explode factor.")
@handle_error
def assembly_explode(asm_index: int, factor: float) -> None:
    """Explode assembly for visualization."""
    sess = get_session()
    sess.snapshot(f"Explode assembly #{asm_index}")
    proj = sess.get_project()
    result = asm_mod.explode_assembly(proj, asm_index, factor=factor)
    output_fn(result, "Assembly exploded")


@assembly_group.command("collapse")
@click.argument("asm_index", type=int)
@handle_error
def assembly_collapse(asm_index: int) -> None:
    """Collapse (reset) assembly transforms."""
    sess = get_session()
    sess.snapshot(f"Collapse assembly #{asm_index}")
    proj = sess.get_project()
    result = asm_mod.collapse_assembly(proj, asm_index)
    output_fn(result, "Assembly collapsed")


@assembly_group.command("insert-part")
@click.argument("asm_index", type=int)
@click.option("--type", "part_type", default="box", help="Part type to insert")
@click.option("--name", default=None, help="Part name")
@click.option("-P", "--param", multiple=True, help="Parameters as key=value")
@click.option("--transform", default=None, help="Transform as x,y,z")
@handle_error
def assembly_insert_part(asm_index, part_type, name, param, transform):
    """Insert a new inline part into an assembly (FreeCAD 1.1)."""
    sess = get_session()
    proj = sess.get_project()
    params = _parse_params(param) if param else None
    t = _parse_vec3(transform) if transform else None
    result = asm_mod.insert_new_part(proj, asm_index, part_type, name, params, t)
    output_fn(result, "Part inserted into assembly.")


@assembly_group.command("create-simulation")
@click.argument("asm_index", type=int)
@click.option("--name", default=None, help="Simulation name")
@click.option("--duration", type=float, default=5.0, help="Duration in seconds")
@click.option("--fps", type=int, default=24, help="Frames per second")
@handle_error
def assembly_create_simulation(asm_index, name, duration, fps):
    """Create a joint motion simulation (FreeCAD 1.1)."""
    sess = get_session()
    proj = sess.get_project()
    result = asm_mod.create_simulation(proj, asm_index, name, duration, fps)
    output_fn(result, "Simulation created.")
