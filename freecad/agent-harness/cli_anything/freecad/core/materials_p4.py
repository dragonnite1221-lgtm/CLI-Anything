# ruff: noqa: F403, F405, E501
from .materials_base import *  # noqa: F403

# fmt: off
from .materials_p2 import _get_material, _validate_project  # noqa: E402,E501
# fmt: on


def assign_material(
    project: Dict[str, Any],
    material_index: int,
    part_index: int,
) -> Dict[str, Any]:
    """Assign a material to a part.

    Parameters
    ----------
    project:
        The project dictionary.
    material_index:
        Index of the material in ``project["materials"]``.
    part_index:
        Index of the part in ``project["parts"]``.

    Returns
    -------
    Dict[str, Any]
        Assignment summary with material and part names/IDs.

    Raises
    ------
    IndexError
        If either index is out of range.
    """
    _validate_project(project)

    mat = _get_material(project, material_index)

    parts = project.get("parts", [])
    if not isinstance(parts, list):
        raise ValueError("Project 'parts' must be a list")
    if part_index < 0 or part_index >= len(parts):
        raise IndexError(f"Part index {part_index} out of range (0-{len(parts) - 1})")

    part = parts[part_index]

    # Record the assignment on the material
    if part_index not in mat.get("assigned_to", []):
        mat.setdefault("assigned_to", []).append(part_index)

    # Record the material on the part
    part["material_id"] = mat["id"]
    part["material_index"] = material_index

    return {
        "material": mat["name"],
        "material_id": mat["id"],
        "part": part.get("name", f"Part {part_index}"),
        "part_id": part.get("id", part_index),
    }


def list_materials(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return a summary list of all materials in the project.

    Parameters
    ----------
    project:
        The project dictionary.

    Returns
    -------
    List[Dict[str, Any]]
        List of material summaries.
    """
    _validate_project(project)

    result: List[Dict[str, Any]] = []
    for i, mat in enumerate(project["materials"]):
        result.append(
            {
                "index": i,
                "id": mat.get("id", i),
                "name": mat.get("name", f"Material {i}"),
                "preset": mat.get("preset"),
                "color": mat.get("color", [0.8, 0.8, 0.8, 1.0]),
                "metallic": mat.get("metallic", 0.0),
                "roughness": mat.get("roughness", 0.5),
                "assigned_to": mat.get("assigned_to", []),
            }
        )
    return result


def get_material(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Return the full material dictionary at the given index.

    Parameters
    ----------
    project:
        The project dictionary.
    index:
        Material index.

    Returns
    -------
    Dict[str, Any]
        The complete material dictionary.
    """
    _validate_project(project)
    return _get_material(project, index)
