# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBackend:
    """Test zoom_backend utilities."""

    def test_config_save_load(self, mock_config):
        """Config should round-trip through save/load."""
        from cli_anything.zoom.utils.zoom_backend import save_config, load_config

        save_config({"client_id": "abc", "client_secret": "xyz"})
        loaded = load_config()
        assert loaded["client_id"] == "abc"
        assert loaded["client_secret"] == "xyz"

    def test_token_save_load(self, mock_config):
        """Tokens should round-trip with saved_at timestamp."""
        from cli_anything.zoom.utils.zoom_backend import save_tokens, load_tokens

        save_tokens({"access_token": "at_test", "refresh_token": "rt_test"})
        loaded = load_tokens()
        assert loaded["access_token"] == "at_test"
        assert "saved_at" in loaded

    def test_save_config_restricts_directory_and_file(self, mock_config):
        """save_config should enforce 700 on dir and 600 on config file."""
        from cli_anything.zoom.utils.zoom_backend import save_config

        with patch(
            "cli_anything.zoom.utils.zoom_backend._restrict_path"
        ) as mock_restrict:
            save_config({"client_id": "abc", "client_secret": "xyz"})

        assert (mock_config / "config.json").exists()
        assert mock_restrict.call_args_list == [
            call(mock_config, 0o700),
            call(mock_config / "config.json", 0o600),
        ]

    def test_save_tokens_restricts_directory_and_file(self, mock_config):
        """save_tokens should enforce 700 on dir and 600 on token file."""
        from cli_anything.zoom.utils.zoom_backend import save_tokens

        with patch(
            "cli_anything.zoom.utils.zoom_backend._restrict_path"
        ) as mock_restrict:
            save_tokens({"access_token": "at_test", "refresh_token": "rt_test"})

        assert (mock_config / "tokens.json").exists()
        assert mock_restrict.call_args_list == [
            call(mock_config, 0o700),
            call(mock_config / "tokens.json", 0o600),
        ]

    @pytest.mark.skipif(
        os.name == "nt",
        reason="POSIX permission bits are not supported on Windows",
    )
    def test_get_config_dir_sets_posix_700_permissions(self, mock_config):
        """get_config_dir should force 700 permissions on POSIX."""
        from cli_anything.zoom.utils.zoom_backend import get_config_dir

        mock_config.chmod(0o755)
        config_dir = get_config_dir()
        assert config_dir == mock_config
        assert stat.S_IMODE(config_dir.stat().st_mode) == 0o700

    @pytest.mark.skipif(
        os.name == "nt",
        reason="POSIX permission bits are not supported on Windows",
    )
    def test_save_config_sets_posix_600_permissions(self, mock_config):
        """save_config should force 600 on config.json on POSIX."""
        from cli_anything.zoom.utils.zoom_backend import save_config

        save_config({"client_id": "abc", "client_secret": "xyz"})
        assert stat.S_IMODE((mock_config / "config.json").stat().st_mode) == 0o600

    @pytest.mark.skipif(
        os.name == "nt",
        reason="POSIX permission bits are not supported on Windows",
    )
    def test_save_tokens_sets_posix_600_permissions(self, mock_config):
        """save_tokens should force 600 on tokens.json on POSIX."""
        from cli_anything.zoom.utils.zoom_backend import save_tokens

        save_tokens({"access_token": "at_test", "refresh_token": "rt_test"})
        assert stat.S_IMODE((mock_config / "tokens.json").stat().st_mode) == 0o600

    def test_authorize_url(self):
        """get_authorize_url should build valid URL."""
        from cli_anything.zoom.utils.zoom_backend import get_authorize_url

        url = get_authorize_url("my_client_id", "http://localhost:4199/callback")
        assert "zoom.us/oauth/authorize" in url
        assert "my_client_id" in url
        assert "response_type=code" in url

    def test_load_empty_config(self, mock_config):
        """load_config should return empty dict when no config file."""
        from cli_anything.zoom.utils.zoom_backend import load_config

        result = load_config()
        assert result == {}

    def test_load_empty_tokens(self, mock_config):
        """load_tokens should return empty dict when no token file."""
        from cli_anything.zoom.utils.zoom_backend import load_tokens

        result = load_tokens()
        assert result == {}
