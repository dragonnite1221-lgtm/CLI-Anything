# ruff: noqa: F403, F405, E501
from .libreoffice_cli_base import *  # noqa: F403

# fmt: off
from .libreoffice_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .libreoffice_cli_p2 import document  # noqa: E402,E501
# fmt: on


@document.command("import-formats")
@handle_error
def document_import_formats():
    """List supported import formats."""
    formats = import_mod.list_import_formats()
    output(formats, "Supported import formats:")


@document.command("save")
@click.argument("path", required=False)
@handle_error
def document_save(path):
    """Save the current document."""
    sess = get_session()
    saved = sess.save_session(path)
    output({"saved": saved}, f"Saved to: {saved}")


@document.command("info")
@handle_error
def document_info():
    """Show document information."""
    sess = get_session()
    info = doc_mod.get_document_info(sess.get_project())
    output(info)


@document.command("profiles")
@handle_error
def document_profiles():
    """List available page profiles."""
    profiles = doc_mod.list_profiles()
    output(profiles, "Available profiles:")


@document.command("json")
@handle_error
def document_json():
    """Print raw project JSON."""
    sess = get_session()
    click.echo(json.dumps(sess.get_project(), indent=2, default=str))


@cli.group()
def writer():
    """Writer (word processor) commands."""
    pass


@writer.command("add-paragraph")
@click.option("--text", "-t", default="", help="Paragraph text")
@click.option("--position", "-p", type=int, default=None, help="Insert position")
@click.option("--font-size", type=str, default=None, help="Font size (e.g. 12pt)")
@click.option("--bold", is_flag=True, help="Bold text")
@click.option("--italic", is_flag=True, help="Italic text")
@click.option(
    "--alignment",
    type=click.Choice(["left", "center", "right", "justify"]),
    default=None,
)
@handle_error
def writer_add_paragraph(text, position, font_size, bold, italic, alignment):
    """Add a paragraph to the document."""
    sess = get_session()
    sess.snapshot("Add paragraph")
    style = {}
    if font_size:
        style["font_size"] = font_size
    if bold:
        style["bold"] = True
    if italic:
        style["italic"] = True
    if alignment:
        style["alignment"] = alignment
    item = writer_mod.add_paragraph(
        sess.get_project(),
        text=text,
        style=style or None,
        position=position,
    )
    output(item, "Added paragraph")


@writer.command("add-heading")
@click.option("--text", "-t", default="", help="Heading text")
@click.option("--level", "-l", type=int, default=1, help="Heading level (1-6)")
@click.option("--position", "-p", type=int, default=None, help="Insert position")
@handle_error
def writer_add_heading(text, level, position):
    """Add a heading to the document."""
    sess = get_session()
    sess.snapshot("Add heading")
    item = writer_mod.add_heading(
        sess.get_project(),
        text=text,
        level=level,
        position=position,
    )
    output(item, f"Added heading (level {level})")


@writer.command("add-list")
@click.option("--items", "-i", multiple=True, help="List items")
@click.option(
    "--style",
    "list_style",
    type=click.Choice(["bullet", "number"]),
    default="bullet",
    help="List style",
)
@click.option("--position", "-p", type=int, default=None, help="Insert position")
@handle_error
def writer_add_list(items, list_style, position):
    """Add a list to the document."""
    sess = get_session()
    sess.snapshot("Add list")
    item = writer_mod.add_list(
        sess.get_project(),
        items=list(items),
        list_style=list_style,
        position=position,
    )
    output(item, f"Added {list_style} list")


@writer.command("add-table")
@click.option("--rows", "-r", type=int, default=2, help="Number of rows")
@click.option("--cols", "-c", type=int, default=2, help="Number of columns")
@click.option("--position", "-p", type=int, default=None, help="Insert position")
@handle_error
def writer_add_table(rows, cols, position):
    """Add a table to the document."""
    sess = get_session()
    sess.snapshot("Add table")
    item = writer_mod.add_table(
        sess.get_project(),
        rows=rows,
        cols=cols,
        position=position,
    )
    output(item, f"Added {rows}x{cols} table")


@writer.command("add-page-break")
@click.option("--position", "-p", type=int, default=None, help="Insert position")
@handle_error
def writer_add_page_break(position):
    """Add a page break."""
    sess = get_session()
    sess.snapshot("Add page break")
    item = writer_mod.add_page_break(sess.get_project(), position=position)
    output(item, "Added page break")


@writer.command("remove")
@click.argument("index", type=int)
@handle_error
def writer_remove(index):
    """Remove a content item by index."""
    sess = get_session()
    sess.snapshot(f"Remove content {index}")
    removed = writer_mod.remove_content(sess.get_project(), index)
    output(removed, f"Removed content at index {index}")


@writer.command("list")
@handle_error
def writer_list():
    """List all content items."""
    sess = get_session()
    items = writer_mod.list_content(sess.get_project())
    output(items, "Content items:")


@writer.command("set-text")
@click.argument("index", type=int)
@click.argument("text")
@handle_error
def writer_set_text(index, text):
    """Set the text of a content item."""
    sess = get_session()
    sess.snapshot(f"Set text at {index}")
    item = writer_mod.set_content_text(sess.get_project(), index, text)
    output(item, f"Updated text at index {index}")


@cli.group()
def calc():
    """Calc (spreadsheet) commands."""
    pass
