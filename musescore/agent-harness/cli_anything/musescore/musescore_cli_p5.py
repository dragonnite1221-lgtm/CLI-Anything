# ruff: noqa: F403, F405, E501
from .musescore_cli_base import *  # noqa: F403

# fmt: off
from .musescore_cli_p1 import cli, handle_error, output  # noqa: E402,E501
from .musescore_cli_p4 import instruments  # noqa: E402,E501
# fmt: on


@instruments.command("remove")
@click.option("-i", "--input", "path", required=True, help="Input .mscz file")
@click.option("-o", "--output", "output_path", required=True, help="Output .mscz file")
@click.option("--name", required=True, help="Instrument name to remove")
@handle_error
def instruments_remove(path, output_path, name):
    """Remove an instrument from a score."""
    sess = get_session()
    if sess.has_project():
        sess.snapshot(f"Remove instrument: {name}")
    result = inst_mod.remove_instrument(path, output_path, name)

    # Update session state from output file
    if sess.has_project() and sess.project_path == path:
        updated = proj_mod.open_project(output_path)
        sess.project_data.update(updated)
        sess.project_path = output_path

    output(result, f"Removed instrument: {name}")


@instruments.command("reorder")
@click.option("-i", "--input", "path", required=True, help="Input .mscz file")
@click.option("-o", "--output", "output_path", required=True, help="Output .mscz file")
@click.option("--order", required=True, help="Comma-separated instrument names")
@handle_error
def instruments_reorder(path, output_path, order):
    """Reorder instruments in a score."""
    new_order = [n.strip() for n in order.split(",")]
    sess = get_session()
    if sess.has_project():
        sess.snapshot("Reorder instruments")
    result = inst_mod.reorder_instruments(path, output_path, new_order)

    # Update session state from output file
    if sess.has_project() and sess.project_path == path:
        updated = proj_mod.open_project(output_path)
        sess.project_data.update(updated)
        sess.project_path = output_path

    output(result, "Reordered instruments")


@cli.group()
def media():
    """Media analysis commands."""
    pass


@media.command("probe")
@click.option("-i", "--input", "path", required=True, help="Score file path")
@handle_error
def media_probe(path):
    """Probe score metadata."""
    result = media_mod.probe_score(path)
    output(result)


@media.command("diff")
@click.option("--reference", required=True, help="Reference score")
@click.option("--compare", required=True, help="Comparison score")
@click.option("--raw", is_flag=True, help="Use raw diff format")
@handle_error
def media_diff(reference, compare, raw):
    """Diff two scores."""
    result = media_mod.diff_scores(reference, compare, raw=raw)
    output(result)


@media.command("stats")
@click.option("-i", "--input", "path", required=True, help="Score file path")
@handle_error
def media_stats(path):
    """Show score statistics."""
    result = media_mod.score_stats(path)
    output(result)


@cli.group("session")
def session_group():
    """Session management commands."""
    pass


@session_group.command("status")
@handle_error
def session_status():
    """Show session status."""
    sess = get_session()
    output(sess.status())


@session_group.command("undo")
@handle_error
def session_undo():
    """Undo the last operation."""
    sess = get_session()
    desc = sess.undo()
    output({"undone": desc}, f"Undone: {desc}")


@session_group.command("redo")
@handle_error
def session_redo():
    """Redo the last undone operation."""
    sess = get_session()
    desc = sess.redo()
    output({"redone": desc}, f"Redone: {desc}")


@session_group.command("history")
@handle_error
def session_history():
    """Show undo history."""
    sess = get_session()
    history = sess.list_history()
    output(history, "History:")


def main():
    cli()
