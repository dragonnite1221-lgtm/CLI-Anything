# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_indices, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p12 import body_group  # noqa: E402,E501
# fmt: on


@body_group.command("groove")
@click.argument("body_index", type=int)
@click.argument("sketch_index", type=int)
@click.option("--angle", "-a", default=360.0, type=float, help="Groove angle.")
@click.option(
    "--axis", default="Z", type=click.Choice(["X", "Y", "Z"]), help="Revolution axis."
)
@click.option("--reversed", "is_reversed", is_flag=True, help="Reverse direction.")
@handle_error
def body_groove(
    body_index: int, sketch_index: int, angle: float, axis: str, is_reversed: bool
) -> None:
    """Add a groove (subtractive revolution) feature."""
    sess = get_session()
    sess.snapshot(f"Groove body #{body_index}")
    proj = sess.get_project()
    result = body_mod.groove(
        proj, body_index, sketch_index, angle=angle, axis=axis, reversed=is_reversed
    )
    output_fn(result, "Added groove feature")


@body_group.command("additive-loft")
@click.argument("body_index", type=int)
@click.argument("sketch_indices", type=str)
@click.option("--solid/--no-solid", default=True, help="Create solid.")
@click.option("--ruled", is_flag=True, help="Use ruled surfaces.")
@handle_error
def body_additive_loft(
    body_index: int, sketch_indices: str, solid: bool, ruled: bool
) -> None:
    """Add an additive loft feature (comma-separated sketch indices)."""
    sess = get_session()
    sess.snapshot(f"Additive loft body #{body_index}")
    proj = sess.get_project()
    idx_list = _parse_indices(sketch_indices)
    result = body_mod.additive_loft(
        proj, body_index, sketch_indices=idx_list, solid=solid, ruled=ruled
    )
    output_fn(result, "Added additive loft")


@body_group.command("additive-pipe")
@click.argument("body_index", type=int)
@click.argument("profile_sketch_index", type=int)
@click.argument("path_sketch_index", type=int)
@handle_error
def body_additive_pipe(
    body_index: int, profile_sketch_index: int, path_sketch_index: int
) -> None:
    """Add an additive pipe (sweep) feature."""
    sess = get_session()
    sess.snapshot(f"Additive pipe body #{body_index}")
    proj = sess.get_project()
    result = body_mod.additive_pipe(
        proj, body_index, profile_sketch_index, path_sketch_index
    )
    output_fn(result, "Added additive pipe")


@body_group.command("additive-helix")
@click.argument("body_index", type=int)
@click.argument("sketch_index", type=int)
@click.option("--pitch", default=5.0, type=float, help="Helix pitch.")
@click.option("--height", default=20.0, type=float, help="Helix height.")
@click.option("--turns", type=float, help="Number of turns (overrides height).")
@handle_error
def body_additive_helix(
    body_index: int,
    sketch_index: int,
    pitch: float,
    height: float,
    turns: Optional[float],
) -> None:
    """Add an additive helix feature."""
    sess = get_session()
    sess.snapshot(f"Additive helix body #{body_index}")
    proj = sess.get_project()
    result = body_mod.additive_helix(
        proj, body_index, sketch_index, pitch=pitch, height=height, turns=turns
    )
    output_fn(result, "Added additive helix")


@body_group.command("subtractive-loft")
@click.argument("body_index", type=int)
@click.argument("sketch_indices", type=str)
@click.option("--solid/--no-solid", default=True, help="Create solid.")
@click.option("--ruled", is_flag=True, help="Use ruled surfaces.")
@handle_error
def body_subtractive_loft(
    body_index: int, sketch_indices: str, solid: bool, ruled: bool
) -> None:
    """Add a subtractive loft feature (comma-separated sketch indices)."""
    sess = get_session()
    sess.snapshot(f"Subtractive loft body #{body_index}")
    proj = sess.get_project()
    idx_list = _parse_indices(sketch_indices)
    result = body_mod.subtractive_loft(
        proj, body_index, sketch_indices=idx_list, solid=solid, ruled=ruled
    )
    output_fn(result, "Added subtractive loft")


@body_group.command("subtractive-pipe")
@click.argument("body_index", type=int)
@click.argument("profile_sketch_index", type=int)
@click.argument("path_sketch_index", type=int)
@handle_error
def body_subtractive_pipe(
    body_index: int, profile_sketch_index: int, path_sketch_index: int
) -> None:
    """Add a subtractive pipe (sweep cut) feature."""
    sess = get_session()
    sess.snapshot(f"Subtractive pipe body #{body_index}")
    proj = sess.get_project()
    result = body_mod.subtractive_pipe(
        proj, body_index, profile_sketch_index, path_sketch_index
    )
    output_fn(result, "Added subtractive pipe")


@body_group.command("subtractive-helix")
@click.argument("body_index", type=int)
@click.argument("sketch_index", type=int)
@click.option("--pitch", default=5.0, type=float, help="Helix pitch.")
@click.option("--height", default=20.0, type=float, help="Helix height.")
@click.option("--turns", type=float, help="Number of turns (overrides height).")
@handle_error
def body_subtractive_helix(
    body_index: int,
    sketch_index: int,
    pitch: float,
    height: float,
    turns: Optional[float],
) -> None:
    """Add a subtractive helix feature."""
    sess = get_session()
    sess.snapshot(f"Subtractive helix body #{body_index}")
    proj = sess.get_project()
    result = body_mod.subtractive_helix(
        proj, body_index, sketch_index, pitch=pitch, height=height, turns=turns
    )
    output_fn(result, "Added subtractive helix")
