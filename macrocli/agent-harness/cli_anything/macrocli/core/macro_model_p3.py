# ruff: noqa: F403, F405, E501
from .macro_model_base import *  # noqa: F403

# fmt: off
from .macro_model_p1 import MacroParameter  # noqa: E402,E501
from .macro_model_p2 import MacroDefinition, _parse_condition, _parse_output, _parse_parameter, _parse_step  # noqa: E402,E501
# fmt: on


def load_from_yaml(path: str) -> MacroDefinition:
    """Load and parse a macro definition from a YAML file."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Macro file not found: {path}")
    with open(p, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if not isinstance(raw, dict):
        raise ValueError(
            f"Macro YAML must be a mapping, got {type(raw).__name__}: {path}"
        )

    parameters: dict[str, MacroParameter] = {}
    for pname, praw in (raw.get("parameters") or {}).items():
        if isinstance(praw, dict):
            parameters[pname] = _parse_parameter(pname, praw)
        else:
            # shorthand: parameter_name: string
            parameters[pname] = MacroParameter(name=pname, type=str(praw))

    steps = [_parse_step(i, s) for i, s in enumerate(raw.get("steps") or [])]
    preconditions = [_parse_condition(c) for c in (raw.get("preconditions") or [])]
    postconditions = [_parse_condition(c) for c in (raw.get("postconditions") or [])]
    outputs = [_parse_output(o) for o in (raw.get("outputs") or [])]

    macro = MacroDefinition(
        name=raw.get("name", p.stem),
        version=str(raw.get("version", "1.0")),
        description=raw.get("description", ""),
        parameters=parameters,
        preconditions=preconditions,
        steps=steps,
        postconditions=postconditions,
        outputs=outputs,
        tags=raw.get("tags", []),
        composable=raw.get("composable", False),
        agent_hints=raw.get("agent_hints", {}),
        source_path=str(p.resolve()),
    )
    return macro
