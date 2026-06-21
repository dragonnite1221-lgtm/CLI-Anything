# ruff: noqa: F403, F405, E501
from .diff_base import *  # noqa: F403

# fmt: off
from .diff_p1 import _diff_dicts  # noqa: E402,E501
from .diff_p2 import _diff_bindings  # noqa: E402,E501
# fmt: on


def _diff_stages(stages_a: Dict, stages_b: Dict) -> Optional[Dict[str, Any]]:
    """Diff the stages sub-dict of PipelineState.

    For each stage present in either snapshot, compare:
    - shader / entryPoint (as a dict)
    - ShaderReflection (deep dict diff)
    - bindings (structured diff with variable values)
    """
    all_names = sorted(set(list(stages_a.keys()) + list(stages_b.keys())))
    result: Dict[str, Any] = {}
    has_diff = False

    for name in all_names:
        sa = stages_a.get(name)
        sb = stages_b.get(name)

        if sa is None:
            result[name] = {"status": "only_in_B", "B": sb}
            has_diff = True
            continue
        if sb is None:
            result[name] = {"status": "only_in_A", "A": sa}
            has_diff = True
            continue

        stage_result: Dict[str, Any] = {}
        stage_has_diff = False

        # shader + entryPoint
        shader_dict_a = {"shader": sa.get("shader"), "entryPoint": sa.get("entryPoint")}
        shader_dict_b = {"shader": sb.get("shader"), "entryPoint": sb.get("entryPoint")}
        shader_diff = _diff_dicts(shader_dict_a, shader_dict_b)
        if shader_diff:
            stage_result["shader"] = shader_diff
            stage_has_diff = True
        else:
            stage_result["shader"] = "SAME"

        # ShaderReflection
        refl_diff = _diff_dicts(
            sa.get("ShaderReflection"),
            sb.get("ShaderReflection"),
        )
        if refl_diff:
            stage_result["ShaderReflection"] = refl_diff
            stage_has_diff = True
        else:
            stage_result["ShaderReflection"] = "SAME"

        # bindings
        bindings_diff = _diff_bindings(
            sa.get("bindings", {}),
            sb.get("bindings", {}),
        )
        if bindings_diff:
            stage_result["bindings"] = bindings_diff
            stage_has_diff = True
        else:
            stage_result["bindings"] = "SAME"

        if stage_has_diff:
            result[name] = stage_result
            has_diff = True
        else:
            result[name] = "SAME"

    return result if has_diff else None
