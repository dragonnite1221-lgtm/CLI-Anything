# ruff: noqa: F403, F405, E501
from .parameterize_base import *  # noqa: F403

# fmt: off
from .parameterize_p1 import _YamlTypeStep, interactive_parameterize  # noqa: E402,E501
# fmt: on


def parameterize_yaml_file(yaml_path: str) -> bool:
    """Interactively parameterize an existing macro YAML file in-place.

    Finds all steps with action=type_text, runs the interactive flow,
    updates the file, and returns True if any changes were made.
    """
    p = Path(yaml_path)
    if not p.is_file():
        raise FileNotFoundError(f"Macro file not found: {yaml_path}")

    with open(p, encoding="utf-8") as f:
        macro = yaml.safe_load(f)

    if not isinstance(macro, dict):
        raise ValueError("Invalid macro YAML: expected a mapping at top level.")

    steps: list[dict] = macro.get("steps") or []
    type_steps_raw = [
        (i, s)
        for i, s in enumerate(steps)
        if isinstance(s, dict)
        and s.get("action") == "type_text"
        and s.get("params", {}).get("text", "").strip()
        # Skip already-parameterized steps
        and not s["params"]["text"].startswith("${")
    ]

    if not type_steps_raw:
        print("  No hardcoded type_text steps found to parameterize.")
        return False

    # Wrap in lightweight objects for interactive_parameterize
    wrapped = [(i, _YamlTypeStep(i, s)) for i, s in type_steps_raw]

    existing_params = set((macro.get("parameters") or {}).keys())
    assignments = interactive_parameterize(wrapped, existing_params)

    if not assignments:
        return False

    # Apply in-place and collect parameter specs
    parameters: dict = dict(macro.get("parameters") or {})
    for idx, param_name in assignments.items():
        yw = next(w for i, w in wrapped if i == idx)
        original = yw.text
        yw.apply(param_name)

        # Infer type
        ptype = "string"
        try:
            int(original)
            ptype = "integer"
        except ValueError:
            try:
                float(original)
                ptype = "float"
            except ValueError:
                pass

        parameters[param_name] = {
            "type": ptype,
            "required": True,
            "description": f"Value typed at step {idx + 1}",
            "example": original,
        }

    macro["parameters"] = parameters

    with open(p, "w", encoding="utf-8") as f:
        yaml.dump(
            macro, f, allow_unicode=True, sort_keys=False, default_flow_style=False
        )

    print(f"\n  ✓ Updated: {p.resolve()}")
    return True
