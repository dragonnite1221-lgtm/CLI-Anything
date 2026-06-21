# ruff: noqa: F403, F405, E501
from .spreadsheet_base import *  # noqa: F403

# fmt: off
from .spreadsheet_p1 import _col_to_index, _get_sheet, _index_to_col, _parse_cell_ref, _validate_cell_ref  # noqa: E402,E501
# fmt: on


def import_csv(
    project: Dict[str, Any],
    sheet_index: int,
    path: str,
    start_cell: str = "A1",
) -> Dict[str, Any]:
    """Import CSV data into a spreadsheet.

    Each CSV value is stored as a cell starting from *start_cell*.
    Numeric strings are converted to floats automatically.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    sheet_index : int
        Index of the target spreadsheet.
    path : str
        Path to the CSV file.
    start_cell : str
        Top-left cell for the imported data.  Defaults to ``"A1"``.

    Returns
    -------
    dict
        Summary with number of rows and columns imported.

    Raises
    ------
    IndexError
        If *sheet_index* is out of range.
    FileNotFoundError
        If *path* does not exist.
    ValueError
        If *start_cell* is invalid.
    """
    if not isinstance(path, str) or not path.strip():
        raise ValueError("Path must be a non-empty string")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"CSV file not found: {path}")

    start_ref = _validate_cell_ref(start_cell)
    start_col_letters, start_row = _parse_cell_ref(start_ref)
    start_col = _col_to_index(start_col_letters)

    sheet = _get_sheet(project, sheet_index)

    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        rows_imported = 0
        max_cols = 0

        for row_offset, row in enumerate(reader):
            for col_offset, raw_value in enumerate(row):
                col_letters = _index_to_col(start_col + col_offset)
                row_num = start_row + row_offset
                ref = f"{col_letters}{row_num}"

                # Try to parse as number
                value: Union[str, float]
                try:
                    value = float(raw_value)
                    # Keep as int if no decimal part
                    if value == int(value):
                        value = int(value)
                    cell_type = "number"
                except (ValueError, OverflowError):
                    value = raw_value
                    cell_type = "string"

                sheet["cells"][ref] = {"value": value, "type": cell_type}

            rows_imported += 1
            if len(row) > max_cols:
                max_cols = len(row)

    return {
        "sheet_index": sheet_index,
        "rows_imported": rows_imported,
        "columns_imported": max_cols,
        "start_cell": start_ref,
    }
