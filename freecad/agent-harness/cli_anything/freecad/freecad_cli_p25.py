# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p24 import measure_group  # noqa: E402,E501
# fmt: on


@measure_group.command("bounding-box")
@click.argument("index", type=int)
@handle_error
def measure_bounding_box(index: int) -> None:
    """Compute bounding box of a part."""
    sess = get_session()
    proj = sess.get_project()
    result = measure_mod.measure_bounding_box(proj, index)
    output_fn(result, "Bounding box:")


@measure_group.command("inertia")
@click.argument("index", type=int)
@handle_error
def measure_inertia(index: int) -> None:
    """Estimate principal moments of inertia."""
    sess = get_session()
    proj = sess.get_project()
    result = measure_mod.measure_inertia(proj, index)
    output_fn(result, "Inertia:")


@measure_group.command("check-geometry")
@click.argument("index", type=int)
@click.option(
    "--include-valid", is_flag=True, help="Include valid shape entries in report."
)
@click.option(
    "--skip", default=None, type=str, help="Comma-separated part indices to skip."
)
@handle_error
def measure_check_geometry(
    index: int, include_valid: bool, skip: Optional[str]
) -> None:
    """Perform geometry validation on a part."""
    sess = get_session()
    proj = sess.get_project()
    skip_list = [int(x.strip()) for x in skip.split(",")] if skip else None
    result = measure_mod.check_geometry(
        proj, index, include_valid=include_valid, skip_objects=skip_list
    )
    output_fn(result, "Geometry check:")


@cli.group("spreadsheet")
def spreadsheet_group():
    """Spreadsheet commands."""
    pass


@spreadsheet_group.command("new")
@click.option("--name", "-n", help="Spreadsheet name.")
@handle_error
def spreadsheet_new(name: Optional[str]) -> None:
    """Create a new spreadsheet."""
    sess = get_session()
    sess.snapshot("New spreadsheet")
    proj = sess.get_project()
    result = spread_mod.create_spreadsheet(proj, name=name)
    output_fn(result, f"Created spreadsheet: {result.get('name', '')}")


@spreadsheet_group.command("set-cell")
@click.argument("sheet_index", type=int)
@click.argument("cell_ref", type=str)
@click.argument("value", type=str)
@handle_error
def spreadsheet_set_cell(sheet_index: int, cell_ref: str, value: str) -> None:
    """Set a cell value in a spreadsheet."""
    sess = get_session()
    sess.snapshot(f"Set cell {cell_ref} in sheet #{sheet_index}")
    proj = sess.get_project()
    # Try to parse as number
    try:
        val: Any = float(value)
        if val == int(val) and "." not in value:
            val = int(val)
    except ValueError:
        val = value
    result = spread_mod.set_cell(proj, sheet_index, cell_ref, val)
    output_fn(result, f"Set {cell_ref} = {val}")


@spreadsheet_group.command("get-cell")
@click.argument("sheet_index", type=int)
@click.argument("cell_ref", type=str)
@handle_error
def spreadsheet_get_cell(sheet_index: int, cell_ref: str) -> None:
    """Get a cell value from a spreadsheet."""
    sess = get_session()
    proj = sess.get_project()
    result = spread_mod.get_cell(proj, sheet_index, cell_ref)
    output_fn(result, f"{cell_ref}: {result.get('value', 'empty')}")


@spreadsheet_group.command("set-alias")
@click.argument("sheet_index", type=int)
@click.argument("cell_ref", type=str)
@click.argument("alias", type=str)
@handle_error
def spreadsheet_set_alias(sheet_index: int, cell_ref: str, alias: str) -> None:
    """Assign an alias to a cell."""
    sess = get_session()
    sess.snapshot(f"Set alias {alias} for {cell_ref}")
    proj = sess.get_project()
    result = spread_mod.set_alias(proj, sheet_index, cell_ref, alias)
    output_fn(result, f"Alias '{alias}' -> {cell_ref}")


@spreadsheet_group.command("import-csv")
@click.argument("sheet_index", type=int)
@click.argument("path", type=click.Path(exists=True))
@click.option("--start-cell", default="A1", help="Top-left cell for import.")
@handle_error
def spreadsheet_import_csv(sheet_index: int, path: str, start_cell: str) -> None:
    """Import CSV data into a spreadsheet."""
    sess = get_session()
    sess.snapshot(f"Import CSV into sheet #{sheet_index}")
    proj = sess.get_project()
    result = spread_mod.import_csv(proj, sheet_index, path, start_cell=start_cell)
    output_fn(result, f"Imported {result.get('rows_imported', 0)} rows")


@spreadsheet_group.command("export-csv")
@click.argument("sheet_index", type=int)
@click.argument("path", type=click.Path())
@handle_error
def spreadsheet_export_csv(sheet_index: int, path: str) -> None:
    """Export a spreadsheet to CSV."""
    sess = get_session()
    proj = sess.get_project()
    result = spread_mod.export_csv(proj, sheet_index, path)
    output_fn(result, f"Exported: {result.get('path', path)}")
