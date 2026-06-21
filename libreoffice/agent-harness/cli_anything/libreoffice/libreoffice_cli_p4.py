# ruff: noqa: F403, F405, E501
from .libreoffice_cli_base import *  # noqa: F403

# fmt: off
from .libreoffice_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .libreoffice_cli_p3 import calc  # noqa: E402,E501
# fmt: on


@calc.command("add-sheet")
@click.option("--name", "-n", default="Sheet", help="Sheet name")
@click.option("--position", "-p", type=int, default=None, help="Insert position")
@handle_error
def calc_add_sheet(name, position):
    """Add a new sheet."""
    sess = get_session()
    sess.snapshot(f"Add sheet: {name}")
    sheet = calc_mod.add_sheet(sess.get_project(), name=name, position=position)
    output(sheet, f"Added sheet: {name}")


@calc.command("remove-sheet")
@click.argument("index", type=int)
@handle_error
def calc_remove_sheet(index):
    """Remove a sheet by index."""
    sess = get_session()
    sess.snapshot(f"Remove sheet {index}")
    removed = calc_mod.remove_sheet(sess.get_project(), index)
    output(removed, f"Removed sheet at index {index}")


@calc.command("rename-sheet")
@click.argument("index", type=int)
@click.argument("name")
@handle_error
def calc_rename_sheet(index, name):
    """Rename a sheet."""
    sess = get_session()
    sess.snapshot(f"Rename sheet {index}")
    sheet = calc_mod.rename_sheet(sess.get_project(), index, name)
    output(sheet, f"Renamed sheet {index} to: {name}")


@calc.command("set-cell")
@click.argument("ref")
@click.argument("value")
@click.option("--type", "cell_type", default="string", help="Cell type: string, float")
@click.option("--sheet", "-s", type=int, default=0, help="Sheet index")
@click.option("--formula", type=str, default=None, help="Cell formula")
@handle_error
def calc_set_cell(ref, value, cell_type, sheet, formula):
    """Set a cell value."""
    sess = get_session()
    sess.snapshot(f"Set cell {ref}")
    result = calc_mod.set_cell(
        sess.get_project(),
        ref=ref,
        value=value,
        cell_type=cell_type,
        sheet=sheet,
        formula=formula,
    )
    output(result, f"Set {ref} = {value}")


@calc.command("get-cell")
@click.argument("ref")
@click.option("--sheet", "-s", type=int, default=0, help="Sheet index")
@handle_error
def calc_get_cell(ref, sheet):
    """Get a cell value."""
    sess = get_session()
    result = calc_mod.get_cell(sess.get_project(), ref=ref, sheet=sheet)
    output(result)


@calc.command("list-sheets")
@handle_error
def calc_list_sheets():
    """List all sheets."""
    sess = get_session()
    sheets = calc_mod.list_sheets(sess.get_project())
    output(sheets, "Sheets:")


@cli.group()
def impress():
    """Impress (presentation) commands."""
    pass


@impress.command("add-slide")
@click.option("--title", "-t", default="", help="Slide title")
@click.option("--content", "-c", default="", help="Slide content")
@click.option("--position", "-p", type=int, default=None, help="Insert position")
@handle_error
def impress_add_slide(title, content, position):
    """Add a slide to the presentation."""
    sess = get_session()
    sess.snapshot("Add slide")
    slide = impress_mod.add_slide(
        sess.get_project(),
        title=title,
        content=content,
        position=position,
    )
    output(slide, f"Added slide: {title}")


@impress.command("remove-slide")
@click.argument("index", type=int)
@handle_error
def impress_remove_slide(index):
    """Remove a slide by index."""
    sess = get_session()
    sess.snapshot(f"Remove slide {index}")
    removed = impress_mod.remove_slide(sess.get_project(), index)
    output(removed, f"Removed slide {index}")


@impress.command("set-content")
@click.argument("index", type=int)
@click.option("--title", "-t", type=str, default=None, help="New title")
@click.option("--content", "-c", type=str, default=None, help="New content")
@handle_error
def impress_set_content(index, title, content):
    """Update a slide's title and/or content."""
    sess = get_session()
    sess.snapshot(f"Update slide {index}")
    slide = impress_mod.set_slide_content(
        sess.get_project(),
        index,
        title=title,
        content=content,
    )
    output(slide, f"Updated slide {index}")


@impress.command("list-slides")
@handle_error
def impress_list_slides():
    """List all slides."""
    sess = get_session()
    slides = impress_mod.list_slides(sess.get_project())
    output(slides, "Slides:")


@impress.command("add-element")
@click.argument("slide_index", type=int)
@click.option("--type", "element_type", default="text_box", help="Element type")
@click.option("--text", "-t", default="", help="Element text")
@click.option("--x", default="2cm", help="X position")
@click.option("--y", default="2cm", help="Y position")
@click.option("--width", "-w", default="10cm", help="Width")
@click.option("--height", "-h", default="5cm", help="Height")
@handle_error
def impress_add_element(slide_index, element_type, text, x, y, width, height):
    """Add an element to a slide."""
    sess = get_session()
    sess.snapshot(f"Add element to slide {slide_index}")
    elem = impress_mod.add_slide_element(
        sess.get_project(),
        slide_index,
        element_type=element_type,
        text=text,
        x=x,
        y=y,
        width=width,
        height=height,
    )
    output(elem, f"Added {element_type} to slide {slide_index}")


@cli.group("style")
def style_group():
    """Style management commands."""
    pass


def _parse_props(prop_list):
    """Parse property key=value pairs from CLI."""
    props = {}
    for p in prop_list:
        if "=" not in p:
            raise ValueError(f"Invalid property format: '{p}'. Use key=value.")
        k, v = p.split("=", 1)
        # Try to parse bool/number
        if v.lower() == "true":
            v = True
        elif v.lower() == "false":
            v = False
        else:
            try:
                v = float(v) if "." in v else int(v)
            except ValueError:
                pass
        props[k] = v
    return props
