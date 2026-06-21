# ruff: noqa: F403, F405, E501
from .dap_base import *  # noqa: F403


class LLDBDebugAdapterMixin4:
    def _ensure_stopped_for_target_mutation(self, operation: str):
        if not self._is_continue_active():
            return
        self._log(f"{operation}: interrupting running debuggee before target mutation")
        self._request_async_interrupt()
        with self._continue_state:
            stopped = self._continue_state.wait_for(
                lambda: not self._continue_active,
                timeout=self._mutation_stop_timeout,
            )
        if not stopped:
            raise RuntimeError(
                f"Timed out waiting for debuggee to stop before {operation}. "
                "Send a pause request and retry after the stopped event."
            )

    def _request_async_interrupt(self):
        session = self._ensure_session()
        interrupt = getattr(session, "interrupt_async", None)
        if interrupt is not None:
            return interrupt()
        return session.interrupt()

    def _configure_stop_rules(self, args: dict[str, Any]):
        rules = list(self._base_stop_rules)
        auto_continue = self._base_auto_continue_internal_breakpoints or bool(
            args.get("autoContinueInternalBreakpoints", False)
        )
        profile_path = (
            args.get("stopRuleProfile")
            or args.get("stopProfile")
            or args.get("profile")
        )
        if profile_path:
            profile_rules, profile_auto_continue = self._load_stop_profile_file(
                str(profile_path)
            )
            rules.extend(profile_rules)
            auto_continue = auto_continue or profile_auto_continue
        inline_rules = args.get("stopRules")
        if inline_rules:
            rules.extend(self._coerce_stop_rules(inline_rules, source="dap-arguments"))
        if auto_continue:
            rules.extend(self._builtin_internal_stop_rules())
        self._auto_continue_internal_breakpoints = auto_continue
        self._active_stop_rules = rules

    def _load_stop_profile_file(self, profile_file: str) -> tuple[list[StopRule], bool]:
        profile_path = Path(profile_file).expanduser().resolve()
        try:
            payload = json.loads(profile_path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise RuntimeError(
                f"Failed to read stop rule profile {profile_path}: {exc}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Invalid stop rule profile JSON {profile_path}: {exc}"
            ) from exc

        auto_continue = False
        if isinstance(payload, list):
            rules_payload = payload
        elif isinstance(payload, dict):
            auto_continue = bool(payload.get("autoContinueInternalBreakpoints", False))
            rules_payload = payload.get("stopRules", [])
        else:
            raise RuntimeError("Stop rule profile must be a JSON object or array")
        return self._coerce_stop_rules(
            rules_payload, source=str(profile_path)
        ), auto_continue

    def _coerce_stop_rules(self, raw_rules: Any, *, source: str) -> list[StopRule]:
        if not isinstance(raw_rules, list):
            raise RuntimeError("stopRules must be a list")
        return [
            StopRule.from_mapping(raw_rule, source=source) for raw_rule in raw_rules
        ]

    def _builtin_internal_stop_rules(self) -> list[StopRule]:
        return [
            StopRule(
                name="nvidia-shader-jit-debug-register",
                action="continue",
                origin="internalTrap",
                reason="breakpoint",
                regex=r"(__jit_debug_register_code|jit-debug-register)",
                source="builtin:autoContinueInternalBreakpoints",
            ),
            StopRule(
                name="windows-debugger-startup-breakpoint",
                action="continue",
                origin="internalTrap",
                regex=r"(Exception 0x80000003|ntdll\.dll`DbgBreakPoint|DbgBreakPoint)",
                source="builtin:autoContinueInternalBreakpoints",
            ),
        ]
