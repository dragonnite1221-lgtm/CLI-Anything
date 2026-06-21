# ruff: noqa: F403, F405, E501
from .spreadsheet_base import *  # noqa: F403


def _next_id(project: Dict[str, Any]) -> int:
    """Return the next available integer ID for spreadsheets."""
    items = project.get("spreadsheets", [])
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _unique_name(project: Dict[str, Any], base: str) -> str:
    """Return a unique spreadsheet name derived from *base*."""
    existing = {item["name"] for item in project.get("spreadsheets", [])}
    if base not in existing:
        return base
    counter = 2
    while f"{base}_{counter}" in existing:
        counter += 1
    return f"{base}_{counter}"


def _validate_cell_ref(cell_ref: str) -> str:
    """Validate and return a normalised cell reference (upper-case).

    Raises ``ValueError`` if the reference is malformed.
    """
    if not isinstance(cell_ref, str):
        raise ValueError(
            f"Cell reference must be a string, got {type(cell_ref).__name__}"
        )
    ref = cell_ref.strip().upper()
    if not _CELL_REF_RE.match(ref):
        raise ValueError(
            f"Invalid cell reference '{cell_ref}'. "
            f"Expected format like A1, B2, AA23 (1-3 uppercase letters + row number >= 1)"
        )
    return ref


def _get_sheet(project: Dict[str, Any], sheet_index: int) -> Dict[str, Any]:
    """Return the spreadsheet at *sheet_index*.

    Raises ``IndexError`` when the index is out of range.
    """
    sheets = project.get("spreadsheets", [])
    if (
        not isinstance(sheet_index, int)
        or sheet_index < 0
        or sheet_index >= len(sheets)
    ):
        raise IndexError(
            f"Spreadsheet index {sheet_index} out of range (0..{len(sheets) - 1})"
        )
    return sheets[sheet_index]


def _parse_cell_ref(cell_ref: str):
    """Split a cell reference into (column_letters, row_number)."""
    match = re.match(r"^([A-Z]{1,3})([1-9][0-9]*)$", cell_ref)
    if not match:
        raise ValueError(f"Cannot parse cell reference '{cell_ref}'")
    return match.group(1), int(match.group(2))


def _col_to_index(col: str) -> int:
    """Convert column letters to a zero-based index (A=0, B=1, ..., Z=25, AA=26)."""
    result = 0
    for ch in col:
        result = result * 26 + (ord(ch) - ord("A") + 1)
    return result - 1


def _index_to_col(index: int) -> str:
    """Convert a zero-based column index back to letters."""
    result = []
    index += 1  # 1-based
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        result.append(chr(ord("A") + remainder))
    return "".join(reversed(result))


def create_spreadsheet(
    project: Dict[str, Any], name: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new spreadsheet and append it to the project.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    name : str or None
        Label for the spreadsheet.  Auto-generated when *None*.

    Returns
    -------
    dict
        The newly created spreadsheet dictionary.
    """
    sheets = ensure_collection(project, "spreadsheets")

    if name is None:
        name = _unique_name(project, "Spreadsheet")
    elif not isinstance(name, str) or not name.strip():
        raise ValueError("Spreadsheet name must be a non-empty string")
    else:
        name = name.strip()

    sheet: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "cells": {},
        "aliases": {},
    }

    sheets.append(sheet)
    return sheet
