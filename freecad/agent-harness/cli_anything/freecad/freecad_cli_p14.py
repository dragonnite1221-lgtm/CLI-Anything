# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p12 import body_group  # noqa: E402,E501
# fmt: on


@body_group.command("additive-box")
@click.argument("body_index", type=int)
@click.option("--length", "-l", default=10.0, type=float)
@click.option("--width", "-w", default=10.0, type=float)
@click.option("--height", "-h", default=10.0, type=float)
@click.option("--position", default=None, help="Placement position as x,y,z.")
@click.option(
    "--rotation", default=None, help="Placement rotation as rx,ry,rz degrees."
)
@handle_error
def body_additive_box(
    body_index: int,
    length: float,
    width: float,
    height: float,
    position: Optional[str],
    rotation: Optional[str],
) -> None:
    """Add an additive box primitive."""
    sess = get_session()
    sess.snapshot(f"Additive box body #{body_index}")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    result = body_mod.additive_box(
        proj,
        body_index,
        length=length,
        width=width,
        height=height,
        position=pos,
        rotation=rot,
    )
    output_fn(result, "Added additive box")


@body_group.command("additive-cylinder")
@click.argument("body_index", type=int)
@click.option("--radius", "-r", default=5.0, type=float)
@click.option("--height", "-h", default=10.0, type=float)
@click.option("--position", default=None, help="Placement position as x,y,z.")
@click.option(
    "--rotation", default=None, help="Placement rotation as rx,ry,rz degrees."
)
@handle_error
def body_additive_cylinder(
    body_index: int,
    radius: float,
    height: float,
    position: Optional[str],
    rotation: Optional[str],
) -> None:
    """Add an additive cylinder primitive."""
    sess = get_session()
    sess.snapshot(f"Additive cylinder body #{body_index}")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    result = body_mod.additive_cylinder(
        proj,
        body_index,
        radius=radius,
        height=height,
        position=pos,
        rotation=rot,
    )
    output_fn(result, "Added additive cylinder")


@body_group.command("additive-sphere")
@click.argument("body_index", type=int)
@click.option("--radius", "-r", default=5.0, type=float)
@click.option("--position", default=None, help="Placement position as x,y,z.")
@click.option(
    "--rotation", default=None, help="Placement rotation as rx,ry,rz degrees."
)
@handle_error
def body_additive_sphere(
    body_index: int, radius: float, position: Optional[str], rotation: Optional[str]
) -> None:
    """Add an additive sphere primitive."""
    sess = get_session()
    sess.snapshot(f"Additive sphere body #{body_index}")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    result = body_mod.additive_sphere(
        proj,
        body_index,
        radius=radius,
        position=pos,
        rotation=rot,
    )
    output_fn(result, "Added additive sphere")


@body_group.command("additive-cone")
@click.argument("body_index", type=int)
@click.option("--radius1", default=5.0, type=float)
@click.option("--radius2", default=0.0, type=float)
@click.option("--height", "-h", default=10.0, type=float)
@click.option("--position", default=None, help="Placement position as x,y,z.")
@click.option(
    "--rotation", default=None, help="Placement rotation as rx,ry,rz degrees."
)
@handle_error
def body_additive_cone(
    body_index: int,
    radius1: float,
    radius2: float,
    height: float,
    position: Optional[str],
    rotation: Optional[str],
) -> None:
    """Add an additive cone primitive."""
    sess = get_session()
    sess.snapshot(f"Additive cone body #{body_index}")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    result = body_mod.additive_cone(
        proj,
        body_index,
        radius1=radius1,
        radius2=radius2,
        height=height,
        position=pos,
        rotation=rot,
    )
    output_fn(result, "Added additive cone")
