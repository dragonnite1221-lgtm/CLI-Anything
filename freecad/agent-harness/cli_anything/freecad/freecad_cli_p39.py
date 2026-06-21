# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p38 import fem_group  # noqa: E402,E501
# fmt: on


@fem_group.command("set-material")
@click.argument("ai", type=int)
@click.argument("material_index", type=int)
@handle_error
def fem_set_material(ai: int, material_index: int) -> None:
    """Assign a material to an analysis."""
    sess = get_session()
    sess.snapshot(f"Set material on analysis #{ai}")
    proj = sess.get_project()
    result = fem_mod.set_fem_material(proj, ai, material_index)
    output_fn(result, "Material assigned to analysis")


@fem_group.command("mesh-generate")
@click.argument("ai", type=int)
@click.option("--max-size", type=float, help="Max element size.")
@click.option("--min-size", type=float, help="Min element size.")
@click.option("--element-type", default="Tet10", help="Element type.")
@click.option(
    "--mesher",
    type=click.Choice(["gmsh", "netgen"]),
    default="gmsh",
    help="Mesher backend (FreeCAD 1.1).",
)
@click.option(
    "--gmsh-verbosity", type=int, default=1, help="Gmsh verbosity level (FreeCAD 1.1)."
)
@click.option(
    "--second-order-linear",
    is_flag=True,
    help="Second order linear elements (FreeCAD 1.1).",
)
@click.option(
    "--local-refinement",
    type=str,
    default=None,
    help="Local refinement as JSON string (FreeCAD 1.1).",
)
@handle_error
def fem_mesh_generate(
    ai: int,
    max_size: Optional[float],
    min_size: Optional[float],
    element_type: str,
    mesher: str,
    gmsh_verbosity: int,
    second_order_linear: bool,
    local_refinement: Optional[str],
) -> None:
    """Configure mesh generation for an analysis."""
    sess = get_session()
    sess.snapshot(f"Generate FEM mesh for analysis #{ai}")
    proj = sess.get_project()
    lr = json.loads(local_refinement) if local_refinement else None
    result = fem_mod.generate_fem_mesh(
        proj,
        ai,
        max_size=max_size,
        min_size=min_size,
        element_type=element_type,
        mesher=mesher,
        gmsh_verbosity=gmsh_verbosity,
        second_order_linear=second_order_linear,
        local_refinement=lr,
    )
    output_fn(result, "Mesh parameters set")


@fem_group.command("solve")
@click.argument("ai", type=int)
@click.option(
    "--solver", default="calculix", type=click.Choice(["calculix", "elmer", "z88"])
)
@click.option(
    "--output-format",
    type=click.Choice(["vtu", "vtk", "result"]),
    default=None,
    help="Output format (FreeCAD 1.1).",
)
@click.option(
    "--buckling-accuracy",
    type=float,
    default=None,
    help="Buckling accuracy (FreeCAD 1.1).",
)
@handle_error
def fem_solve(
    ai: int,
    solver: str,
    output_format: Optional[str],
    buckling_accuracy: Optional[float],
) -> None:
    """Solve a FEM analysis."""
    sess = get_session()
    sess.snapshot(f"Solve analysis #{ai}")
    proj = sess.get_project()
    result = fem_mod.solve_fem(
        proj,
        ai,
        solver=solver,
        output_format=output_format,
        buckling_accuracy=buckling_accuracy,
    )
    output_fn(result, "Analysis solver configured")


@fem_group.command("results")
@click.argument("ai", type=int)
@handle_error
def fem_results(ai: int) -> None:
    """Get FEM analysis results."""
    sess = get_session()
    proj = sess.get_project()
    result = fem_mod.get_fem_results(proj, ai)
    output_fn(result, "FEM results:")


@fem_group.command("export-results")
@click.argument("ai", type=int)
@click.argument("path", type=click.Path())
@click.option(
    "--format", "fmt", default="vtk", type=click.Choice(["vtk", "csv", "json"])
)
@handle_error
def fem_export_results(ai: int, path: str, fmt: str) -> None:
    """Export FEM results."""
    sess = get_session()
    proj = sess.get_project()
    result = fem_mod.export_fem_results(proj, ai, path, format=fmt)
    output_fn(result, f"Exported results: {path}")


@fem_group.command("add-beam-section")
@click.argument("analysis_index", type=int)
@click.option(
    "--section-type",
    type=click.Choice(["rectangular", "circular", "box_beam", "elliptical", "pipe"]),
    default="rectangular",
)
@click.option("--references", default=None, help="Comma-separated geometry refs")
@click.option("--width", type=float, default=None)
@click.option("--height", type=float, default=None)
@click.option("--radius", type=float, default=None)
@handle_error
def fem_add_beam_section(
    analysis_index, section_type, references, width, height, radius
):
    """Add an ElementGeometry1D beam section (FreeCAD 1.1)."""
    sess = get_session()
    proj = sess.get_project()
    refs = references.split(",") if references else None
    result = fem_mod.add_beam_section(
        proj, analysis_index, section_type, refs, width, height, radius
    )
    output_fn(result, "Beam section added.")
