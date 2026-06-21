# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_vec2, _parse_vec3, cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p34 import assembly_group  # noqa: E402,E501
# fmt: on


@assembly_group.command("add-sim-step")
@click.argument("asm_index", type=int)
@click.argument("sim_index", type=int)
@click.option("--joint", type=int, required=True, help="Joint index")
@click.option("--start", type=float, default=0.0, help="Start value")
@click.option("--end", type=float, default=1.0, help="End value")
@handle_error
def assembly_add_sim_step(asm_index, sim_index, joint, start, end):
    """Add a motion step to a simulation (FreeCAD 1.1)."""
    sess = get_session()
    proj = sess.get_project()
    result = asm_mod.add_simulation_step(proj, asm_index, sim_index, joint, start, end)
    output_fn(result, "Simulation step added.")


@cli.group("techdraw")
def techdraw_group():
    """Technical drawing commands."""
    pass


@techdraw_group.command("new-page")
@click.option("--name", "-n", help="Page name.")
@click.option("--template", default="A4_LandscapeTD", help="Drawing template.")
@handle_error
def techdraw_new_page(name: Optional[str], template: str) -> None:
    """Create a new TechDraw page."""
    sess = get_session()
    sess.snapshot("New TechDraw page")
    proj = sess.get_project()
    result = td_mod.new_page(proj, name=name, template=template)
    output_fn(result, f"Created page: {result.get('name', '')}")


@techdraw_group.command("set-template")
@click.argument("page_index", type=int)
@click.argument("template", type=str)
@handle_error
def techdraw_set_template(page_index: int, template: str) -> None:
    """Change the template of a page."""
    sess = get_session()
    sess.snapshot(f"Set template on page #{page_index}")
    proj = sess.get_project()
    result = td_mod.set_template(proj, page_index, template)
    output_fn(result, f"Template set to: {template}")


@techdraw_group.command("add-view")
@click.argument("page_index", type=int)
@click.argument("source_index", type=int)
@click.option("--direction", help="View direction x,y,z.")
@click.option("--scale", default=1.0, type=float, help="View scale.")
@click.option("--position", help="Page position x,y.")
@handle_error
def techdraw_add_view(
    page_index: int,
    source_index: int,
    direction: Optional[str],
    scale: float,
    position: Optional[str],
) -> None:
    """Add a standard view to a page."""
    sess = get_session()
    sess.snapshot(f"Add view to page #{page_index}")
    proj = sess.get_project()
    d = _parse_vec3(direction) if direction else None
    p = _parse_vec2(position) if position else None
    result = td_mod.add_view(
        proj, page_index, source_index, direction=d, scale=scale, position=p
    )
    output_fn(result, "Added view")


@techdraw_group.command("add-projection-group")
@click.argument("page_index", type=int)
@click.argument("source_index", type=int)
@click.option("--directions", help="Projections (comma-sep, e.g. front,right,top).")
@handle_error
def techdraw_add_projection_group(
    page_index: int, source_index: int, directions: Optional[str]
) -> None:
    """Add a projection group to a page."""
    sess = get_session()
    sess.snapshot(f"Add projection group to page #{page_index}")
    proj = sess.get_project()
    dirs = [d.strip() for d in directions.split(",")] if directions else None
    result = td_mod.add_projection_group(
        proj, page_index, source_index, directions=dirs
    )
    output_fn(result, "Added projection group")


@techdraw_group.command("add-section-view")
@click.argument("page_index", type=int)
@click.argument("view_index", type=int)
@click.option("--section-normal", help="Section normal x,y,z.")
@click.option("--section-origin", help="Section origin x,y,z.")
@handle_error
def techdraw_add_section_view(
    page_index: int,
    view_index: int,
    section_normal: Optional[str],
    section_origin: Optional[str],
) -> None:
    """Add a section view."""
    sess = get_session()
    sess.snapshot(f"Add section view to page #{page_index}")
    proj = sess.get_project()
    sn = _parse_vec3(section_normal) if section_normal else None
    so = _parse_vec3(section_origin) if section_origin else None
    result = td_mod.add_section_view(
        proj, page_index, view_index, section_normal=sn, section_origin=so
    )
    output_fn(result, "Added section view")


@techdraw_group.command("add-detail-view")
@click.argument("page_index", type=int)
@click.argument("view_index", type=int)
@click.option("--center", help="Detail center x,y.")
@click.option("--radius", default=20.0, type=float, help="Detail radius.")
@handle_error
def techdraw_add_detail_view(
    page_index: int, view_index: int, center: Optional[str], radius: float
) -> None:
    """Add a detail (magnified) view."""
    sess = get_session()
    sess.snapshot(f"Add detail view to page #{page_index}")
    proj = sess.get_project()
    c = _parse_vec2(center) if center else None
    result = td_mod.add_detail_view(
        proj, page_index, view_index, center=c, radius=radius
    )
    output_fn(result, "Added detail view")
