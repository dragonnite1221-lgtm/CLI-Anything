# ruff: noqa: F403, F405, E501
from .assembly_base import *  # noqa: F403

# fmt: off
from .assembly_p1 import _get_assembly  # noqa: E402,E501
# fmt: on


def degrees_of_freedom(
    project: Dict[str, Any],
    asm_index: int,
) -> Dict[str, Any]:
    """Estimate the remaining degrees of freedom for an assembly.

    Uses the simple formula ``6 * components - constraints``, clamped
    to zero.

    Returns
    -------
    dict
        ``{"dof": <int>, "components": <int>, "constraints": <int>}``
    """
    assembly = _get_assembly(project, asm_index)

    num_components = len(assembly["components"])
    num_constraints = len(assembly["constraints"])
    dof = max(0, 6 * num_components - num_constraints)

    return {
        "dof": dof,
        "components": num_components,
        "constraints": num_constraints,
    }


def generate_bom(
    project: Dict[str, Any],
    asm_index: int,
) -> Dict[str, Any]:
    """Generate a bill of materials for an assembly.

    Returns
    -------
    dict
        ``{"items": [{"name", "part_index", "quantity", "material"}], "total_parts": <int>}``
    """
    assembly = _get_assembly(project, asm_index)
    parts = project.get("parts", [])
    materials = project.get("materials", [])

    # Count occurrences of each part_index
    counts: Dict[int, int] = {}
    for comp in assembly["components"]:
        pi = comp["part_index"]
        counts[pi] = counts.get(pi, 0) + 1

    items: List[Dict[str, Any]] = []
    for pi, qty in sorted(counts.items()):
        part = (
            parts[pi]
            if pi < len(parts)
            else {"name": f"Part_{pi}", "material_index": None}
        )
        mat_name = None
        mi = part.get("material_index")
        if mi is not None and mi < len(materials):
            mat_name = materials[mi].get("name")

        items.append(
            {
                "name": part["name"],
                "part_index": pi,
                "quantity": qty,
                "material": mat_name,
            }
        )

    return {
        "items": items,
        "total_parts": len(assembly["components"]),
    }


def explode_assembly(
    project: Dict[str, Any],
    asm_index: int,
    factor: float = 2.0,
) -> Dict[str, Any]:
    """Move assembly components outward by *factor* for an exploded view.

    Each component's transform is scaled by *factor* relative to the
    assembly centroid.

    Returns
    -------
    dict
        ``{"exploded": True, "factor": <float>, "components": <int>}``
    """
    assembly = _get_assembly(project, asm_index)
    components = assembly["components"]

    if not components:
        return {"exploded": True, "factor": factor, "components": 0}

    # Compute centroid
    cx = sum(c["transform"][0] for c in components) / len(components)
    cy = sum(c["transform"][1] for c in components) / len(components)
    cz = sum(c["transform"][2] for c in components) / len(components)

    # Move each component outward
    for comp in components:
        t = comp["transform"]
        comp["transform"] = [
            cx + (t[0] - cx) * factor,
            cy + (t[1] - cy) * factor,
            cz + (t[2] - cz) * factor,
        ]

    return {"exploded": True, "factor": factor, "components": len(components)}


def collapse_assembly(
    project: Dict[str, Any],
    asm_index: int,
) -> Dict[str, Any]:
    """Reset all component transforms to their origin positions.

    If the assembly was previously solved, transforms are reset to
    ``[0, 0, 0]``.

    Returns
    -------
    dict
        ``{"collapsed": True, "components": <int>}``
    """
    assembly = _get_assembly(project, asm_index)

    for comp in assembly["components"]:
        comp["transform"] = [0.0, 0.0, 0.0]

    return {"collapsed": True, "components": len(assembly["components"])}
