# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p38 import fem_group  # noqa: E402,E501
# fmt: on


@fem_group.command("add-tie")
@click.argument("analysis_index", type=int)
@click.option("--master-refs", required=True, help="Comma-separated master refs")
@click.option("--slave-refs", required=True, help="Comma-separated slave refs")
@handle_error
def fem_add_tie(analysis_index, master_refs, slave_refs):
    """Add a tie constraint between shell faces (FreeCAD 1.1)."""
    sess = get_session()
    proj = sess.get_project()
    result = fem_mod.add_tie_constraint(
        proj, analysis_index, master_refs.split(","), slave_refs.split(",")
    )
    output_fn(result, "Tie constraint added.")


@fem_group.command("purge-results")
@click.argument("analysis_index", type=int)
@handle_error
def fem_purge_results(analysis_index):
    """Delete all result objects from an analysis (FreeCAD 1.1)."""
    sess = get_session()
    proj = sess.get_project()
    result = fem_mod.purge_results(proj, analysis_index)
    output_fn(result, "Results purged.")


@fem_group.command("suppress")
@click.argument("analysis_index", type=int)
@click.argument("constraint_index", type=int)
@handle_error
def fem_suppress(analysis_index, constraint_index):
    """Toggle suppressed state on a constraint (FreeCAD 1.1)."""
    sess = get_session()
    proj = sess.get_project()
    result = fem_mod.suppress_object(proj, analysis_index, constraint_index)
    state = "suppressed" if result.get("suppressed") else "active"
    output_fn(result, f"Constraint is now {state}.")


@cli.group("cam")
def cam_group():
    """CAM/CNC machining commands."""
    pass


@cam_group.command("new-job")
@click.argument("part_index", type=int)
@click.option("--name", "-n", help="Job name.")
@handle_error
def cam_new_job(part_index: int, name: Optional[str]) -> None:
    """Create a new CAM job for a part."""
    sess = get_session()
    sess.snapshot("New CAM job")
    proj = sess.get_project()
    result = cam_mod.new_job(proj, part_index, name=name)
    output_fn(result, f"Created job: {result.get('name', '')}")


@cam_group.command("set-stock")
@click.argument("job_index", type=int)
@click.option(
    "--stock-type", default="box", type=click.Choice(["box", "cylinder", "from_part"])
)
@click.option("--extra-x", default=2.0, type=float)
@click.option("--extra-y", default=2.0, type=float)
@click.option("--extra-z", default=2.0, type=float)
@handle_error
def cam_set_stock(
    job_index: int, stock_type: str, extra_x: float, extra_y: float, extra_z: float
) -> None:
    """Define raw stock for a CAM job."""
    sess = get_session()
    sess.snapshot(f"Set stock on job #{job_index}")
    proj = sess.get_project()
    result = cam_mod.set_stock(
        proj,
        job_index,
        stock_type=stock_type,
        extra_x=extra_x,
        extra_y=extra_y,
        extra_z=extra_z,
    )
    output_fn(result, "Stock defined")


@cam_group.command("add-profile")
@click.argument("job_index", type=int)
@click.option("--faces", default="all", help="Face selection.")
@click.option("--depth", type=float, help="Cut depth.")
@click.option("--step-down", default=1.0, type=float, help="Step-down per pass.")
@click.option(
    "--passes", type=int, default=None, help="Number of passes (FreeCAD 1.1)."
)
@click.option(
    "--finishing-pass", is_flag=True, help="Add finishing pass (FreeCAD 1.1)."
)
@handle_error
def cam_add_profile(
    job_index: int,
    faces: str,
    depth: Optional[float],
    step_down: float,
    passes: Optional[int],
    finishing_pass: bool,
) -> None:
    """Add a profile (contour) operation."""
    sess = get_session()
    sess.snapshot(f"Add profile to job #{job_index}")
    proj = sess.get_project()
    result = cam_mod.add_profile_op(
        proj,
        job_index,
        faces=faces,
        depth=depth,
        step_down=step_down,
        passes=passes,
        finishing_pass=finishing_pass,
    )
    output_fn(result, "Added profile operation")


@cam_group.command("add-pocket")
@click.argument("job_index", type=int)
@click.option("--faces", default="all", help="Face selection.")
@click.option("--depth", type=float, help="Pocket depth.")
@click.option("--step-down", default=1.0, type=float, help="Step-down per pass.")
@click.option("--step-over", default=0.5, type=float, help="Step-over fraction.")
@handle_error
def cam_add_pocket(
    job_index: int,
    faces: str,
    depth: Optional[float],
    step_down: float,
    step_over: float,
) -> None:
    """Add a pocket operation."""
    sess = get_session()
    sess.snapshot(f"Add pocket to job #{job_index}")
    proj = sess.get_project()
    result = cam_mod.add_pocket_op(
        proj,
        job_index,
        faces=faces,
        depth=depth,
        step_down=step_down,
        step_over=step_over,
    )
    output_fn(result, "Added pocket operation")
