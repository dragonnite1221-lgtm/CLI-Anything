# ruff: noqa: F403, F405, E501
from .libreoffice_cli_base import *  # noqa: F403

# fmt: off
from .libreoffice_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .libreoffice_cli_p4 import _parse_props, style_group  # noqa: E402,E501
# fmt: on


@style_group.command("create")
@click.argument("name")
@click.option(
    "--family",
    type=click.Choice(["paragraph", "text"]),
    default="paragraph",
    help="Style family",
)
@click.option("--parent", type=str, default=None, help="Parent style name")
@click.option("--prop", "-p", multiple=True, help="Property: key=value")
@handle_error
def style_create(name, family, parent, prop):
    """Create a new style."""
    props = _parse_props(prop)
    sess = get_session()
    sess.snapshot(f"Create style: {name}")
    result = styles_mod.create_style(
        sess.get_project(),
        name=name,
        family=family,
        parent=parent,
        properties=props,
    )
    output(result, f"Created style: {name}")


@style_group.command("modify")
@click.argument("name")
@click.option("--prop", "-p", multiple=True, help="Property: key=value")
@handle_error
def style_modify(name, prop):
    """Modify an existing style."""
    props = _parse_props(prop)
    sess = get_session()
    sess.snapshot(f"Modify style: {name}")
    result = styles_mod.modify_style(
        sess.get_project(),
        name=name,
        properties=props,
    )
    output(result, f"Modified style: {name}")


@style_group.command("list")
@handle_error
def style_list():
    """List all styles."""
    sess = get_session()
    styles = styles_mod.list_styles(sess.get_project())
    output(styles, "Styles:")


@style_group.command("apply")
@click.argument("style_name")
@click.argument("content_index", type=int)
@handle_error
def style_apply(style_name, content_index):
    """Apply a style to a content item (Writer only)."""
    sess = get_session()
    sess.snapshot(f"Apply style {style_name} to {content_index}")
    result = styles_mod.apply_style(
        sess.get_project(),
        style_name,
        content_index,
    )
    output(result, f"Applied style '{style_name}' to content {content_index}")


@style_group.command("remove")
@click.argument("name")
@handle_error
def style_remove(name):
    """Remove a style."""
    sess = get_session()
    sess.snapshot(f"Remove style: {name}")
    result = styles_mod.remove_style(sess.get_project(), name)
    output(result, f"Removed style: {name}")


@cli.group("export")
def export_group():
    """Export/render commands."""
    pass


@export_group.command("presets")
@handle_error
def export_presets():
    """List export presets."""
    presets = export_mod.list_presets()
    output(presets, "Export presets:")


@export_group.command("preset-info")
@click.argument("name")
@handle_error
def export_preset_info(name):
    """Show preset details."""
    info = export_mod.get_preset_info(name)
    output(info)


@export_group.command("render")
@click.argument("output_path")
@click.option("--preset", "-p", default="odt", help="Export preset")
@click.option("--overwrite", is_flag=True, help="Overwrite existing file")
@handle_error
def export_render(output_path, preset, overwrite):
    """Export the document to a file."""
    sess = get_session()
    result = export_mod.export(
        sess.get_project(),
        output_path,
        preset=preset,
        overwrite=overwrite,
    )
    output(result, f"Exported to: {output_path}")


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


@session.command("redo")
@handle_error
def session_redo():
    """Redo the last undone operation."""
    sess = get_session()
    desc = sess.redo()
    output({"redone": desc}, f"Redone: {desc}")


@session.command("history")
@handle_error
def session_history():
    """Show undo history."""
    sess = get_session()
    history = sess.list_history()
    output(history, "Undo history:")


def main():
    cli()
