# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_params, _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p12 import body_group  # noqa: E402,E501
# fmt: on


@body_group.command("subtractive-sphere")
@click.argument("body_index", type=int)
@click.option("--radius", "-r", default=5.0, type=float)
@click.option("--position", default=None, help="Placement position as x,y,z.")
@click.option(
    "--rotation", default=None, help="Placement rotation as rx,ry,rz degrees."
)
@handle_error
def body_subtractive_sphere(
    body_index: int, radius: float, position: Optional[str], rotation: Optional[str]
) -> None:
    """Add a subtractive sphere primitive."""
    sess = get_session()
    sess.snapshot(f"Subtractive sphere body #{body_index}")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    result = body_mod.subtractive_sphere(
        proj,
        body_index,
        radius=radius,
        position=pos,
        rotation=rot,
    )
    output_fn(result, "Added subtractive sphere")


@body_group.command("subtractive-cone")
@click.argument("body_index", type=int)
@click.option("--radius1", default=5.0, type=float)
@click.option("--radius2", default=0.0, type=float)
@click.option("--height", "-h", default=10.0, type=float)
@click.option("--position", default=None, help="Placement position as x,y,z.")
@click.option(
    "--rotation", default=None, help="Placement rotation as rx,ry,rz degrees."
)
@handle_error
def body_subtractive_cone(
    body_index: int,
    radius1: float,
    radius2: float,
    height: float,
    position: Optional[str],
    rotation: Optional[str],
) -> None:
    """Add a subtractive cone primitive."""
    sess = get_session()
    sess.snapshot(f"Subtractive cone body #{body_index}")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    result = body_mod.subtractive_cone(
        proj,
        body_index,
        radius1=radius1,
        radius2=radius2,
        height=height,
        position=pos,
        rotation=rot,
    )
    output_fn(result, "Added subtractive cone")


@body_group.command("subtractive-torus")
@click.argument("body_index", type=int)
@click.option("--radius1", default=10.0, type=float)
@click.option("--radius2", default=2.0, type=float)
@click.option("--position", default=None, help="Placement position as x,y,z.")
@click.option(
    "--rotation", default=None, help="Placement rotation as rx,ry,rz degrees."
)
@handle_error
def body_subtractive_torus(
    body_index: int,
    radius1: float,
    radius2: float,
    position: Optional[str],
    rotation: Optional[str],
) -> None:
    """Add a subtractive torus primitive."""
    sess = get_session()
    sess.snapshot(f"Subtractive torus body #{body_index}")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    result = body_mod.subtractive_torus(
        proj,
        body_index,
        radius1=radius1,
        radius2=radius2,
        position=pos,
        rotation=rot,
    )
    output_fn(result, "Added subtractive torus")


@body_group.command("subtractive-wedge")
@click.argument("body_index", type=int)
@click.option("--param", "-P", multiple=True, help="Wedge param as key=value.")
@click.option("--position", default=None, help="Placement position as x,y,z.")
@click.option(
    "--rotation", default=None, help="Placement rotation as rx,ry,rz degrees."
)
@handle_error
def body_subtractive_wedge(
    body_index: int, param: tuple, position: Optional[str], rotation: Optional[str]
) -> None:
    """Add a subtractive wedge primitive."""
    sess = get_session()
    sess.snapshot(f"Subtractive wedge body #{body_index}")
    proj = sess.get_project()
    params = _parse_params(param) or {}
    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    result = body_mod.subtractive_wedge(
        proj,
        body_index,
        position=pos,
        rotation=rot,
        **params,
    )
    output_fn(result, "Added subtractive wedge")
