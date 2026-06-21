# ruff: noqa: F403, F405, E501
from .spreadsheet_base import *  # noqa: F403

# fmt: off
from .spreadsheet_p1 import _get_sheet, _validate_cell_ref  # noqa: E402,E501
# fmt: on


def set_cell(
    project: Dict[str, Any],
    sheet_index: int,
    cell_ref: str,
    value: Union[str, int, float],
) -> Dict[str, Any]:
    """Set a cell value in a spreadsheet.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    sheet_index : int
        Index of the spreadsheet in ``project["spreadsheets"]``.
    cell_ref : str
        Cell reference such as ``"A1"``, ``"B2"``, ``"AA23"``.
    value : str, int, or float
        The value to store.  Strings starting with ``"="`` are treated as
        formulas.

    Returns
    -------
    dict
        A summary containing the cell reference and stored value.

    Raises
    ------
    IndexError
        If *sheet_index* is out of range.
    ValueError
        If *cell_ref* is invalid.
    """
    ref = _validate_cell_ref(cell_ref)
    sheet = _get_sheet(project, sheet_index)

    # Determine cell content type
    if isinstance(value, str) and value.startswith("="):
        cell_data = {"value": value, "type": "formula"}
    elif isinstance(value, (int, float)):
        cell_data = {"value": value, "type": "number"}
    else:
        cell_data = {"value": str(value), "type": "string"}

    sheet["cells"][ref] = cell_data

    return {
        "sheet_index": sheet_index,
        "cell_ref": ref,
        "value": cell_data["value"],
        "type": cell_data["type"],
    }


def get_cell(
    project: Dict[str, Any], sheet_index: int, cell_ref: str
) -> Dict[str, Any]:
    """Retrieve a cell value from a spreadsheet.

    Parameters
    ----------
    project : dict
        The project state dictionary.
    sheet_index : int
        Index of the spreadsheet.
    cell_ref : str
        Cell reference such as ``"A1"``.

    Returns
    -------
    dict
        Cell data including ``value`` and ``type``, or ``None`` values if
        the cell is empty.

    Raises
    ------
    IndexError
        If *sheet_index* is out of range.
    ValueError
        If *cell_ref* is invalid.
    """
    ref = _validate_cell_ref(cell_ref)
    sheet = _get_sheet(project, sheet_index)

    cell_data = sheet["cells"].get(ref)
    if cell_data is None:
        return {
            "sheet_index": sheet_index,
            "cell_ref": ref,
            "value": None,
            "type": None,
        }

    return {
        "sheet_index": sheet_index,
        "cell_ref": ref,
        "value": cell_data["value"],
        "type": cell_data["type"],
    }
