# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p27 import draft_group  # noqa: E402,E501
# fmt: on


@draft_group.command("scale")
@click.argument("index", type=int)
@click.argument("scale_factor", type=str)
@click.option("--center", help="Center of scaling x,y,z.")
@click.option("--copy", is_flag=True, help="Create a scaled copy.")
@handle_error
def draft_scale(
    index: int, scale_factor: str, center: Optional[str], copy: bool
) -> None:
    """Scale a draft object."""
    sess = get_session()
    sess.snapshot(f"Draft scale #{index}")
    proj = sess.get_project()
    if "," in scale_factor:
        sf = _parse_vec3(scale_factor)
    else:
        sf = float(scale_factor)
    ctr = _parse_vec3(center) if center else None
    result = draft_mod.draft_scale(proj, index, scale=sf, center=ctr, copy=copy)
    output_fn(result, f"Scaled: {result.get('name', '')}")


@draft_group.command("mirror")
@click.argument("index", type=int)
@click.option("--point", help="Mirror reference point x,y,z.")
@click.option("--name", "-n", help="Name for mirrored copy.")
@handle_error
def draft_mirror(index: int, point: Optional[str], name: Optional[str]) -> None:
    """Create a mirrored copy of a draft object."""
    sess = get_session()
    sess.snapshot(f"Draft mirror #{index}")
    proj = sess.get_project()
    pt = _parse_vec3(point) if point else None
    result = draft_mod.draft_mirror(proj, index, point=pt, name=name)
    output_fn(result, f"Mirrored: {result.get('name', '')}")


@draft_group.command("offset")
@click.argument("index", type=int)
@click.option("--distance", "-d", default=1.0, type=float, help="Offset distance.")
@click.option("--copy/--no-copy", default=True, help="Create offset copy.")
@click.option("--name", "-n", help="Name for offset copy.")
@handle_error
def draft_offset(index: int, distance: float, copy: bool, name: Optional[str]) -> None:
    """Offset a draft object."""
    sess = get_session()
    sess.snapshot(f"Draft offset #{index}")
    proj = sess.get_project()
    result = draft_mod.draft_offset(
        proj, index, distance=distance, copy=copy, name=name
    )
    output_fn(result, f"Offset: {result.get('name', '')}")


@draft_group.command("array-linear")
@click.argument("index", type=int)
@click.option("--x-count", default=2, type=int)
@click.option("--y-count", default=1, type=int)
@click.option("--x-interval", default=20.0, type=float)
@click.option("--y-interval", default=20.0, type=float)
@click.option("--name", "-n", help="Array name.")
@handle_error
def draft_array_linear(
    index: int,
    x_count: int,
    y_count: int,
    x_interval: float,
    y_interval: float,
    name: Optional[str],
) -> None:
    """Create a linear array of a draft object."""
    sess = get_session()
    sess.snapshot(f"Draft linear array #{index}")
    proj = sess.get_project()
    result = draft_mod.draft_array_linear(
        proj,
        index,
        x_count=x_count,
        y_count=y_count,
        x_interval=x_interval,
        y_interval=y_interval,
        name=name,
    )
    output_fn(result, f"Linear array: {result.get('name', '')}")


@draft_group.command("array-polar")
@click.argument("index", type=int)
@click.option("--count", default=6, type=int)
@click.option("--angle", default=360.0, type=float)
@click.option("--center", help="Center x,y,z.")
@click.option("--name", "-n", help="Array name.")
@handle_error
def draft_array_polar(
    index: int, count: int, angle: float, center: Optional[str], name: Optional[str]
) -> None:
    """Create a polar array of a draft object."""
    sess = get_session()
    sess.snapshot(f"Draft polar array #{index}")
    proj = sess.get_project()
    ctr = _parse_vec3(center) if center else None
    result = draft_mod.draft_array_polar(
        proj, index, count=count, angle=angle, center=ctr, name=name
    )
    output_fn(result, f"Polar array: {result.get('name', '')}")


@draft_group.command("array-path")
@click.argument("index", type=int)
@click.argument("path_index", type=int)
@click.option("--count", default=4, type=int)
@click.option("--name", "-n", help="Array name.")
@handle_error
def draft_array_path(
    index: int, path_index: int, count: int, name: Optional[str]
) -> None:
    """Create a path array of a draft object."""
    sess = get_session()
    sess.snapshot(f"Draft path array #{index}")
    proj = sess.get_project()
    result = draft_mod.draft_array_path(
        proj, index, path_index=path_index, count=count, name=name
    )
    output_fn(result, f"Path array: {result.get('name', '')}")


@draft_group.command("copy")
@click.argument("index", type=int)
@click.option("--name", "-n", help="Name for copy.")
@handle_error
def draft_copy(index: int, name: Optional[str]) -> None:
    """Copy a draft object."""
    sess = get_session()
    sess.snapshot(f"Draft copy #{index}")
    proj = sess.get_project()
    result = draft_mod.draft_copy(proj, index, name=name)
    output_fn(result, f"Copied: {result.get('name', '')}")
