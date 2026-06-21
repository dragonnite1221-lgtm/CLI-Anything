# ruff: noqa: F403, F405, E501
from .recorder_base import *  # noqa: F403


class MacroRecorderMixin2:
    def to_yaml(self, parameters: Optional[dict] = None) -> str:
        """Generate macro YAML from recorded steps.

        Args:
            parameters: Dict of {param_name: spec} built by
                        apply_parameterization(). If None, all type_text
                        values remain hardcoded.
        """
        steps = [s.to_step_dict() for s in self._steps if s.to_step_dict()]

        macro = {
            "name": self.macro_name,
            "version": "1.0",
            "description": f"Recorded macro: {self.macro_name}",
            "tags": ["recorded", "visual_anchor"],
            "parameters": parameters or {},
            "preconditions": [],
            "steps": steps,
            "postconditions": [],
            "outputs": [],
            "agent_hints": {
                "danger_level": "moderate",
                "side_effects": ["gui_interaction"],
                "reversible": False,
                "recorded": True,
            },
        }
        return yaml.dump(
            macro, allow_unicode=True, sort_keys=False, default_flow_style=False
        )

    def save(
        self, output_path: Optional[str] = None, parameters: Optional[dict] = None
    ) -> str:
        """Write the generated YAML to a file. Returns the path."""
        if output_path is None:
            output_path = str(self.output_dir / f"{self.macro_name}.yaml")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(
            self.to_yaml(parameters=parameters), encoding="utf-8"
        )
        print(f"[recorder] Saved macro to: {output_path}", flush=True)
        return output_path

    def save_as_package(
        self,
        output_dir: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> str:
        """Save as a macro package folder:
            <macro_name>/
              macro.yaml
              snapshots/
                step_XXX_end_state.png  (copied from recorded locations)

        Returns path to macro.yaml.
        """
        pkg_dir = Path(output_dir or self.output_dir) / self.macro_name
        pkg_dir.mkdir(parents=True, exist_ok=True)
        snapshots_dir = pkg_dir / "snapshots"
        snapshots_dir.mkdir(exist_ok=True)

        # Copy any end_state snapshots into the package and update paths
        for step in self._steps:
            if step.is_agent_step and step.agent_end_state_snapshot:
                src = Path(step.agent_end_state_snapshot)
                if src.is_file():
                    dst = snapshots_dir / src.name
                    import shutil

                    if src.resolve() != dst.resolve():
                        shutil.copy2(src, dst)
                    # Update path to be relative to macro.yaml
                    step.agent_end_state_snapshot = f"snapshots/{src.name}"

        yaml_path = str(pkg_dir / "macro.yaml")
        Path(yaml_path).write_text(
            self.to_yaml(parameters=parameters), encoding="utf-8"
        )
        print(f"[recorder] Saved macro package to: {pkg_dir}/", flush=True)
        return yaml_path
