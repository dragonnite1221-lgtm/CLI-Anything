# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import cli, handle_error, output_fn  # noqa: E402,E501
# fmt: on


@cli.group("body")
def body_group():
    """PartDesign body commands."""
    pass


@body_group.command("new")
@click.option("--name", "-n", help="Body name.")
@handle_error
def body_new(name: Optional[str]) -> None:
    """Create a new PartDesign body."""
    sess = get_session()
    sess.snapshot("New body")
    proj = sess.get_project()
    result = body_mod.create_body(proj, name=name)
    output_fn(result, f"Created body: {result.get('name', '')}")


@body_group.command("pad")
@click.argument("body_index", type=int)
@click.argument("sketch_index", type=int)
@click.option("--length", "-l", default=10.0, type=float, help="Pad length.")
@click.option("--symmetric", is_flag=True, help="Symmetric pad.")
@click.option("--reversed", "is_reversed", is_flag=True, help="Reverse direction.")
@handle_error
def body_pad(
    body_index: int,
    sketch_index: int,
    length: float,
    symmetric: bool,
    is_reversed: bool,
) -> None:
    """Add a pad (extrusion) feature to a body."""
    sess = get_session()
    sess.snapshot(f"Pad body #{body_index}")
    proj = sess.get_project()
    result = body_mod.pad(
        proj,
        body_index,
        sketch_index,
        length=length,
        symmetric=symmetric,
        reversed=is_reversed,
    )
    output_fn(result, "Added pad feature")


@body_group.command("pocket")
@click.argument("body_index", type=int)
@click.argument("sketch_index", type=int)
@click.option("--length", "-l", default=5.0, type=float, help="Pocket depth.")
@click.option("--symmetric", is_flag=True, help="Symmetric pocket.")
@click.option("--reversed", "is_reversed", is_flag=True, help="Reverse direction.")
@handle_error
def body_pocket(
    body_index: int,
    sketch_index: int,
    length: float,
    symmetric: bool,
    is_reversed: bool,
) -> None:
    """Add a pocket (cut extrusion) feature to a body."""
    sess = get_session()
    sess.snapshot(f"Pocket body #{body_index}")
    proj = sess.get_project()
    result = body_mod.pocket(
        proj,
        body_index,
        sketch_index,
        length=length,
        symmetric=symmetric,
        reversed=is_reversed,
    )
    output_fn(result, "Added pocket feature")


@body_group.command("fillet")
@click.argument("body_index", type=int)
@click.option("--radius", "-r", default=1.0, type=float, help="Fillet radius.")
@click.option("--edges", default="all", help="Edges: 'all' or comma-sep indices.")
@handle_error
def body_fillet(body_index: int, radius: float, edges: str) -> None:
    """Add a fillet feature to a body."""
    sess = get_session()
    sess.snapshot(f"Fillet body #{body_index}")
    proj = sess.get_project()
    edge_val = edges if edges == "all" else [int(x) for x in edges.split(",")]
    result = body_mod.fillet(proj, body_index, radius=radius, edges=edge_val)
    output_fn(result, "Added fillet feature")


@body_group.command("chamfer")
@click.argument("body_index", type=int)
@click.option("--size", "-s", default=1.0, type=float, help="Chamfer size.")
@click.option("--edges", default="all", help="Edges: 'all' or comma-sep indices.")
@handle_error
def body_chamfer(body_index: int, size: float, edges: str) -> None:
    """Add a chamfer feature to a body."""
    sess = get_session()
    sess.snapshot(f"Chamfer body #{body_index}")
    proj = sess.get_project()
    edge_val = edges if edges == "all" else [int(x) for x in edges.split(",")]
    result = body_mod.chamfer(proj, body_index, size=size, edges=edge_val)
    output_fn(result, "Added chamfer feature")


@body_group.command("revolution")
@click.argument("body_index", type=int)
@click.argument("sketch_index", type=int)
@click.option("--angle", "-a", default=360.0, type=float, help="Revolution angle.")
@click.option(
    "--axis", default="Z", type=click.Choice(["X", "Y", "Z"]), help="Revolution axis."
)
@click.option("--reversed", "is_reversed", is_flag=True, help="Reverse direction.")
@handle_error
def body_revolution(
    body_index: int, sketch_index: int, angle: float, axis: str, is_reversed: bool
) -> None:
    """Add a revolution feature to a body."""
    sess = get_session()
    sess.snapshot(f"Revolution body #{body_index}")
    proj = sess.get_project()
    result = body_mod.revolution(
        proj, body_index, sketch_index, angle=angle, axis=axis, reversed=is_reversed
    )
    output_fn(result, "Added revolution feature")


@body_group.command("list")
@handle_error
def body_list() -> None:
    """List all bodies."""
    sess = get_session()
    proj = sess.get_project()
    result = body_mod.list_bodies(proj)
    output_fn(result, f"{len(result)} body/bodies:")


@body_group.command("get")
@click.argument("index", type=int)
@handle_error
def body_get(index: int) -> None:
    """Get body details."""
    sess = get_session()
    proj = sess.get_project()
    result = body_mod.get_body(proj, index)
    output_fn(result, f"Body #{index}:")
