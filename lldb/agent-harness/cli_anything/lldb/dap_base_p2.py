# ruff: noqa: F403, F405, E501
from .dap_base_base import *  # noqa: F403

# fmt: off
from .dap_base_p1 import _stop_context_text, _stop_field_matches  # noqa: E402,E501
# fmt: on


@dataclass(frozen=True)
class StopRule:
    """Structured rule used to classify or auto-continue debugger stops."""

    name: str
    action: str = "stop"
    origin: str = "internalTrap"
    reason: str | None = None
    module: str | None = None
    function: str | None = None
    regex: str | None = None
    source: str | None = None

    @classmethod
    def from_mapping(cls, raw: dict[str, Any], *, source: str) -> "StopRule":
        if not isinstance(raw, dict):
            raise RuntimeError("stopRules entries must be objects")
        name = str(raw.get("name") or raw.get("id") or "unnamed-stop-rule")
        action = str(raw.get("action") or "stop")
        if action not in {"stop", "continue"}:
            raise RuntimeError(f"Unsupported stop rule action for {name}: {action}")
        regex = raw.get("regex")
        if regex is not None:
            try:
                re.compile(str(regex))
            except re.error as exc:
                raise RuntimeError(
                    f"Invalid stop rule regex for {name}: {exc}"
                ) from exc
        if not any(
            raw.get(key) is not None
            for key in ("reason", "module", "function", "regex")
        ):
            raise RuntimeError(
                f"Stop rule {name} must include reason, module, function, or regex"
            )
        return cls(
            name=name,
            action=action,
            origin=str(raw.get("origin") or "internalTrap"),
            reason=str(raw["reason"]) if raw.get("reason") is not None else None,
            module=str(raw["module"]) if raw.get("module") is not None else None,
            function=str(raw["function"]) if raw.get("function") is not None else None,
            regex=str(regex) if regex is not None else None,
            source=source,
        )

    def matches(self, stop_context: dict[str, Any]) -> bool:
        if self.reason and not _stop_field_matches(
            self.reason, [stop_context.get("reason"), stop_context.get("lldbReason")]
        ):
            return False
        if self.module and not _stop_field_matches(
            self.module,
            [stop_context.get("module"), stop_context.get("modulePath")],
            allow_basename=True,
        ):
            return False
        if self.function and not _stop_field_matches(
            self.function,
            [stop_context.get("function")],
            allow_symbol_suffix=True,
        ):
            return False
        if self.regex and not re.search(
            self.regex, _stop_context_text(stop_context), re.IGNORECASE
        ):
            return False
        return True

    def to_dap(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "action": self.action,
            "origin": self.origin,
            "source": self.source,
        }


__all__ = [
    "Any",
    "BinaryIO",
    "Callable",
    "DAPProtocolError",
    "LLDBDebugAdapter",
    "LLDBSession",
    "Path",
    "StopRule",
    "_first_present",
    "_raise_protocol_error",
    "_stop_context_text",
    "_stop_field_matches",
    "annotations",
    "argparse",
    "base64",
    "dataclass",
    "encode_message",
    "json",
    "main",
    "os",
    "re",
    "read_message",
    "shlex",
    "sys",
    "threading",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run cli-anything-lldb Debug Adapter Protocol server"
    )
    parser.add_argument(
        "--log-file", default=None, help="Optional file for adapter diagnostics"
    )
    parser.add_argument(
        "--profile",
        default=None,
        help="Optional stop-rule profile JSON loaded at adapter startup",
    )
    args = parser.parse_args(argv)
    adapter = LLDBDebugAdapter(log_file=args.log_file, profile_file=args.profile)
    return adapter.run()
