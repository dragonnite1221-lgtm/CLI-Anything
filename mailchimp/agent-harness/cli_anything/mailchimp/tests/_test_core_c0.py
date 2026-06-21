# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestGeneratedCommandsImportMixin0:
    """Verify every generated command module imports cleanly and registers commands.

    This catches codegen regressions like C1 (builtin shadowing) which would
    cause Click to fail silently or raise at import time.
    """
    def test_all_groups_importable(self):
        from cli_anything.mailchimp.commands import ALL_GROUPS

        assert len(ALL_GROUPS) == 30, f"Expected 30 groups, got {len(ALL_GROUPS)}"
        for group in ALL_GROUPS:
            assert group.name is not None
            assert len(group.commands) > 0, f"Group {group.name!r} has no commands"
    def test_generator_preserves_complete_first_line_help(self):
        from cli_anything.mailchimp._codegen.generate import _click_help_text

        description = (
            "Used for [pagination](https://mailchimp.com/developer/marketing/docs/fundamentals/#pagination) "
            "with enough context to exceed eighty characters.\nSecond line omitted."
        )

        help_text = _click_help_text(description)

        assert help_text.endswith("eighty characters.")
        assert "\n" not in help_text
    def test_no_builtin_shadowing_in_function_names(self):
        """Ensure generated functions are prefixed with _cmd_ (not builtins)."""
        import glob
        import ast
        import builtins as _builtins

        builtin_names = set(dir(_builtins))
        issues = []

        for path in glob.glob("cli_anything/mailchimp/commands/*.py"):
            tree = ast.parse(open(path).read())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name in builtin_names:
                        issues.append(f"{path}: def {node.name}()")

        assert not issues, "Builtin shadowing in generated code:\n" + "\n".join(issues)
    def test_all_commands_have_extra_params(self):
        """Every generated command must accept --extra-params (I3 fix)."""
        from cli_anything.mailchimp.commands import ALL_GROUPS
        import click

        missing = []
        for group in ALL_GROUPS:
            for cmd_name, cmd in group.commands.items():
                if isinstance(cmd, click.Group):
                    continue
                param_names = [p.name for p in cmd.params]
                if "extra_params" not in param_names:
                    missing.append(f"{group.name} {cmd_name}")

        assert not missing, "--extra-params missing on:\n" + "\n".join(missing)
    def test_generated_patch_command_forwards_query_params(self):
        from click.testing import CliRunner
        from cli_anything.mailchimp.commands.audiences import audiences_group

        client = MagicMock()
        client.patch.return_value = {"id": "contact-1"}

        with patch("cli_anything.mailchimp.core.client.get_client", return_value=client):
            result = CliRunner().invoke(
                audiences_group,
                [
                    "update",
                    "audience-1",
                    "contact-1",
                    "--data",
                    '{"email_address":"user@example.com"}',
                    "--data-mode",
                    "sync",
                ],
            )

        assert result.exit_code == 0, result.output
        client.patch.assert_called_once_with(
            "/audiences/audience-1/contacts/contact-1",
            json={"email_address": "user@example.com"},
            params={"data_mode": "sync"},
        )
    def test_generated_put_command_forwards_query_params(self):
        from click.testing import CliRunner
        from cli_anything.mailchimp.commands.lists import lists_group

        client = MagicMock()
        client.put.return_value = {"id": "member-1"}

        with patch("cli_anything.mailchimp.core.client.get_client", return_value=client):
            result = CliRunner().invoke(
                lists_group,
                [
                    "update-3",
                    "list-1",
                    "hash-1",
                    "--data",
                    '{"email_address":"user@example.com"}',
                    "--skip-merge-validation",
                    "true",
                ],
            )

        assert result.exit_code == 0, result.output
        client.put.assert_called_once_with(
            "/lists/list-1/members/hash-1",
            json={"email_address": "user@example.com"},
            params={"skip_merge_validation": True},
        )
