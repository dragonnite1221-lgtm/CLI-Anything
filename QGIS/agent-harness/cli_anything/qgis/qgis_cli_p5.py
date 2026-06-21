# ruff: noqa: F403, F405, E501
from .qgis_cli_base import *  # noqa: F403

# fmt: off
from .qgis_cli_p1 import _current_project_modified, _sync_session_project_path, cli, get_session, handle_error, output, session  # noqa: E402,E501
from .qgis_cli_p2 import _active_project_path, _load_requested_project, _record  # noqa: E402,E501
from .qgis_cli_p4 import export  # noqa: E402,E501
# fmt: on


@export.command("pdf")
@click.argument("output_path", type=click.Path(path_type=Path))
@click.option("--layout", "layout_name", required=True, help="Layout name")
@click.option("--dpi", default=None, type=float, help="Override layout DPI")
@click.option("--force-vector", is_flag=True, help="Always export vector output")
@click.option("--force-raster", is_flag=True, help="Always rasterize the PDF")
@click.option(
    "--georeference/--no-georeference",
    default=True,
    help="Append georeference metadata",
)
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
@handle_error
def export_pdf(
    output_path: Path,
    layout_name: str,
    dpi: float | None,
    force_vector: bool,
    force_raster: bool,
    georeference: bool,
    overwrite: bool,
):
    """Export a named print layout as PDF."""
    _load_requested_project(required=True)
    data = export_mod.export_layout_pdf(
        str(output_path),
        layout_name=layout_name,
        dpi=dpi,
        force_vector=force_vector,
        force_raster=force_raster,
        georeference=georeference,
        overwrite=overwrite,
    )
    _record(
        "export pdf",
        {
            "output": str(output_path),
            "layout": layout_name,
            "dpi": dpi,
            "force_vector": force_vector,
            "force_raster": force_raster,
            "georeference": georeference,
            "overwrite": overwrite,
        },
        data,
    )
    output(data, f"Exported PDF: {data['output']}")


@export.command("image")
@click.argument("output_path", type=click.Path(path_type=Path))
@click.option("--layout", "layout_name", required=True, help="Layout name")
@click.option("--dpi", default=None, type=float, help="Override layout DPI")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
@handle_error
def export_image(
    output_path: Path, layout_name: str, dpi: float | None, overwrite: bool
):
    """Export a named print layout as an image file."""
    _load_requested_project(required=True)
    data = export_mod.export_layout_image(
        str(output_path),
        layout_name=layout_name,
        dpi=dpi,
        overwrite=overwrite,
    )
    _record(
        "export image",
        {
            "output": str(output_path),
            "layout": layout_name,
            "dpi": dpi,
            "overwrite": overwrite,
        },
        data,
    )
    output(data, f"Exported image: {data['output']}")


@cli.group()
def process():
    """Generic qgis_process discovery and execution commands."""


@process.command("list")
@handle_error
def process_list():
    """List installed QGIS processing algorithms."""
    data = processing_mod.list_algorithms()
    _record("process list", {}, {"count": data.get("algorithm_count")})
    output(data)


@process.command("help")
@click.argument("algorithm_id")
@handle_error
def process_help(algorithm_id: str):
    """Show parameter and output details for a processing algorithm."""
    data = processing_mod.help_algorithm(algorithm_id)
    _record("process help", {"algorithm_id": algorithm_id}, data)
    output(data)


@process.command("run")
@click.argument("algorithm_id")
@click.option(
    "--param", "param_specs", multiple=True, help="Algorithm parameter as KEY=VALUE"
)
@handle_error
def process_run(algorithm_id: str, param_specs: tuple[str, ...]):
    """Run a QGIS processing algorithm through qgis_process."""
    data = processing_mod.run_algorithm(
        algorithm_id,
        param_specs=list(param_specs),
        project_path=_active_project_path(required=False),
    )
    _record(
        "process run", {"algorithm_id": algorithm_id, "params": list(param_specs)}, data
    )
    output(data)


@session.command("status")
@handle_error
def session_status():
    """Show the current session status."""
    _sync_session_project_path()
    data = get_session().status(modified=_current_project_modified())
    _record("session status", {}, data)
    output(data)


@session.command("history")
@click.option(
    "--limit",
    default=20,
    show_default=True,
    type=int,
    help="Maximum history entries to show",
)
@handle_error
def session_history(limit: int):
    """Show recent command history."""
    data = {"history": get_session().history(limit=limit)}
    _record("session history", {"limit": limit}, {"count": len(data["history"])})
    output(data)


def main() -> None:
    """CLI entry point for setuptools."""
    cli()
