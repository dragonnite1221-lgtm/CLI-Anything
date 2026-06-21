# ruff: noqa: F403, F405, E501
from .assembly_base import *  # noqa: F403

# fmt: off
from .assembly_p1 import _get_assembly, _next_id, _unique_name, _validate_vec3  # noqa: E402,E501
# fmt: on


def insert_new_part(
    project: Dict[str, Any],
    asm_index: int,
    part_type: str = "box",
    name: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    transform: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Create a new part inline within an assembly.

    Instead of referencing an existing part from ``project["parts"]``,
    this function embeds an inline part definition directly in the
    assembly's components list.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    asm_index : int
        Index of the target assembly.
    part_type : str
        The type of part to create (e.g. ``"box"``, ``"cylinder"``).
    name : str or None
        Human-readable label. Auto-generated when *None*.
    params : dict or None
        Part-specific parameters (e.g. dimensions). Defaults to ``{}``.
    transform : list[float] or None
        Optional ``[x, y, z]`` placement offset. Defaults to ``[0, 0, 0]``.

    Returns
    -------
    dict
        The newly created component entry.

    Raises
    ------
    IndexError
        If *asm_index* is out of range.
    """
    assembly = _get_assembly(project, asm_index)

    if transform is not None:
        transform = _validate_vec3(transform, "transform")
    else:
        transform = [0.0, 0.0, 0.0]

    if params is None:
        params = {}

    if name is None:
        name = _unique_name(project, f"InlinePart_{part_type}")

    component: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "inline_part": {
            "type": part_type,
            "params": dict(params),
        },
        "transform": transform,
    }

    assembly["components"].append(component)
    assembly["solved"] = False
    return component


def create_simulation(
    project: Dict[str, Any],
    asm_index: int,
    name: Optional[str] = None,
    duration: float = 5.0,
    fps: int = 24,
) -> Dict[str, Any]:
    """Create a simulation entry on an assembly for joint motion/animation.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    asm_index : int
        Index of the target assembly.
    name : str or None
        Human-readable label. Auto-generated when *None*.
    duration : float
        Total simulation duration in seconds.
    fps : int
        Frames per second for the simulation.

    Returns
    -------
    dict
        The newly created simulation dictionary.

    Raises
    ------
    IndexError
        If *asm_index* is out of range.
    """
    assembly = _get_assembly(project, asm_index)

    if name is None:
        name = f"Simulation_{len(assembly.get('simulations', [])) + 1}"

    simulation: Dict[str, Any] = {
        "name": name,
        "duration": float(duration),
        "fps": int(fps),
        "steps": [],
        "status": "configured",
    }

    assembly.setdefault("simulations", []).append(simulation)
    return simulation
