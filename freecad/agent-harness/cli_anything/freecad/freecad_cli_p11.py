# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_indices, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p8 import sketch_group  # noqa: E402,E501
# fmt: on


@sketch_group.command("offset")
@click.argument("sketch_index", type=int)
@click.option("--elements", "-e", required=True, help="Element IDs (comma-sep).")
@click.option("--distance", "-d", required=True, type=float, help="Offset distance.")
@handle_error
def sketch_offset(sketch_index: int, elements: str, distance: float) -> None:
    """Offset wire elements by a distance."""
    sess = get_session()
    sess.snapshot(f"Offset elements in sketch #{sketch_index}")
    proj = sess.get_project()
    elem_ids = _parse_indices(elements)
    result = sketch_mod.offset_wire(
        proj, sketch_index, elem_ids=elem_ids, distance=distance
    )
    output_fn(result, "Offset elements")


@sketch_group.command("trim")
@click.argument("sketch_index", type=int)
@click.argument("elem_id", type=int)
@click.option(
    "--keep-side",
    default="start",
    type=click.Choice(["start", "end"]),
    help="Side to keep.",
)
@handle_error
def sketch_trim(sketch_index: int, elem_id: int, keep_side: str) -> None:
    """Trim a sketch element."""
    sess = get_session()
    sess.snapshot(f"Trim element {elem_id} in sketch #{sketch_index}")
    proj = sess.get_project()
    result = sketch_mod.trim_element(proj, sketch_index, elem_id, keep_side=keep_side)
    output_fn(result, f"Trimmed element {elem_id}")


@sketch_group.command("extend")
@click.argument("sketch_index", type=int)
@click.argument("elem_id", type=int)
@click.argument("target_elem_id", type=int)
@handle_error
def sketch_extend(sketch_index: int, elem_id: int, target_elem_id: int) -> None:
    """Extend a sketch element to a target element."""
    sess = get_session()
    sess.snapshot(f"Extend element {elem_id} in sketch #{sketch_index}")
    proj = sess.get_project()
    result = sketch_mod.extend_element(
        proj, sketch_index, elem_id, target_elem_id=target_elem_id
    )
    output_fn(result, f"Extended element {elem_id}")


@sketch_group.command("validate")
@click.argument("sketch_index", type=int)
@handle_error
def sketch_validate(sketch_index: int) -> None:
    """Validate a sketch for errors."""
    sess = get_session()
    proj = sess.get_project()
    result = sketch_mod.validate_sketch(proj, sketch_index)
    output_fn(result, "Sketch validation:")


@sketch_group.command("solve-status")
@click.argument("sketch_index", type=int)
@handle_error
def sketch_solve_status(sketch_index: int) -> None:
    """Show constraint solving status of a sketch."""
    sess = get_session()
    proj = sess.get_project()
    result = sketch_mod.solve_status(proj, sketch_index)
    output_fn(result, "Solve status:")


@sketch_group.command("set-construction")
@click.argument("sketch_index", type=int)
@click.argument("elem_id", type=int)
@click.option("--flag/--no-flag", default=True, help="Construction flag.")
@handle_error
def sketch_set_construction(sketch_index: int, elem_id: int, flag: bool) -> None:
    """Toggle construction geometry flag on an element."""
    sess = get_session()
    sess.snapshot(f"Set construction on element {elem_id}")
    proj = sess.get_project()
    result = sketch_mod.set_construction(proj, sketch_index, elem_id, flag=flag)
    output_fn(result, f"Set construction={flag} on element {elem_id}")


@sketch_group.command("project-external")
@click.argument("sketch_index", type=int)
@click.argument("part_index", type=int)
@click.option("--edge-ref", help="Edge reference (e.g. Edge1).")
@click.option(
    "--mode",
    type=click.Choice(["projection", "reference"]),
    default="projection",
    help="Projection mode (FreeCAD 1.1).",
)
@handle_error
def sketch_project_external(
    sketch_index: int, part_index: int, edge_ref: Optional[str], mode: str
) -> None:
    """Project external geometry into a sketch."""
    sess = get_session()
    sess.snapshot(f"Project external into sketch #{sketch_index}")
    proj = sess.get_project()
    result = sketch_mod.project_external(
        proj, sketch_index, part_index, edge_ref=edge_ref, mode=mode
    )
    output_fn(result, "Projected external geometry")


@sketch_group.command("intersection")
@click.argument("sketch_index", type=int)
@click.argument("body_index", type=int)
@handle_error
def sketch_intersection(sketch_index, body_index):
    """Create external geometry from sketch-plane intersection (FreeCAD 1.1)."""
    sess = get_session()
    proj = sess.get_project()
    result = sketch_mod.intersection_external(proj, sketch_index, body_index)
    output_fn(result, "Intersection reference created.")


@sketch_group.command("add-external-face")
@click.argument("sketch_index", type=int)
@click.argument("part_index", type=int)
@click.option("--face-ref", required=True, help="Face reference string")
@handle_error
def sketch_add_external_face(sketch_index, part_index, face_ref):
    """Create external geometry from face selection (FreeCAD 1.1)."""
    sess = get_session()
    proj = sess.get_project()
    result = sketch_mod.add_external_from_face(proj, sketch_index, part_index, face_ref)
    output_fn(result, "Face reference created.")
