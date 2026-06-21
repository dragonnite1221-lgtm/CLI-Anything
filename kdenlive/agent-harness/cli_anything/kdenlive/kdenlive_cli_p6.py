# ruff: noqa: F403, F405, E501
from .kdenlive_cli_base import *  # noqa: F403

# fmt: off
from .kdenlive_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .kdenlive_cli_p5 import guide  # noqa: E402,E501
# fmt: on


@guide.command("add")
@click.argument("position", type=float)
@click.option("--label", "-l", default="", help="Guide label")
@click.option(
    "--type",
    "guide_type",
    type=click.Choice(["default", "chapter", "segment"]),
    default="default",
)
@click.option("--comment", "-c", default="", help="Comment")
@handle_error
def guide_add(position, label, guide_type, comment):
    """Add a guide at a position (seconds)."""
    sess = get_session()
    sess.snapshot("Add guide")
    g = guide_mod.add_guide(
        sess.get_project(),
        position,
        label=label,
        guide_type=guide_type,
        comment=comment,
    )
    output(g, f"Added guide at {position}s")


@guide.command("remove")
@click.argument("guide_id", type=int)
@handle_error
def guide_remove(guide_id):
    """Remove a guide."""
    sess = get_session()
    sess.snapshot(f"Remove guide {guide_id}")
    removed = guide_mod.remove_guide(sess.get_project(), guide_id)
    output(removed, f"Removed guide {guide_id}")


@guide.command("list")
@handle_error
def guide_list():
    """List all guides."""
    sess = get_session()
    guides = guide_mod.list_guides(sess.get_project())
    output(guides, "Guides:")


@cli.group()
def export():
    """Export and render commands."""
    pass


@export.command("xml")
@click.option("--output", "-o", type=str, default=None, help="Output file path")
@handle_error
def export_xml(output):
    """Generate Kdenlive/MLT XML."""
    sess = get_session()
    xml = export_mod.generate_kdenlive_xml(sess.get_project())
    if output:
        with open(output, "w") as f:
            f.write(xml)
        globals()["output"](
            {"path": output, "size": len(xml)}, f"XML written to: {output}"
        )
    else:
        click.echo(xml)


@export.command("presets")
@handle_error
def export_presets():
    """List available render presets."""
    presets = export_mod.list_render_presets()
    output(presets, "Render presets:")


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
