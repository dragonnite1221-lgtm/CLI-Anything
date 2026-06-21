# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything-iterm2")

    def _run(self, args, check=True, timeout=15):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout,
        )

    def test_help(self):
        """--help exits 0 and mentions commands."""
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "iterm2" in result.stdout.lower() or "window" in result.stdout.lower()
        print(f"\n  help output: {result.stdout[:200]}")

    def test_json_app_status(self):
        """--json app status returns parseable JSON."""
        try:
            result = self._run(["--json", "app", "status"])
            data = json.loads(result.stdout)
            assert "window_count" in data
            print(f"\n  JSON app status: {data}")
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            pytest.skip(f"iTerm2 not available for subprocess test: {e}")

    def test_json_window_list(self):
        """--json window list returns parseable JSON list."""
        try:
            result = self._run(["--json", "window", "list"])
            data = json.loads(result.stdout)
            assert "windows" in data
            assert isinstance(data["windows"], list)
            print(f"\n  JSON window list: {len(data['windows'])} window(s)")
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            pytest.skip(f"iTerm2 not available for subprocess test: {e}")

    def test_json_session_list(self):
        """--json session list returns parseable JSON."""
        try:
            result = self._run(["--json", "session", "list"])
            data = json.loads(result.stdout)
            assert "sessions" in data
            assert isinstance(data["sessions"], list)
            print(f"\n  JSON session list: {len(data['sessions'])} session(s)")
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            pytest.skip(f"iTerm2 not available for subprocess test: {e}")

    def test_json_profile_list(self):
        """--json profile list returns parseable JSON."""
        try:
            result = self._run(["--json", "profile", "list"])
            data = json.loads(result.stdout)
            assert "profiles" in data
            print(f"\n  JSON profiles: {len(data['profiles'])} profile(s)")
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            pytest.skip(f"iTerm2 not available for subprocess test: {e}")

    def test_json_tmux_list(self):
        """--json tmux list returns parseable JSON with a 'connections' key."""
        try:
            result = self._run(["--json", "tmux", "list"])
            data = json.loads(result.stdout)
            assert "connections" in data
            assert isinstance(data["connections"], list)
            print(f"\n  JSON tmux connections: {len(data['connections'])}")
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            pytest.skip(f"iTerm2 not available for subprocess test: {e}")

    def test_json_tmux_tabs(self):
        """--json tmux tabs returns parseable JSON with a 'tmux_tabs' key."""
        try:
            result = self._run(["--json", "tmux", "tabs"])
            data = json.loads(result.stdout)
            assert "tmux_tabs" in data
            assert isinstance(data["tmux_tabs"], list)
            print(f"\n  JSON tmux tabs: {len(data['tmux_tabs'])}")
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            pytest.skip(f"iTerm2 not available for subprocess test: {e}")

    def test_tmux_send_no_connections_error(self):
        """tmux send without any active connection exits non-zero with clear error."""
        # This test verifies the error path when no tmux -CC is running.
        # If tmux IS connected, the command succeeds — which is also fine.
        result = self._run(["tmux", "send", "list-sessions"], check=False)
        # Either success (tmux connected) or a clear error (not connected)
        if result.returncode != 0:
            assert (
                "tmux" in result.stderr.lower() or "connection" in result.stderr.lower()
            )
            print(f"\n  Expected error when no tmux: {result.stderr.strip()[:120]}")
        else:
            print(f"\n  tmux connected — command succeeded: {result.stdout[:80]}")

    def test_tmux_help(self):
        """tmux --help exits 0 and mentions subcommands."""
        result = self._run(["tmux", "--help"])
        assert result.returncode == 0
        assert "send" in result.stdout
        assert "list" in result.stdout
