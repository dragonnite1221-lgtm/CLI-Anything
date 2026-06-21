# ruff: noqa: F403, F405, E501
from .diff_base import *  # noqa: F403

# fmt: off
from .diff_p4 import _diff_from_snapshots  # noqa: E402,E501
# fmt: on


def diff_pipeline_from_snapshots(
    snap_a: Dict[str, Any],
    snap_b: Dict[str, Any],
) -> Dict[str, Any]:
    """Compare two pre-built pipeline snapshots (for testing or offline use).

    Expects snapshots in the ``dump_pipeline_for_diff`` format::

        {"eventId": ..., "PipelineState": { ... }}

    Same logic as diff_pipeline but without needing live controllers.
    """
    return _diff_from_snapshots(snap_a, snap_b)
