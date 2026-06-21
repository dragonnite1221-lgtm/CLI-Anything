# ruff: noqa: F403, F405, E501
from .musescore_cli_base import *  # noqa: F403

# fmt: off
from .musescore_cli_p1 import cli, handle_error, output  # noqa: E402,E501
from .musescore_cli_p2 import transpose  # noqa: E402,E501
# fmt: on


@transpose.command("by-key")
@click.option("-i", "--input", "input_path", required=True, help="Input score")
@click.option("-o", "--output", "output_path", required=True, help="Output score")
@click.option(
    "--target-key", required=True, help="Target key (e.g., 'C major', 'Db', 'Am')"
)
@click.option(
    "--direction",
    type=click.Choice(["up", "down", "closest"]),
    default="closest",
    help="Transpose direction",
)
@click.option("--no-key-sig", is_flag=True, help="Don't transpose key signatures")
@click.option("--no-chord-names", is_flag=True, help="Don't transpose chord names")
@handle_error
def transpose_by_key(
    input_path, output_path, target_key, direction, no_key_sig, no_chord_names
):
    """Transpose to a target key."""
    sess = get_session()
    if sess.has_project():
        sess.snapshot(f"Transpose to {target_key}")

    result = trans_mod.transpose_by_key(
        input_path,
        output_path,
        target_key=target_key,
        direction=direction,
        transpose_key_signatures=not no_key_sig,
        transpose_chord_names=not no_chord_names,
    )

    # Update session state from output file
    if sess.has_project() and sess.project_path == input_path:
        updated = proj_mod.open_project(output_path)
        sess.project_data.update(updated)
        sess.project_path = output_path

    output(result, f"Transposed to {target_key}")


@transpose.command("by-interval")
@click.option("-i", "--input", "input_path", required=True, help="Input score")
@click.option("-o", "--output", "output_path", required=True, help="Output score")
@click.option("--semitones", type=int, default=None, help="Semitones (negative = down)")
@click.option(
    "--interval",
    "interval_index",
    type=int,
    default=None,
    help="MuseScore interval index (0-25)",
)
@click.option(
    "--direction",
    type=click.Choice(["up", "down"]),
    default="up",
    help="Transpose direction",
)
@click.option("--no-key-sig", is_flag=True, help="Don't transpose key signatures")
@click.option("--no-chord-names", is_flag=True, help="Don't transpose chord names")
@handle_error
def transpose_by_interval(
    input_path,
    output_path,
    semitones,
    interval_index,
    direction,
    no_key_sig,
    no_chord_names,
):
    """Transpose by a chromatic interval."""
    sess = get_session()
    if sess.has_project():
        sess.snapshot(f"Transpose by interval")

    result = trans_mod.transpose_by_interval(
        input_path,
        output_path,
        semitones=semitones,
        interval_index=interval_index,
        direction=direction,
        transpose_key_signatures=not no_key_sig,
        transpose_chord_names=not no_chord_names,
    )

    # Update session state from output file
    if sess.has_project() and sess.project_path == input_path:
        updated = proj_mod.open_project(output_path)
        sess.project_data.update(updated)
        sess.project_path = output_path

    output(result, "Transposed by interval")


@transpose.command("diatonic")
@click.option("-i", "--input", "input_path", required=True, help="Input score")
@click.option("-o", "--output", "output_path", required=True, help="Output score")
@click.option(
    "--steps", type=int, required=True, help="Diatonic steps (negative = down)"
)
@click.option(
    "--direction",
    type=click.Choice(["up", "down"]),
    default="up",
    help="Transpose direction",
)
@click.option("--no-key-sig", is_flag=True, help="Don't transpose key signatures")
@click.option("--no-chord-names", is_flag=True, help="Don't transpose chord names")
@handle_error
def transpose_diatonic(
    input_path, output_path, steps, direction, no_key_sig, no_chord_names
):
    """Transpose diatonically."""
    sess = get_session()
    if sess.has_project():
        sess.snapshot(f"Diatonic transpose by {steps}")

    result = trans_mod.transpose_diatonic(
        input_path,
        output_path,
        steps=steps,
        direction=direction,
        transpose_key_signatures=not no_key_sig,
        transpose_chord_names=not no_chord_names,
    )

    # Update session state from output file
    if sess.has_project() and sess.project_path == input_path:
        updated = proj_mod.open_project(output_path)
        sess.project_data.update(updated)
        sess.project_path = output_path

    output(result, f"Diatonic transpose by {steps} steps")


@cli.group()
def parts():
    """Part extraction and management."""
    pass


@parts.command("list")
@click.option("-i", "--input", "path", required=True, help="Score file path")
@handle_error
def parts_list(path):
    """List all parts in a score."""
    result = parts_mod.list_parts(path)
    output(result, "Parts:")
