# ruff: noqa: F403, F405, E501
from .diff_base import *  # noqa: F403

# fmt: off
from .diff_p1 import _diff_dicts, _diff_lists, _values_equal  # noqa: E402,E501
from .diff_p3 import _diff_stages  # noqa: E402,E501
# fmt: on


def _diff_from_snapshots(
    snap_a: Dict[str, Any], snap_b: Dict[str, Any]
) -> Dict[str, Any]:
    """Shared implementation: diff two dump_pipeline_for_diff snapshots."""
    ps_a = snap_a.get("PipelineState", {})
    ps_b = snap_b.get("PipelineState", {})

    result: Dict[str, Any] = {
        "eventA": snap_a.get("eventId"),
        "eventB": snap_b.get("eventId"),
    }

    has_diff = False

    # pipelineType
    pt_a = ps_a.get("pipelineType")
    pt_b = ps_b.get("pipelineType")
    if pt_a != pt_b:
        result["pipelineType"] = {"A": pt_a, "B": pt_b}
        has_diff = True
    else:
        result["pipelineType"] = pt_a

    # Simple sections: vertexInputs, outputTargets, depthTarget, viewport,
    # rasterizer, depthStencil
    for section, key_field in [
        ("vertexInputs", "name"),
        ("outputTargets", "index"),
    ]:
        d = _diff_lists(
            ps_a.get(section, []),
            ps_b.get(section, []),
            key_field=key_field,
        )
        if d:
            result[section] = d
            has_diff = True
        else:
            result[section] = "SAME"

    for section in ("depthTarget", "viewport", "rasterizer", "depthStencil"):
        d = _diff_dicts(ps_a.get(section), ps_b.get(section))
        if d:
            result[section] = d
            has_diff = True
        else:
            result[section] = "SAME"

    # blend — nested: top-level dict keys + blends list
    blend_a = ps_a.get("blend")
    blend_b = ps_b.get("blend")
    if blend_a is None and blend_b is None:
        result["blend"] = "SAME"
    elif blend_a is None or blend_b is None:
        result["blend"] = {"A": blend_a, "B": blend_b}
        has_diff = True
    else:
        blend_diff: Dict[str, Any] = {}
        blend_has_diff = False
        # Top-level scalar keys
        for k in sorted(set(list(blend_a.keys()) + list(blend_b.keys()))):
            if k == "blends":
                continue
            va = blend_a.get(k)
            vb = blend_b.get(k)
            if not _values_equal(va, vb):
                blend_diff[k] = {"A": va, "B": vb}
                blend_has_diff = True
        # blends list
        blends_diff = _diff_lists(
            blend_a.get("blends", []),
            blend_b.get("blends", []),
            key_field="index",
        )
        if blends_diff:
            blend_diff["blends"] = blends_diff
            blend_has_diff = True
        if blend_has_diff:
            result["blend"] = blend_diff
            has_diff = True
        else:
            result["blend"] = "SAME"

    # stages
    stages_diff = _diff_stages(
        ps_a.get("stages", {}),
        ps_b.get("stages", {}),
    )
    if stages_diff:
        result["stages"] = stages_diff
        has_diff = True
    else:
        result["stages"] = "SAME"

    result["identical"] = not has_diff
    return result


def diff_pipeline(
    controller_a,
    event_a: int,
    controller_b,
    event_b: int,
) -> Dict[str, Any]:
    """Compare full pipeline state at two events (possibly from different captures).

    Returns a dict containing only the dimensions that differ.
    Each section is either omitted (identical) or marked "SAME".
    """
    snap_a = dump_pipeline_for_diff(controller_a, event_a)
    snap_b = dump_pipeline_for_diff(controller_b, event_b)
    return _diff_from_snapshots(snap_a, snap_b)
