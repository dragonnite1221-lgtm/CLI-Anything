# ruff: noqa: F403, F405, E501
from .macro_model_base import *  # noqa: F403


@dataclass
class MacroParameter:
    name: str
    type: str = "string"  # string | integer | boolean | list | dict
    required: bool = False
    default: Any = None
    description: str = ""
    example: Any = None
    enum: Optional[list] = None
    min: Optional[float] = None
    max: Optional[float] = None

    def validate_value(self, value: Any) -> list[str]:
        """Return list of validation error strings (empty if valid)."""
        errors: list[str] = []
        if value is None:
            if self.required:
                errors.append(f"Parameter '{self.name}' is required.")
            return errors

        if self.type == "integer":
            if not isinstance(value, int):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    errors.append(f"Parameter '{self.name}' must be an integer.")
                    return errors
            if self.min is not None and value < self.min:
                errors.append(f"Parameter '{self.name}' must be >= {self.min}.")
            if self.max is not None and value > self.max:
                errors.append(f"Parameter '{self.name}' must be <= {self.max}.")

        if self.enum and value not in self.enum:
            errors.append(
                f"Parameter '{self.name}' must be one of {self.enum}, got {value!r}."
            )
        return errors


@dataclass
class MacroStep:
    backend: str  # native_api | file_transform | semantic_ui | gui_macro | recovery
    action: str  # backend-specific action name
    id: str = ""
    params: dict = field(default_factory=dict)
    timeout_ms: int = 30_000
    on_failure: str = "fail"  # fail | skip | continue
    retry_max: int = 0
    retry_backoff_ms: list[int] = field(default_factory=lambda: [1000])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "backend": self.backend,
            "action": self.action,
            "params": self.params,
            "timeout_ms": self.timeout_ms,
            "on_failure": self.on_failure,
            "retry_max": self.retry_max,
            "retry_backoff_ms": self.retry_backoff_ms,
        }


@dataclass
class MacroCondition:
    """A single pre- or post-condition check.

    Supported types (derived from the YAML key):
      file_exists: <path>
      file_size_gt: [<path>, <bytes>]
      process_running: <name>
      env_var: <name>
      always: true | false
    """

    type: str
    args: Any  # depends on type

    def to_dict(self) -> dict:
        return {"type": self.type, "args": self.args}

    @classmethod
    def from_dict(cls, d: dict) -> "MacroCondition":
        """Parse a condition dict like {file_exists: /tmp/out.png}."""
        if not isinstance(d, dict) or len(d) != 1:
            raise ValueError(f"Condition must be a single-key dict, got: {d!r}")
        ctype, args = next(iter(d.items()))
        return cls(type=ctype, args=args)


@dataclass
class MacroOutput:
    name: str
    description: str = ""
    path: Optional[str] = None  # raw template string (may contain ${...})
    value: Optional[Any] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "path": self.path,
            "value": self.value,
        }
