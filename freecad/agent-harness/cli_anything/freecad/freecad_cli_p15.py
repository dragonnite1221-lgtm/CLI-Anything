# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_params, _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p12 import body_group  # noqa: E402,E501
# fmt: on


@body_group.command("additive-torus")
@click.argument("body_index", type=int)
@click.option("--radius1", default=10.0, type=float)
@click.option("--radius2", default=2.0, type=float)
@click.option("--position", default=None, help="Placement position as x,y,z.")
@click.option(
    "--rotation", default=None, help="Placement rotation as rx,ry,rz degrees."
)
@handle_error
def body_additive_torus(
    body_index: int,
    radius1: float,
    radius2: float,
    position: Optional[str],
    rotation: Optional[str],
) -> None:
    """Add an additive torus primitive."""
    sess = get_session()
    sess.snapshot(f"Additive torus body #{body_index}")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    result = body_mod.additive_torus(
        proj,
        body_index,
        radius1=radius1,
        radius2=radius2,
        position=pos,
        rotation=rot,
    )
    output_fn(result, "Added additive torus")


@body_group.command("additive-wedge")
@click.argument("body_index", type=int)
@click.option("--param", "-P", multiple=True, help="Wedge param as key=value.")
@click.option("--position", default=None, help="Placement position as x,y,z.")
@click.option(
    "--rotation", default=None, help="Placement rotation as rx,ry,rz degrees."
)
@handle_error
def body_additive_wedge(
    body_index: int, param: tuple, position: Optional[str], rotation: Optional[str]
) -> None:
    """Add an additive wedge primitive."""
    sess = get_session()
    sess.snapshot(f"Additive wedge body #{body_index}")
    proj = sess.get_project()
    params = _parse_params(param) or {}
    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    result = body_mod.additive_wedge(
        proj,
        body_index,
        position=pos,
        rotation=rot,
        **params,
    )
    output_fn(result, "Added additive wedge")


@body_group.command("subtractive-box")
@click.argument("body_index", type=int)
@click.option("--length", "-l", default=10.0, type=float)
@click.option("--width", "-w", default=10.0, type=float)
@click.option("--height", "-h", default=10.0, type=float)
@click.option("--position", default=None, help="Placement position as x,y,z.")
@click.option(
    "--rotation", default=None, help="Placement rotation as rx,ry,rz degrees."
)
@handle_error
def body_subtractive_box(
    body_index: int,
    length: float,
    width: float,
    height: float,
    position: Optional[str],
    rotation: Optional[str],
) -> None:
    """Add a subtractive box primitive."""
    sess = get_session()
    sess.snapshot(f"Subtractive box body #{body_index}")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    result = body_mod.subtractive_box(
        proj,
        body_index,
        length=length,
        width=width,
        height=height,
        position=pos,
        rotation=rot,
    )
    output_fn(result, "Added subtractive box")


@body_group.command("subtractive-cylinder")
@click.argument("body_index", type=int)
@click.option("--radius", "-r", default=5.0, type=float)
@click.option("--height", "-h", default=10.0, type=float)
@click.option("--position", default=None, help="Placement position as x,y,z.")
@click.option(
    "--rotation", default=None, help="Placement rotation as rx,ry,rz degrees."
)
@handle_error
def body_subtractive_cylinder(
    body_index: int,
    radius: float,
    height: float,
    position: Optional[str],
    rotation: Optional[str],
) -> None:
    """Add a subtractive cylinder primitive."""
    sess = get_session()
    sess.snapshot(f"Subtractive cylinder body #{body_index}")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    result = body_mod.subtractive_cylinder(
        proj,
        body_index,
        radius=radius,
        height=height,
        position=pos,
        rotation=rot,
    )
    output_fn(result, "Added subtractive cylinder")
