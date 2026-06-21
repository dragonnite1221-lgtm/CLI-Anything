# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p40 import cam_group  # noqa: E402,E501
# fmt: on


@cam_group.command("add-drilling")
@click.argument("job_index", type=int)
@click.option("--holes", default="all", help="Hole selection.")
@click.option("--depth", type=float, help="Drill depth.")
@click.option("--peck-depth", type=float, help="Peck increment.")
@handle_error
def cam_add_drilling(
    job_index: int, holes: str, depth: Optional[float], peck_depth: Optional[float]
) -> None:
    """Add a drilling operation."""
    sess = get_session()
    sess.snapshot(f"Add drilling to job #{job_index}")
    proj = sess.get_project()
    result = cam_mod.add_drilling_op(
        proj, job_index, holes=holes, depth=depth, peck_depth=peck_depth
    )
    output_fn(result, "Added drilling operation")


@cam_group.command("add-facing")
@click.argument("job_index", type=int)
@click.option("--depth", default=1.0, type=float, help="Facing depth.")
@click.option("--step-over", default=0.5, type=float, help="Step-over fraction.")
@handle_error
def cam_add_facing(job_index: int, depth: float, step_over: float) -> None:
    """Add a facing operation."""
    sess = get_session()
    sess.snapshot(f"Add facing to job #{job_index}")
    proj = sess.get_project()
    result = cam_mod.add_facing_op(proj, job_index, depth=depth, step_over=step_over)
    output_fn(result, "Added facing operation")


@cam_group.command("set-tool")
@click.argument("job_index", type=int)
@click.option("--tool-number", default=1, type=int, help="Tool number.")
@click.option("--diameter", default=6.0, type=float, help="Tool diameter.")
@click.option("--flutes", default=2, type=int, help="Number of flutes.")
@click.option(
    "--type",
    "tool_type",
    default="endmill",
    type=click.Choice(["endmill", "ballnose", "drill", "chamfer", "vbit", "facemill"]),
)
@click.option("--material", type=str, default=None, help="Tool material (FreeCAD 1.1).")
@click.option("--coating", type=str, default=None, help="Tool coating (FreeCAD 1.1).")
@handle_error
def cam_set_tool(
    job_index: int,
    tool_number: int,
    diameter: float,
    flutes: int,
    tool_type: str,
    material: Optional[str],
    coating: Optional[str],
) -> None:
    """Define a cutting tool."""
    sess = get_session()
    sess.snapshot(f"Set tool on job #{job_index}")
    proj = sess.get_project()
    result = cam_mod.set_tool(
        proj,
        job_index,
        tool_number=tool_number,
        diameter=diameter,
        flutes=flutes,
        type=tool_type,
        material=material,
        coating=coating,
    )
    output_fn(result, f"Tool T{tool_number} defined")


@cam_group.command("generate-gcode")
@click.argument("job_index", type=int)
@handle_error
def cam_generate_gcode(job_index: int) -> None:
    """Generate G-code for a job."""
    sess = get_session()
    sess.snapshot(f"Generate G-code for job #{job_index}")
    proj = sess.get_project()
    result = cam_mod.generate_gcode(proj, job_index)
    output_fn(result, "G-code generation configured")


@cam_group.command("simulate")
@click.argument("job_index", type=int)
@handle_error
def cam_simulate(job_index: int) -> None:
    """Simulate a CAM job."""
    sess = get_session()
    proj = sess.get_project()
    result = cam_mod.simulate_job(proj, job_index)
    output_fn(result, "Simulation:")


@cam_group.command("export-gcode")
@click.argument("job_index", type=int)
@click.argument("path", type=click.Path())
@handle_error
def cam_export_gcode(job_index: int, path: str) -> None:
    """Export G-code to a file."""
    sess = get_session()
    proj = sess.get_project()
    result = cam_mod.export_gcode(proj, job_index, path)
    output_fn(result, f"Exported G-code: {path}")


@cam_group.command("add-tapping")
@click.argument("job_index", type=int)
@click.option("--holes", default="all", help="Hole selection")
@click.option("--depth", type=float, default=None, help="Tapping depth")
@click.option("--thread-pitch", type=float, default=1.5, help="Thread pitch")
@click.option("--left-hand", is_flag=True, help="Use G74 left-hand tapping")
@handle_error
def cam_add_tapping(job_index, holes, depth, thread_pitch, left_hand):
    """Add a tapping operation G84/G74 (FreeCAD 1.1)."""
    sess = get_session()
    proj = sess.get_project()
    result = cam_mod.add_tapping_op(
        proj, job_index, holes, depth, thread_pitch, not left_hand
    )
    output_fn(result, "Tapping operation added.")


@cam_group.command("import-tool-library")
@click.argument("job_index", type=int)
@click.argument("path", type=click.Path())
@handle_error
def cam_import_tool_library(job_index, path):
    """Import a FreeCAD 1.1 tool library file."""
    sess = get_session()
    proj = sess.get_project()
    result = cam_mod.import_tool_library(proj, job_index, path)
    output_fn(result, "Tool library imported.")
