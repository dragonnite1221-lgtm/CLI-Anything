# ruff: noqa: F403, F405, E501
from .test_parity_helpers import *  # noqa: F403


class TestParityParameters:
    """Every MCP parameter must map to a Click option with the right shape."""

    def setup_method(self):
        self.registry = load_registry()

    def test_every_param_has_cli_option(self):
        """For each MCP param, the Click command has a matching option."""
        missing = []
        for tool in self.registry:
            cmd = tool_group.commands.get(tool.short_name)
            assert cmd is not None, f"missing command for {tool.short_name}"
            cli_opt_names = set()
            for param in cmd.params:
                if hasattr(param, "opts"):
                    for opt in param.opts:
                        # Strip leading dashes and normalize
                        clean = opt.lstrip("-")
                        # Boolean flags come as "--flag/--no-flag" so the raw
                        # opt may already be "flag" or "no-flag".
                        if clean.startswith("no-"):
                            clean = clean[3:]
                        cli_opt_names.add(clean)
            for mcp_param in tool.params:
                expected = _cli_name_for(mcp_param.name)
                if expected not in cli_opt_names:
                    missing.append(f"{tool.name}.{mcp_param.name} → --{expected}")
        assert not missing, f"Missing CLI options for params:\n" + "\n".join(missing)

    def test_required_params_are_required_in_click(self):
        """Required MCP params must be required in Click — covers all types.

        Previously this test skipped object/array params on the theory
        that JSON-string inputs were always optional. That masked a real
        parser regression (safari_mock_route.response / safari_run_script.steps
        were wrongly marked optional). The fix in extract_tools.py is
        locked in by this test now covering all types.
        """
        drift = []
        for tool in self.registry:
            cmd = tool_group.commands.get(tool.short_name)
            if cmd is None:
                continue
            click_required_by_name = {}
            for cp in cmd.params:
                if hasattr(cp, "opts"):
                    for opt in cp.opts:
                        clean = opt.lstrip("-")
                        if clean.startswith("no-"):
                            clean = clean[3:]
                        click_required_by_name[clean] = getattr(cp, "required", False)
            for mp in tool.params:
                if not mp.required:
                    continue
                key = _cli_name_for(mp.name)
                if not click_required_by_name.get(key, False):
                    drift.append(
                        f"{tool.name}.{mp.name} ({mp.type}) is required "
                        f"in MCP but not in Click"
                    )
        assert not drift, "\n".join(drift)

    def test_enum_choices_match(self):
        """Enum params must expose the same choices."""
        drift = []
        for tool in self.registry:
            cmd = tool_group.commands.get(tool.short_name)
            if cmd is None:
                continue
            for mp in tool.params:
                if not mp.choices:
                    continue
                target_name = _cli_name_for(mp.name)
                for cp in cmd.params:
                    if not hasattr(cp, "opts"):
                        continue
                    opts_clean = [o.lstrip("-") for o in cp.opts]
                    if target_name not in opts_clean:
                        continue
                    click_type = getattr(cp, "type", None)
                    if not hasattr(click_type, "choices"):
                        drift.append(
                            f"{tool.name}.{mp.name} has choices "
                            f"{mp.choices} but Click option has no Choice type"
                        )
                        continue
                    if set(click_type.choices) != set(mp.choices):
                        drift.append(
                            f"{tool.name}.{mp.name} choices mismatch: "
                            f"registry={mp.choices} cli={click_type.choices}"
                        )
        assert not drift, "\n".join(drift)
