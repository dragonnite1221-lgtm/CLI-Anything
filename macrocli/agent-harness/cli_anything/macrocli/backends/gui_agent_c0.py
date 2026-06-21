# ruff: noqa: F403, F405, E501
from .gui_agent_base import *  # noqa: F403


class GUIAgentBackendMixin0:
    """Execute GUI steps using a vision model (OpenAI-compatible API) to decide actions."""
    name = "gui_agent"
    priority = 60  # between semantic_ui(50) and file_transform(70)
    def execute(
        self, step: MacroStep, params: dict, context: BackendContext
    ) -> StepResult:
        t0 = time.time()
        p = substitute(step.params, params)

        if context.dry_run:
            return StepResult(
                success=True,
                output={"dry_run": True, "action": step.action},
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        if step.action == "instruct":
            return self._instruct(p, context, t0)
        elif step.action == "instruct_with_refine":
            return self._instruct_with_refine(p, context, t0)
        else:
            return StepResult(
                success=False,
                error=f"GUIAgentBackend: unknown action '{step.action}'. "
                      "Supported: 'instruct', 'instruct_with_refine'.",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )
    def is_available(self) -> bool:
        try:
            import openai  # noqa: F401
            import mss  # noqa: F401
            return True
        except ImportError:
            return False
