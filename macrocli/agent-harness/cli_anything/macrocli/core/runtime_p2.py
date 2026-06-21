# ruff: noqa: F403, F405, E501
from .runtime_base import *  # noqa: F403

# fmt: off
from .runtime_p1 import ExecutionResult, _check_condition  # noqa: E402,E501
# fmt: on


class MacroRuntime:
    """Executes macros end-to-end."""

    def __init__(
        self,
        registry: Optional[MacroRegistry] = None,
        routing_engine: Optional[RoutingEngine] = None,
        session: Optional[ExecutionSession] = None,
    ):
        self.registry = registry or MacroRegistry()
        self.routing = routing_engine or RoutingEngine()
        self.session = session or ExecutionSession()

    # ── Public API ───────────────────────────────────────────────────────

    def execute(
        self,
        macro_name: str,
        params: dict,
        dry_run: bool = False,
    ) -> ExecutionResult:
        """Execute a macro by name with the given parameters.

        Args:
            macro_name: Name of the macro to execute.
            params: Input parameters (raw, may be strings from CLI).
            dry_run: If True, skip all side effects and return simulated success.

        Returns:
            ExecutionResult with success status, outputs, and telemetry.
        """
        t0 = time.time()

        # 1. Load macro
        try:
            macro = self.registry.load(macro_name)
        except KeyError as exc:
            return ExecutionResult(success=False, macro_name=macro_name, error=str(exc))

        # 2. Resolve + validate params
        resolved = macro.resolve_params(params)
        param_errors = macro.validate_params(resolved)
        if param_errors:
            return ExecutionResult(
                success=False,
                macro_name=macro_name,
                error="Parameter validation failed:\n"
                + "\n".join(f"  - {e}" for e in param_errors),
            )

        # 3. Check preconditions
        precond_errors = self.check_conditions(macro.preconditions, resolved)
        if precond_errors:
            return ExecutionResult(
                success=False,
                macro_name=macro_name,
                error="Preconditions not met:\n"
                + "\n".join(f"  - {e}" for e in precond_errors),
            )

        # 4. Execute steps
        step_results: list[StepResult] = []
        context = BackendContext(
            params=resolved,
            previous_results=step_results,
            dry_run=dry_run,
        )

        aborted = False
        abort_error = ""
        for step in macro.steps:
            context.timeout_ms = step.timeout_ms
            try:
                result = self.routing.execute_step(step, resolved, context)
            except Exception as exc:
                result = StepResult(
                    success=False,
                    error=f"Unhandled exception in step '{step.id}': {exc}",
                    backend_used=step.backend,
                )

            step_results.append(result)

            if not result.success:
                if step.on_failure == "fail":
                    aborted = True
                    abort_error = f"Step '{step.id}' failed: {result.error}"
                    break
                elif step.on_failure == "skip":
                    continue
                # on_failure == "continue" — keep going regardless

        # 5. Check postconditions (skip if already failed)
        postcond_errors: list[str] = []
        if not aborted:
            postcond_errors = self.check_conditions(macro.postconditions, resolved)

        success = not aborted and not postcond_errors

        # 6. Collect outputs
        output = self._collect_outputs(macro, resolved, step_results) if success else {}

        # 7. Build error string
        error = ""
        if aborted:
            error = abort_error
        elif postcond_errors:
            error = "Postconditions failed:\n" + "\n".join(
                f"  - {e}" for e in postcond_errors
            )

        # 8. Telemetry
        duration_ms = (time.time() - t0) * 1000
        backends_used = list({r.backend_used for r in step_results if r.backend_used})
        telemetry = {
            "duration_ms": duration_ms,
            "steps_total": len(macro.steps),
            "steps_run": len(step_results),
            "backends_used": backends_used,
            "dry_run": dry_run,
        }

        # 9. Record in session
        record = RunRecord(
            macro_name=macro_name,
            params=params,
            success=success,
            output=output,
            error=error,
            duration_ms=duration_ms,
            backends_used=backends_used,
            steps_run=len(step_results),
        )
        self.session.record(record)

        return ExecutionResult(
            success=success,
            macro_name=macro_name,
            output=output,
            error=error,
            step_results=step_results,
            telemetry=telemetry,
        )

    def check_conditions(
        self,
        conditions: list[MacroCondition],
        params: dict,
    ) -> list[str]:
        """Evaluate a list of conditions; return list of failure messages."""
        errors: list[str] = []
        for cond in conditions:
            err = _check_condition(cond, params)
            if err:
                errors.append(err)
        return errors

    def validate_macro(self, macro_name: str) -> list[str]:
        """Load and structurally validate a macro; return error list."""
        try:
            macro = self.registry.load(macro_name)
        except KeyError as exc:
            return [str(exc)]
        return macro.validate()

    # ── Helpers ──────────────────────────────────────────────────────────

    def _collect_outputs(
        self,
        macro: MacroDefinition,
        params: dict,
        step_results: list[StepResult],
    ) -> dict:
        """Resolve declared macro outputs into a concrete dict."""
        out: dict[str, Any] = {}
        for output_spec in macro.outputs:
            name = output_spec.name
            if output_spec.path:
                out[name] = substitute(output_spec.path, params)
            elif output_spec.value is not None:
                out[name] = substitute(output_spec.value, params)
        # Always include combined step outputs under 'steps'
        out["_steps"] = [r.output for r in step_results]
        return out
