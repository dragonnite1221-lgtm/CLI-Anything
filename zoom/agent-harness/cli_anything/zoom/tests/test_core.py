# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestAuthSetup:
    """Test OAuth configuration."""

    def test_setup_saves_config(self, runner, mock_config):
        """auth setup should save client_id and client_secret."""
        result = runner.invoke(
            cli,
            [
                "auth",
                "setup",
                "--client-id",
                "test_id_123",
                "--client-secret",
                "test_secret_456",
            ],
        )
        assert result.exit_code == 0
        assert "configured" in result.output.lower() or "OAuth" in result.output

        config_file = mock_config / "config.json"
        assert config_file.exists()
        config = json.loads(config_file.read_text())
        assert config["client_id"] == "test_id_123"
        assert config["client_secret"] == "test_secret_456"

    def test_setup_with_custom_redirect(self, runner, mock_config):
        """auth setup should accept custom redirect URI."""
        result = runner.invoke(
            cli,
            [
                "auth",
                "setup",
                "--client-id",
                "id",
                "--client-secret",
                "secret",
                "--redirect-uri",
                "http://localhost:9999/cb",
            ],
        )
        assert result.exit_code == 0

        config = json.loads((mock_config / "config.json").read_text())
        assert config["redirect_uri"] == "http://localhost:9999/cb"

    def test_status_not_configured(self, runner, mock_config):
        """auth status should report not configured when no config exists."""
        result = runner.invoke(cli, ["auth", "status"])
        assert result.exit_code == 0
        assert "False" in result.output or "false" in result.output.lower()

    def test_logout_no_tokens(self, runner, mock_config):
        """auth logout should succeed even when no tokens exist."""
        result = runner.invoke(cli, ["auth", "logout"])
        assert result.exit_code == 0
        assert "logged_out" in result.output.lower() or "Logged out" in result.output


class TestAuthLogin:
    """Test login flow (mocked)."""

    def test_login_without_config_fails(self, runner, mock_config):
        """Login should fail without OAuth config."""
        result = runner.invoke(cli, ["auth", "login", "--code", "dummy"])
        assert result.exit_code == 1
        assert "not configured" in result.output.lower() or "Error" in result.output

    def test_login_with_code(self, runner, mock_config):
        """Login with manual code should exchange it for tokens."""
        # Setup config first
        (mock_config / "config.json").write_text(
            json.dumps(
                {
                    "client_id": "id",
                    "client_secret": "secret",
                    "redirect_uri": "http://localhost:4199/callback",
                }
            )
        )

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "at_123",
            "refresh_token": "rt_456",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = MagicMock()

        with (
            patch(
                "cli_anything.zoom.utils.zoom_backend.requests.post",
                return_value=mock_response,
            ),
            patch(
                "cli_anything.zoom.utils.zoom_backend.api_get",
                return_value={
                    "email": "test@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "account_id": "acc123",
                },
            ),
        ):
            result = runner.invoke(cli, ["auth", "login", "--code", "auth_code_xyz"])

        assert result.exit_code == 0
        token_file = mock_config / "tokens.json"
        assert token_file.exists()
        tokens = json.loads(token_file.read_text())
        assert tokens["access_token"] == "at_123"
