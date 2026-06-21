# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p40 import cam_group  # noqa: E402,E501
# fmt: on


@cam_group.command("export-tool-library")
@click.argument("job_index", type=int)
@click.argument("path", type=click.Path())
@handle_error
def cam_export_tool_library(job_index, path):
    """Export CAM job tool library."""
    sess = get_session()
    proj = sess.get_project()
    result = cam_mod.export_tool_library(proj, job_index, path)
    output_fn(result, "Tool library exported.")


def main():
    """Entry point for the CLI."""
    cli()
