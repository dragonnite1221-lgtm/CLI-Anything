# ruff: noqa: F403, F405, E501
from .inkscape_cli_base import *  # noqa: F403

# fmt: off
from .inkscape_cli_p1 import get_session, handle_error, output  # noqa: E402,E501
from .inkscape_cli_p2 import cli  # noqa: E402,E501
from .inkscape_cli_p6 import path_group  # noqa: E402,E501
# fmt: on


@path_group.command("list-operations")
@handle_error
def path_list_ops():
    """List available path boolean operations."""
    ops = path_mod.list_path_operations()
    output(ops, "Path operations:")


@cli.group()
def gradient():
    """Gradient management commands."""
    pass


@gradient.command("add-linear")
@click.option("--x1", type=float, default=0)
@click.option("--y1", type=float, default=0)
@click.option("--x2", type=float, default=1)
@click.option("--y2", type=float, default=0)
@click.option("--color1", default="#000000", help="Start color")
@click.option("--color2", default="#ffffff", help="End color")
@click.option("--name", "-n", default=None)
@handle_error
def gradient_add_linear(x1, y1, x2, y2, color1, color2, name):
    """Add a linear gradient."""
    stops = [
        {"offset": 0, "color": color1, "opacity": 1},
        {"offset": 1, "color": color2, "opacity": 1},
    ]
    sess = get_session()
    sess.snapshot("Add linear gradient")
    grad = grad_mod.add_linear_gradient(
        sess.get_project(), stops=stops, x1=x1, y1=y1, x2=x2, y2=y2, name=name
    )
    output(grad, f"Added linear gradient: {grad['name']}")


@gradient.command("add-radial")
@click.option("--cx", type=float, default=0.5)
@click.option("--cy", type=float, default=0.5)
@click.option("--r", type=float, default=0.5)
@click.option("--color1", default="#ffffff", help="Center color")
@click.option("--color2", default="#000000", help="Edge color")
@click.option("--name", "-n", default=None)
@handle_error
def gradient_add_radial(cx, cy, r, color1, color2, name):
    """Add a radial gradient."""
    stops = [
        {"offset": 0, "color": color1, "opacity": 1},
        {"offset": 1, "color": color2, "opacity": 1},
    ]
    sess = get_session()
    sess.snapshot("Add radial gradient")
    grad = grad_mod.add_radial_gradient(
        sess.get_project(), stops=stops, cx=cx, cy=cy, r=r, name=name
    )
    output(grad, f"Added radial gradient: {grad['name']}")


@gradient.command("apply")
@click.argument("gradient_index", type=int)
@click.argument("object_index", type=int)
@click.option("--target", "-t", default="fill", help="fill or stroke")
@handle_error
def gradient_apply(gradient_index, object_index, target):
    """Apply a gradient to an object."""
    sess = get_session()
    sess.snapshot(f"Apply gradient {gradient_index} to object {object_index}")
    result = grad_mod.apply_gradient(
        sess.get_project(), object_index, gradient_index, target
    )
    output(result, f"Applied gradient to {result['object']}")


@gradient.command("list")
@handle_error
def gradient_list():
    """List all gradients."""
    sess = get_session()
    grads = grad_mod.list_gradients(sess.get_project())
    output(grads, "Gradients:")


@cli.group("export")
def export_group():
    """Export/render commands."""
    pass


@export_group.command("png")
@click.argument("output_path")
@click.option("--width", "-w", type=int, default=None)
@click.option("--height", "-h", type=int, default=None)
@click.option("--dpi", type=int, default=96)
@click.option("--background", "-bg", default=None)
@click.option("--overwrite", is_flag=True)
@handle_error
def export_png(output_path, width, height, dpi, background, overwrite):
    """Render the document to PNG."""
    sess = get_session()
    result = export_mod.render_to_png(
        sess.get_project(),
        output_path,
        width=width,
        height=height,
        dpi=dpi,
        background=background,
        overwrite=overwrite,
    )
    output(result, f"Rendered: {output_path}")


@export_group.command("svg")
@click.argument("output_path")
@click.option("--overwrite", is_flag=True)
@handle_error
def export_svg(output_path, overwrite):
    """Export the document as SVG."""
    sess = get_session()
    result = export_mod.export_svg(sess.get_project(), output_path, overwrite=overwrite)
    output(result, f"Exported SVG: {output_path}")


@export_group.command("pdf")
@click.argument("output_path")
@click.option("--overwrite", is_flag=True)
@handle_error
def export_pdf(output_path, overwrite):
    """Export the document as PDF (requires Inkscape)."""
    sess = get_session()
    result = export_mod.export_pdf(sess.get_project(), output_path, overwrite=overwrite)
    output(result, f"Export PDF: {output_path}")


@export_group.command("presets")
@handle_error
def export_presets():
    """List export presets."""
    presets = export_mod.list_presets()
    output(presets, "Export presets:")


@cli.group()
def session():
    """Session management commands."""
    pass


@session.command("status")
@handle_error
def session_status():
    """Show session status."""
    sess = get_session()
    output(sess.status())


@session.command("undo")
@handle_error
def session_undo():
    """Undo the last operation."""
    sess = get_session()
    desc = sess.undo()
    output({"undone": desc}, f"Undone: {desc}")
