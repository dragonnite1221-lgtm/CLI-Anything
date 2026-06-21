# ruff: noqa: F403, F405, E501
from .musescore_cli_base import *  # noqa: F403

# fmt: off
from .musescore_cli_p1 import cli, handle_error, output  # noqa: E402,E501
from .musescore_cli_p3 import parts  # noqa: E402,E501
# fmt: on


@parts.command("extract")
@click.option("-i", "--input", "path", required=True, help="Score file path")
@click.option("-o", "--output", "output_path", required=True, help="Output file path")
@click.option("--part", "part_name", required=True, help="Part name to extract")
@handle_error
def parts_extract(path, output_path, part_name):
    """Extract a single part from a score."""
    result = parts_mod.extract_part(path, part_name, output_path)
    output(result, f"Extracted part: {part_name}")


@parts.command("generate")
@click.option("-i", "--input", "path", required=True, help="Score file path")
@click.option("-d", "--output-dir", required=True, help="Output directory")
@handle_error
def parts_generate(path, output_dir):
    """Generate all parts as separate files."""
    result = parts_mod.generate_all_parts(path, output_dir)
    output(result, f"Generated {len(result)} parts")


@cli.group("export")
def export_group():
    """Export/render commands."""
    pass


def _make_export_cmd(fmt_name, description):
    """Factory for format-specific export commands."""

    @export_group.command(fmt_name, help=description)
    @click.option("-i", "--input", "input_path", required=True, help="Input score")
    @click.option("-o", "--output", "output_path", required=True, help="Output file")
    @click.option("--dpi", type=int, default=None, help="DPI for PNG export")
    @click.option("--bitrate", type=int, default=None, help="Bitrate for MP3 (kbps)")
    @click.option("--trim", type=int, default=None, help="Trim margin for PNG/SVG")
    @click.option("--style", type=str, default=None, help="Style file (.mss)")
    @click.option(
        "--sound-profile",
        type=str,
        default=None,
        help="Audio profile (MuseScore Basic or Muse Sounds)",
    )
    @handle_error
    def export_cmd(input_path, output_path, dpi, bitrate, trim, style, sound_profile):
        result = export_mod.export_score(
            input_path,
            output_path,
            fmt=fmt_name,
            dpi=dpi,
            bitrate=bitrate,
            trim=trim,
            style=style,
            sound_profile=sound_profile,
        )
        output(result, f"Exported {fmt_name}: {output_path}")

    return export_cmd


_make_export_cmd("pdf", "Export as PDF document")
_make_export_cmd("png", "Export as PNG images (one per page)")
_make_export_cmd("svg", "Export as SVG vector graphics")
_make_export_cmd("mp3", "Export as MP3 audio")
_make_export_cmd("flac", "Export as FLAC audio")
_make_export_cmd("wav", "Export as WAV audio")
_make_export_cmd("midi", "Export as MIDI file")
_make_export_cmd("musicxml", "Export as MusicXML")
_make_export_cmd("braille", "Export as Braille music notation")


@export_group.command("batch")
@click.option("-i", "--input", "input_path", required=True, help="Input score")
@click.option(
    "-o",
    "--output",
    "outputs",
    multiple=True,
    required=True,
    help="Output files (specify multiple)",
)
@handle_error
def export_batch(input_path, outputs):
    """Export to multiple formats at once."""
    result = export_mod.batch_export(input_path, list(outputs))
    output(result, f"Batch exported {len(result)} files")


@export_group.command("verify")
@click.argument("path")
@click.option("--format", "fmt", default=None, help="Expected format")
@handle_error
def export_verify(path, fmt):
    """Verify an exported file using magic bytes."""
    result = export_mod.verify_output(path, fmt)
    output(result)


@cli.group()
def instruments():
    """Instrument management commands."""
    pass


@instruments.command("list")
@click.option("-i", "--input", "path", required=True, help="Score file path")
@handle_error
def instruments_list(path):
    """List instruments in a score."""
    result = inst_mod.list_instruments(path)
    output(result, "Instruments:")


@instruments.command("add")
@click.option("-i", "--input", "path", required=True, help="Input .mscz file")
@click.option("-o", "--output", "output_path", required=True, help="Output .mscz file")
@click.option("--id", "instrument_id", required=True, help="Instrument ID")
@click.option("--name", required=True, help="Display name")
@handle_error
def instruments_add(path, output_path, instrument_id, name):
    """Add an instrument to a score."""
    sess = get_session()
    if sess.has_project():
        sess.snapshot(f"Add instrument: {name}")
    result = inst_mod.add_instrument(path, output_path, instrument_id, name)

    # Update session state from output file
    if sess.has_project() and sess.project_path == path:
        updated = proj_mod.open_project(output_path)
        sess.project_data.update(updated)
        sess.project_path = output_path

    output(result, f"Added instrument: {name}")
