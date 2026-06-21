# ruff: noqa: F403, F405, E501
from .assembly_base import *  # noqa: F403

# fmt: off
from .assembly_p1 import _get_assembly  # noqa: E402,E501
# fmt: on


def add_simulation_step(
    project: Dict[str, Any],
    asm_index: int,
    sim_index: int,
    joint_index: int,
    start_value: float = 0.0,
    end_value: float = 1.0,
) -> Dict[str, Any]:
    """Append a motion step to an existing simulation.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    asm_index : int
        Index of the target assembly.
    sim_index : int
        Index of the simulation within the assembly's ``simulations`` list.
    joint_index : int
        Index of the joint/constraint this step drives.
    start_value : float
        Starting value for the joint parameter.
    end_value : float
        Ending value for the joint parameter.

    Returns
    -------
    dict
        The newly created step dictionary.

    Raises
    ------
    IndexError
        If *asm_index* or *sim_index* is out of range.
    """
    assembly = _get_assembly(project, asm_index)

    simulations = assembly.get("simulations", [])
    if not isinstance(sim_index, int) or sim_index < 0 or sim_index >= len(simulations):
        raise IndexError(
            f"Simulation index {sim_index} out of range (0..{len(simulations) - 1})"
        )

    simulation = simulations[sim_index]

    step: Dict[str, Any] = {
        "joint_index": int(joint_index),
        "start_value": float(start_value),
        "end_value": float(end_value),
    }

    simulation["steps"].append(step)
    return step
