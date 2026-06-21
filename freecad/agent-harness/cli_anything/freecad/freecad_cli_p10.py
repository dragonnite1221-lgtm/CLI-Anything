# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_indices, _parse_points_2d, _parse_vec2, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p8 import sketch_group  # noqa: E402,E501
# fmt: on


@sketch_group.command("add-bspline")
@click.argument("sketch_index", type=int)
@click.argument("points_str", type=str)
@click.option("--closed", is_flag=True, help="Close the B-spline.")
@handle_error
def sketch_add_bspline(sketch_index: int, points_str: str, closed: bool) -> None:
    """Add a B-spline to a sketch (semicolon-separated x,y points)."""
    sess = get_session()
    sess.snapshot(f"Add bspline to sketch #{sketch_index}")
    proj = sess.get_project()
    pts = _parse_points_2d(points_str)
    result = sketch_mod.add_bspline(proj, sketch_index, points=pts, closed=closed)
    output_fn(result, "Added B-spline")


@sketch_group.command("add-slot")
@click.argument("sketch_index", type=int)
@click.option("--center1", default="0,0", help="First center x,y.")
@click.option("--center2", default="10,0", help="Second center x,y.")
@click.option("--radius", "-r", default=2.0, type=float, help="Radius.")
@handle_error
def sketch_add_slot(
    sketch_index: int, center1: str, center2: str, radius: float
) -> None:
    """Add a slot (obround) shape to a sketch."""
    sess = get_session()
    sess.snapshot(f"Add slot to sketch #{sketch_index}")
    proj = sess.get_project()
    c1 = _parse_vec2(center1)
    c2 = _parse_vec2(center2)
    result = sketch_mod.add_slot(
        proj, sketch_index, center1=c1, center2=c2, radius=radius
    )
    output_fn(result, "Added slot")


@sketch_group.command("edit-element")
@click.argument("sketch_index", type=int)
@click.argument("elem_id", type=int)
@click.option("--param", "-P", multiple=True, help="Property as key=value.")
@handle_error
def sketch_edit_element(sketch_index: int, elem_id: int, param: tuple) -> None:
    """Edit a sketch element's properties."""
    sess = get_session()
    sess.snapshot(f"Edit element {elem_id} in sketch #{sketch_index}")
    proj = sess.get_project()
    props = {}
    for p in param:
        if "=" not in p:
            raise ValueError(f"Param must be key=value, got: {p}")
        k, v = p.split("=", 1)
        k = k.strip()
        v = v.strip()
        if k in ("start", "end", "center", "position"):
            props[k] = _parse_vec2(v)
        elif k == "radius":
            props[k] = float(v)
        else:
            try:
                props[k] = float(v)
            except ValueError:
                props[k] = v
    result = sketch_mod.edit_element(proj, sketch_index, elem_id, **props)
    output_fn(result, f"Edited element {elem_id}")


@sketch_group.command("remove-element")
@click.argument("sketch_index", type=int)
@click.argument("elem_id", type=int)
@handle_error
def sketch_remove_element(sketch_index: int, elem_id: int) -> None:
    """Remove an element from a sketch."""
    sess = get_session()
    sess.snapshot(f"Remove element {elem_id} from sketch #{sketch_index}")
    proj = sess.get_project()
    result = sketch_mod.remove_element(proj, sketch_index, elem_id)
    output_fn(result, f"Removed element {elem_id}")


@sketch_group.command("remove-constraint")
@click.argument("sketch_index", type=int)
@click.argument("constraint_id", type=int)
@handle_error
def sketch_remove_constraint(sketch_index: int, constraint_id: int) -> None:
    """Remove a constraint from a sketch."""
    sess = get_session()
    sess.snapshot(f"Remove constraint {constraint_id} from sketch #{sketch_index}")
    proj = sess.get_project()
    result = sketch_mod.remove_constraint(proj, sketch_index, constraint_id)
    output_fn(result, f"Removed constraint {constraint_id}")


@sketch_group.command("edit-constraint")
@click.argument("sketch_index", type=int)
@click.argument("constraint_id", type=int)
@click.option("--value", "-v", type=float, help="New constraint value.")
@handle_error
def sketch_edit_constraint(
    sketch_index: int, constraint_id: int, value: Optional[float]
) -> None:
    """Edit a constraint value."""
    sess = get_session()
    sess.snapshot(f"Edit constraint {constraint_id} in sketch #{sketch_index}")
    proj = sess.get_project()
    result = sketch_mod.edit_constraint(proj, sketch_index, constraint_id, value=value)
    output_fn(result, f"Edited constraint {constraint_id}")


@sketch_group.command("mirror")
@click.argument("sketch_index", type=int)
@click.option("--elements", "-e", required=True, help="Element IDs (comma-sep).")
@click.option("--axis-elem-id", required=True, type=int, help="Axis element ID.")
@handle_error
def sketch_mirror(sketch_index: int, elements: str, axis_elem_id: int) -> None:
    """Mirror elements about an axis element."""
    sess = get_session()
    sess.snapshot(f"Mirror elements in sketch #{sketch_index}")
    proj = sess.get_project()
    elem_ids = _parse_indices(elements)
    result = sketch_mod.mirror_elements(
        proj, sketch_index, elem_ids=elem_ids, axis_elem_id=axis_elem_id
    )
    output_fn(result, "Mirrored elements")
