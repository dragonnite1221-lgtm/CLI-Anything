# ruff: noqa: F403, F405, E501
from .recorder_base import *  # noqa: F403


class MacroRecorderMixin4:
    def apply_parameterization(self, assignments: dict[int, str]) -> dict[str, dict]:
        """Replace type_text values with ${param} placeholders in-place.

        Args:
            assignments: {list_index: param_name} for steps to parameterize.
                         Steps not present keep their hardcoded value.

        Returns:
            parameters block ready to pass into to_yaml().
        """
        parameters: dict[str, dict] = {}
        for idx, param_name in assignments.items():
            step = self._steps[idx]
            original = step.text
            step.text = f"${{{param_name}}}"

            # Infer type from the original value
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
        return parameters
