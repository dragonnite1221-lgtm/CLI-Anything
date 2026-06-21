# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestGeneratedCommandsImportMixin1:
    def test_generated_keyword_query_option_uses_safe_callback_name(self):
        from click.testing import CliRunner
        from cli_anything.mailchimp.commands.templates import templates_group

        client = MagicMock()
        client.get.return_value = {"templates": []}

        with patch("cli_anything.mailchimp.core.client.get_client", return_value=client):
            result = CliRunner().invoke(templates_group, ["list", "--type", "user"])

        assert result.exit_code == 0, result.output
        client.get.assert_called_once_with("/templates", params={"type": "user"})
    def test_campaign_shortcut_aliases_match_generated_commands(self):
        from click.testing import CliRunner
        from cli_anything.mailchimp.commands.campaigns import campaigns_group

        client = MagicMock()
        client.get.return_value = {"items": []}

        with patch("cli_anything.mailchimp.core.client.get_client", return_value=client):
            content = CliRunner().invoke(campaigns_group, ["list-content", "campaign-1"])
            checklist = CliRunner().invoke(campaigns_group, ["list-send-checklist", "campaign-1"])

        assert content.exit_code == 0, content.output
        assert checklist.exit_code == 0, checklist.output
        client.get.assert_any_call("/campaigns/campaign-1/content", params=None)
        client.get.assert_any_call("/campaigns/campaign-1/send-checklist", params=None)
    def test_report_shortcut_aliases_match_generated_commands(self):
        from click.testing import CliRunner
        from cli_anything.mailchimp.commands.reports import reports_group

        client = MagicMock()
        client.get.return_value = {"items": []}

        shortcuts = {
            "list-email-activity": "/reports/campaign-1/email-activity",
            "list-click-details": "/reports/campaign-1/click-details",
            "list-open-details": "/reports/campaign-1/open-details",
            "list-unsubscribed": "/reports/campaign-1/unsubscribed",
            "list-locations": "/reports/campaign-1/locations",
            "list-domain-performance": "/reports/campaign-1/domain-performance",
        }

        with patch("cli_anything.mailchimp.core.client.get_client", return_value=client):
            for command in shortcuts:
                result = CliRunner().invoke(reports_group, [command, "campaign-1"])
                assert result.exit_code == 0, result.output

        for path in shortcuts.values():
            client.get.assert_any_call(path, params=None)
    def test_automation_and_segment_shortcut_aliases_match_generated_commands(self):
        from click.testing import CliRunner
        from cli_anything.mailchimp.commands.automations import automations_group
        from cli_anything.mailchimp.commands.lists import lists_group

        client = MagicMock()
        client.get.return_value = {"items": []}

        with patch("cli_anything.mailchimp.core.client.get_client", return_value=client):
            emails = CliRunner().invoke(automations_group, ["list-emails", "workflow-1"])
            segments = CliRunner().invoke(lists_group, ["list-lists-id-segments", "list-1"])

        assert emails.exit_code == 0, emails.output
        assert segments.exit_code == 0, segments.output
        client.get.assert_any_call("/automations/workflow-1/emails", params=None)
        client.get.assert_any_call("/lists/list-1/segments", params=None)
    def test_ping_group_invokes_health_check_without_list_subcommand(self):
        from click.testing import CliRunner
        from cli_anything.mailchimp.mailchimp_cli import cli

        client = MagicMock()
        client.get.return_value = {"health_status": "Everything's Chimpy!"}

        with patch("cli_anything.mailchimp.core.client.get_client", return_value=client):
            result = CliRunner().invoke(cli, ["ping"])

        assert result.exit_code == 0, result.output
        client.get.assert_called_once_with("/ping", params=None)
    def test_create_members_alias_matches_generated_command(self):
        from click.testing import CliRunner
        from cli_anything.mailchimp.commands.lists import lists_group

        client = MagicMock()
        client.post.return_value = {"id": "member-1"}

        with patch("cli_anything.mailchimp.core.client.get_client", return_value=client):
            result = CliRunner().invoke(
                lists_group,
                [
                    "create-members",
                    "list-1",
                    "--data",
                    '{"email_address":"user@example.com","status":"subscribed"}',
                    "--skip-merge-validation",
                    "true",
                ],
            )

        assert result.exit_code == 0, result.output
        client.post.assert_called_once_with(
            "/lists/list-1/members",
            json={"email_address": "user@example.com", "status": "subscribed"},
            params={"skip_merge_validation": True},
        )
