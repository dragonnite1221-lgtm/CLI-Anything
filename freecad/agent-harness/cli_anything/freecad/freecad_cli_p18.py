# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p12 import body_group  # noqa: E402,E501
# fmt: on


@body_group.command("multi-transform")
@click.argument("body_index", type=int)
@click.argument("transforms_json", type=str)
@handle_error
def body_multi_transform(body_index: int, transforms_json: str) -> None:
    """Add a multi-transform feature (JSON array of transformations)."""
    sess = get_session()
    sess.snapshot(f"Multi-transform body #{body_index}")
    proj = sess.get_project()
    transforms = json.loads(transforms_json)
    result = body_mod.multi_transform(proj, body_index, transformations=transforms)
    output_fn(result, "Added multi-transform")


@body_group.command("datum-plane")
@click.argument("body_index", type=int)
@click.option("--offset", default=0.0, type=float, help="Offset from reference.")
@click.option("--reference", default="XY", type=click.Choice(["XY", "XZ", "YZ"]))
@click.option(
    "--attachment-mode", type=str, default=None, help="Attachment mode (FreeCAD 1.1)."
)
@click.option(
    "--attachment-refs",
    type=str,
    default=None,
    help="Comma-separated attachment references (FreeCAD 1.1).",
)
@handle_error
def body_datum_plane(
    body_index: int,
    offset: float,
    reference: str,
    attachment_mode: Optional[str],
    attachment_refs: Optional[str],
) -> None:
    """Add a datum plane to a body."""
    sess = get_session()
    sess.snapshot(f"Datum plane body #{body_index}")
    proj = sess.get_project()
    att_refs = (
        [r.strip() for r in attachment_refs.split(",")] if attachment_refs else None
    )
    result = body_mod.datum_plane(
        proj,
        body_index,
        offset=offset,
        reference=reference,
        attachment_mode=attachment_mode,
        attachment_refs=att_refs,
    )
    output_fn(result, "Added datum plane")


@body_group.command("datum-line")
@click.argument("body_index", type=int)
@click.option("--point", default="0,0,0", help="Base point x,y,z.")
@click.option("--direction", "-d", default="0,0,1", help="Direction x,y,z.")
@click.option(
    "--attachment-mode", type=str, default=None, help="Attachment mode (FreeCAD 1.1)."
)
@click.option(
    "--attachment-refs",
    type=str,
    default=None,
    help="Comma-separated attachment references (FreeCAD 1.1).",
)
@handle_error
def body_datum_line(
    body_index: int,
    point: str,
    direction: str,
    attachment_mode: Optional[str],
    attachment_refs: Optional[str],
) -> None:
    """Add a datum line to a body."""
    sess = get_session()
    sess.snapshot(f"Datum line body #{body_index}")
    proj = sess.get_project()
    pt = _parse_vec3(point)
    d = _parse_vec3(direction)
    att_refs = (
        [r.strip() for r in attachment_refs.split(",")] if attachment_refs else None
    )
    result = body_mod.datum_line(
        proj,
        body_index,
        point=pt,
        direction=d,
        attachment_mode=attachment_mode,
        attachment_refs=att_refs,
    )
    output_fn(result, "Added datum line")


@body_group.command("datum-point")
@click.argument("body_index", type=int)
@click.option("--position", "-p", default="0,0,0", help="Position x,y,z.")
@click.option(
    "--attachment-mode", type=str, default=None, help="Attachment mode (FreeCAD 1.1)."
)
@click.option(
    "--attachment-refs",
    type=str,
    default=None,
    help="Comma-separated attachment references (FreeCAD 1.1).",
)
@handle_error
def body_datum_point(
    body_index: int,
    position: str,
    attachment_mode: Optional[str],
    attachment_refs: Optional[str],
) -> None:
    """Add a datum point to a body."""
    sess = get_session()
    sess.snapshot(f"Datum point body #{body_index}")
    proj = sess.get_project()
    pos = _parse_vec3(position)
    att_refs = (
        [r.strip() for r in attachment_refs.split(",")] if attachment_refs else None
    )
    result = body_mod.datum_point(
        proj,
        body_index,
        position=pos,
        attachment_mode=attachment_mode,
        attachment_refs=att_refs,
    )
    output_fn(result, "Added datum point")


@body_group.command("shape-binder")
@click.argument("body_index", type=int)
@click.argument("source_body_index", type=int)
@click.option("--feature-ref", help="Feature reference in source body.")
@handle_error
def body_shape_binder(
    body_index: int, source_body_index: int, feature_ref: Optional[str]
) -> None:
    """Add a shape binder referencing geometry from another body."""
    sess = get_session()
    sess.snapshot(f"Shape binder body #{body_index}")
    proj = sess.get_project()
    result = body_mod.shape_binder(
        proj, body_index, source_body_index, feature_ref=feature_ref
    )
    output_fn(result, "Added shape binder")


@body_group.command("local-coordinate-system")
@click.argument("body_index", type=int)
@click.option("--position", default=None, help="Position as x,y,z")
@click.option("--x-axis", default=None, help="X axis direction as x,y,z")
@click.option("--y-axis", default=None, help="Y axis direction as x,y,z")
@click.option("--z-axis", default=None, help="Z axis direction as x,y,z")
@handle_error
def body_local_coordinate_system(body_index, position, x_axis, y_axis, z_axis):
    """Add a local coordinate system to a body (FreeCAD 1.1)."""
    sess = get_session()
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    xa = _parse_vec3(x_axis) if x_axis else None
    ya = _parse_vec3(y_axis) if y_axis else None
    za = _parse_vec3(z_axis) if z_axis else None
    result = body_mod.local_coordinate_system(proj, body_index, pos, xa, ya, za)
    output_fn(result, "Local coordinate system added.")
