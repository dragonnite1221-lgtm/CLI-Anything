# ruff: noqa: F403, F405, E501
from .spreadsheet_base import *  # noqa: F403

# fmt: off
from .spreadsheet_p1 import _col_to_index, _get_sheet, _index_to_col, _parse_cell_ref  # noqa: E402,E501
# fmt: on


def export_csv(project: Dict[str, Any], sheet_index: int, path: str) -> Dict[str, Any]:
    """Export a spreadsheet to a CSV file.

    Cells are written in row-major order.  Empty cells produce empty
    strings in the output.

    Parameters
    ----------
    project : dict
        The project state dictionary.
    sheet_index : int
        Index of the spreadsheet.
    path : str
        Destination file path.

    Returns
    -------
    dict
        Summary with the absolute path and dimensions.

    Raises
    ------
    IndexError
        If *sheet_index* is out of range.
    ValueError
        If *path* is invalid.
    """
    if not isinstance(path, str) or not path.strip():
        raise ValueError("Path must be a non-empty string")

    sheet = _get_sheet(project, sheet_index)
    cells = sheet["cells"]

    if not cells:
        # Write an empty file
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            pass
        return {
            "sheet_index": sheet_index,
            "path": os.path.abspath(path),
            "rows": 0,
            "columns": 0,
        }

    # Determine grid bounds
    min_col, max_col = float("inf"), 0
    min_row, max_row = float("inf"), 0

    for ref in cells:
        col_letters, row_num = _parse_cell_ref(ref)
        col_idx = _col_to_index(col_letters)
        min_col = min(min_col, col_idx)
        max_col = max(max_col, col_idx)
        min_row = min(min_row, row_num)
        max_row = max(max_row, row_num)

    min_col = int(min_col)
    min_row = int(min_row)

    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    num_rows = max_row - min_row + 1
    num_cols = max_col - min_col + 1

    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        for row_num in range(min_row, max_row + 1):
            row_data: List[str] = []
            for col_idx in range(min_col, max_col + 1):
                ref = f"{_index_to_col(col_idx)}{row_num}"
                cell = cells.get(ref)
                if cell is not None:
                    row_data.append(str(cell["value"]))
                else:
                    row_data.append("")
            writer.writerow(row_data)

    return {
        "sheet_index": sheet_index,
        "path": os.path.abspath(path),
        "rows": num_rows,
        "columns": num_cols,
    }


def list_spreadsheets(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return a summary of all spreadsheets in the project.

    Returns
    -------
    list[dict]
        Each entry has ``id``, ``name``, ``cell_count``, and ``alias_count``.
    """
    sheets = project.get("spreadsheets", [])
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "cell_count": len(s.get("cells", {})),
            "alias_count": len(s.get("aliases", {})),
        }
        for s in sheets
    ]
