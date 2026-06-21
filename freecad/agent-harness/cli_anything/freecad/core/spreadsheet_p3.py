# ruff: noqa: F403, F405, E501
from .spreadsheet_base import *  # noqa: F403

# fmt: off
from .spreadsheet_p1 import _get_sheet, _validate_cell_ref  # noqa: E402,E501
# fmt: on


def set_alias(
    project: Dict[str, Any],
    sheet_index: int,
    cell_ref: str,
    alias: str,
) -> Dict[str, Any]:
    """Assign an alias name to a cell.

    Aliases allow cells to be referenced by name in formulas and
    parametric expressions.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    sheet_index : int
        Index of the spreadsheet.
    cell_ref : str
        Cell reference to alias.
    alias : str
        Alias name.  Must start with a letter or underscore and contain
        only alphanumeric characters and underscores.

    Returns
    -------
    dict
        Summary with ``cell_ref`` and ``alias``.

    Raises
    ------
    IndexError
        If *sheet_index* is out of range.
    ValueError
        If *cell_ref* or *alias* is invalid, or the alias is already in use.
    """
    ref = _validate_cell_ref(cell_ref)
    sheet = _get_sheet(project, sheet_index)

    if not isinstance(alias, str) or not alias.strip():
        raise ValueError("Alias must be a non-empty string")
    alias = alias.strip()

    if not _ALIAS_RE.match(alias):
        raise ValueError(
            f"Invalid alias '{alias}'. Must start with a letter or underscore "
            f"and contain only alphanumeric characters and underscores."
        )

    # Check alias uniqueness (allow re-aliasing the same cell)
    for existing_ref, existing_alias in sheet["aliases"].items():
        if existing_alias == alias and existing_ref != ref:
            raise ValueError(
                f"Alias '{alias}' is already assigned to cell {existing_ref}"
            )

    sheet["aliases"][ref] = alias

    return {
        "sheet_index": sheet_index,
        "cell_ref": ref,
        "alias": alias,
    }
