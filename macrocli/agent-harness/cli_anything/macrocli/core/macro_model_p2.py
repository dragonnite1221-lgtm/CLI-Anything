# ruff: noqa: F403, F405, E501
from .macro_model_base import *  # noqa: F403

# fmt: off
from .macro_model_p1 import MacroCondition, MacroOutput, MacroParameter, MacroStep  # noqa: E402,E501
# fmt: on


@dataclass
class MacroDefinition:
    name: str
    version: str = "1.0"
    description: str = ""
    parameters: dict[str, MacroParameter] = field(default_factory=dict)
    preconditions: list[MacroCondition] = field(default_factory=list)
    steps: list[MacroStep] = field(default_factory=list)
    postconditions: list[MacroCondition] = field(default_factory=list)
    outputs: list[MacroOutput] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    composable: bool = False
    agent_hints: dict = field(default_factory=dict)
    source_path: str = ""  # absolute path to the .yaml file

    # ── Validation ────────────────────────────────────────────────────

    def validate(self) -> list[str]:
        """Structural validation — returns list of error strings."""
        errors: list[str] = []
        if not self.name:
            errors.append("Macro name is required.")
        if not self.steps:
            errors.append(f"Macro '{self.name}' has no steps.")
        valid_backends = {
            "native_api",
            "file_transform",
            "semantic_ui",
            "gui_macro",
            "recovery",
            "visual_anchor",
            "gui_agent",
        }
        for i, step in enumerate(self.steps):
            if step.backend not in valid_backends:
                errors.append(
                    f"Step {i} has unknown backend '{step.backend}'. "
                    f"Valid: {sorted(valid_backends)}"
                )
            if not step.action:
                errors.append(f"Step {i} (backend={step.backend}) is missing 'action'.")
        for pname, pspec in self.parameters.items():
            if pspec.type not in (
                "string",
                "integer",
                "boolean",
                "list",
                "dict",
                "float",
            ):
                errors.append(f"Parameter '{pname}' has unknown type '{pspec.type}'.")
        return errors

    def validate_params(self, params: dict) -> list[str]:
        """Validate runtime parameter values against schema."""
        errors: list[str] = []
        for pname, pspec in self.parameters.items():
            value = params.get(pname, pspec.default)
            errors.extend(pspec.validate_value(value))
        return errors

    def resolve_params(self, params: dict) -> dict:
        """Return params with defaults filled in."""
        resolved = {}
        for pname, pspec in self.parameters.items():
            resolved[pname] = params.get(pname, pspec.default)
        # Pass through any extra params not in schema
        for k, v in params.items():
            if k not in resolved:
                resolved[k] = v
        return resolved

    # ── Serialisation ─────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "parameters": {
                n: {
                    "type": p.type,
                    "required": p.required,
                    "default": p.default,
                    "description": p.description,
                    "example": p.example,
                    "enum": p.enum,
                }
                for n, p in self.parameters.items()
            },
            "preconditions": [c.to_dict() for c in self.preconditions],
            "steps": [s.to_dict() for s in self.steps],
            "postconditions": [c.to_dict() for c in self.postconditions],
            "outputs": [o.to_dict() for o in self.outputs],
            "tags": self.tags,
            "composable": self.composable,
            "agent_hints": self.agent_hints,
            "source_path": self.source_path,
        }


_SUBST_RE = re.compile(r"\$\{([^}]+)\}")


def substitute(template: Any, params: dict) -> Any:
    """Replace ${key} placeholders in strings (and nested structures).

    Works recursively on strings, lists, and dicts.
    Leaves non-string types (int, bool, None) untouched.
    """
    if isinstance(template, str):

        def _replace(m: re.Match) -> str:
            key = m.group(1).strip()
            val = params.get(key)
            return str(val) if val is not None else m.group(0)

        return _SUBST_RE.sub(_replace, template)
    if isinstance(template, list):
        return [substitute(item, params) for item in template]
    if isinstance(template, dict):
        return {k: substitute(v, params) for k, v in template.items()}
    return template


def _parse_parameter(name: str, raw: dict) -> MacroParameter:
    return MacroParameter(
        name=name,
        type=raw.get("type", "string"),
        required=raw.get("required", False),
        default=raw.get("default"),
        description=raw.get("description", ""),
        example=raw.get("example"),
        enum=raw.get("enum"),
        min=raw.get("min"),
        max=raw.get("max"),
    )


def _parse_step(i: int, raw: dict) -> MacroStep:
    retry = raw.get("retry_policy", {}) or {}
    return MacroStep(
        id=raw.get("id", f"step_{i}"),
        backend=raw.get("backend", "native_api"),
        action=raw.get("action", ""),
        params=raw.get("params", {}),
        timeout_ms=int(
            raw.get(
                "timeout_ms",
                raw.get("timeout", "30s").replace("s", "000")
                if isinstance(raw.get("timeout"), str)
                else raw.get("timeout_ms", 30_000),
            )
        ),
        on_failure=raw.get("on_failure", "fail"),
        retry_max=retry.get("max_retries", raw.get("retry_max", 0)),
        retry_backoff_ms=retry.get("backoff_ms", [1000]),
    )


def _parse_condition(raw: Any) -> MacroCondition:
    if isinstance(raw, dict):
        return MacroCondition.from_dict(raw)
    raise ValueError(f"Cannot parse condition from {raw!r}")


def _parse_output(raw: dict) -> MacroOutput:
    return MacroOutput(
        name=raw.get("name", ""),
        description=raw.get("description", ""),
        path=raw.get("path"),
        value=raw.get("value"),
    )
