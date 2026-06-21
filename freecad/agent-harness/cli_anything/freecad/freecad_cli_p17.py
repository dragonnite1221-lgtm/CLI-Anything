# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_indices, _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p12 import body_group  # noqa: E402,E501
# fmt: on


@body_group.command("draft-feature")
@click.argument("body_index", type=int)
@click.argument("angle", type=float)
@click.option("--faces", default="all", help="Faces: 'all' or comma-sep indices.")
@click.option("--pull-direction", help="Pull direction as x,y,z.")
@handle_error
def body_draft_feature(
    body_index: int, angle: float, faces: str, pull_direction: Optional[str]
) -> None:
    """Add a draft (taper) feature."""
    sess = get_session()
    sess.snapshot(f"Draft feature body #{body_index}")
    proj = sess.get_project()
    face_val = faces if faces == "all" else _parse_indices(faces)
    pd = _parse_vec3(pull_direction) if pull_direction else None
    result = body_mod.draft_feature(
        proj, body_index, angle=angle, faces=face_val, pull_direction=pd
    )
    output_fn(result, "Added draft feature")


@body_group.command("thickness-feature")
@click.argument("body_index", type=int)
@click.argument("thickness_val", type=float)
@click.option("--faces", default="all", help="Faces: 'all' or comma-sep indices.")
@click.option(
    "--join", default="arc", type=click.Choice(["arc", "tangent", "intersection"])
)
@handle_error
def body_thickness_feature(
    body_index: int, thickness_val: float, faces: str, join: str
) -> None:
    """Add a thickness (shell) feature."""
    sess = get_session()
    sess.snapshot(f"Thickness feature body #{body_index}")
    proj = sess.get_project()
    face_val = faces if faces == "all" else _parse_indices(faces)
    result = body_mod.thickness_feature(
        proj, body_index, thickness=thickness_val, faces=face_val, join=join
    )
    output_fn(result, "Added thickness feature")


@body_group.command("hole")
@click.argument("body_index", type=int)
@click.argument("sketch_index", type=int)
@click.option("--diameter", "-d", default=5.0, type=float, help="Hole diameter.")
@click.option("--depth", default=10.0, type=float, help="Hole depth.")
@click.option("--threaded", is_flag=True, help="Threaded hole.")
@click.option("--thread-pitch", type=float, help="Thread pitch.")
@click.option(
    "--thread-standard",
    type=click.Choice(["metric", "BSW", "BSF", "BSP", "NPT"]),
    default="metric",
    help="Thread standard (FreeCAD 1.1).",
)
@click.option("--tapered", is_flag=True, help="Tapered hole (FreeCAD 1.1).")
@click.option(
    "--taper-angle", type=float, default=None, help="Taper angle (FreeCAD 1.1)."
)
@handle_error
def body_hole(
    body_index: int,
    sketch_index: int,
    diameter: float,
    depth: float,
    threaded: bool,
    thread_pitch: Optional[float],
    thread_standard: str,
    tapered: bool,
    taper_angle: Optional[float],
) -> None:
    """Add a hole feature to a body."""
    sess = get_session()
    sess.snapshot(f"Hole body #{body_index}")
    proj = sess.get_project()
    result = body_mod.hole_feature(
        proj,
        body_index,
        sketch_index,
        diameter=diameter,
        depth=depth,
        threaded=threaded,
        thread_pitch=thread_pitch,
        thread_standard=thread_standard,
        tapered=tapered,
        taper_angle=taper_angle,
    )
    output_fn(result, "Added hole feature")


@body_group.command("linear-pattern")
@click.argument("body_index", type=int)
@click.option("--direction", "-d", default="1,0,0", help="Direction as x,y,z.")
@click.option("--length", "-l", default=50.0, type=float, help="Pattern length.")
@click.option("--occurrences", default=3, type=int, help="Number of occurrences.")
@handle_error
def body_linear_pattern(
    body_index: int, direction: str, length: float, occurrences: int
) -> None:
    """Add a linear pattern feature."""
    sess = get_session()
    sess.snapshot(f"Linear pattern body #{body_index}")
    proj = sess.get_project()
    dir_vec = _parse_vec3(direction)
    result = body_mod.linear_pattern(
        proj, body_index, direction=dir_vec, length=length, occurrences=occurrences
    )
    output_fn(result, "Added linear pattern")


@body_group.command("polar-pattern")
@click.argument("body_index", type=int)
@click.option("--axis", default="Z", type=click.Choice(["X", "Y", "Z"]))
@click.option("--angle", "-a", default=360.0, type=float, help="Total angle.")
@click.option("--occurrences", default=6, type=int, help="Number of occurrences.")
@handle_error
def body_polar_pattern(
    body_index: int, axis: str, angle: float, occurrences: int
) -> None:
    """Add a polar pattern feature."""
    sess = get_session()
    sess.snapshot(f"Polar pattern body #{body_index}")
    proj = sess.get_project()
    result = body_mod.polar_pattern(
        proj, body_index, axis=axis, angle=angle, occurrences=occurrences
    )
    output_fn(result, "Added polar pattern")


@body_group.command("mirrored")
@click.argument("body_index", type=int)
@click.option("--plane", default="XY", type=click.Choice(["XY", "XZ", "YZ"]))
@handle_error
def body_mirrored(body_index: int, plane: str) -> None:
    """Add a mirrored feature."""
    sess = get_session()
    sess.snapshot(f"Mirrored body #{body_index}")
    proj = sess.get_project()
    result = body_mod.mirrored_feature(proj, body_index, plane=plane)
    output_fn(result, "Added mirrored feature")
