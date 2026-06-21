# ruff: noqa: F403, F405, E501
from ._test_cli_hub_base import *  # noqa: F403
from ._test_cli_hub_p0 import _make_preview_bundle  # noqa: F401,E501
from ._test_cli_hub_p1 import _make_preview_session  # noqa: F401,E501


class TestPreviewBundle:
    """Tests for preview bundle inspection and HTML rendering."""

    def test_inspect_bundle(self, tmp_path):
        bundle_dir = _make_preview_bundle(tmp_path)
        payload = inspect_bundle(str(bundle_dir))
        assert payload["artifact_count"] == 2
        assert payload["manifest"]["software"] == "shotcut"
        assert payload["summary"]["headline"] == "Quick preview rendered"

    def test_inspect_bundle_loads_trajectory_from_context_path(self, tmp_path):
        bundle_dir = _make_preview_bundle(tmp_path, with_trajectory=True)
        payload = inspect_bundle(str(bundle_dir))
        assert payload["trajectory"]["protocol"] == "preview-trajectory/v1"
        assert payload["trajectory"]["step_count"] == 1
        assert payload["trajectory"]["recent_publish_reason"] == "capture"

    def test_render_inspect_text(self, tmp_path):
        bundle_dir = _make_preview_bundle(tmp_path)
        text = render_inspect_text(str(bundle_dir))
        assert "Bundle:" in text
        assert "Artifacts" in text
        assert "Midpoint frame" in text

    def test_render_html(self, tmp_path):
        bundle_dir = _make_preview_bundle(tmp_path)
        output_path = tmp_path / "preview.html"
        rendered = render_html(str(bundle_dir), str(output_path))
        assert rendered == str(output_path.resolve())
        content = output_path.read_text()
        assert "CLI-Anything Preview Bundle" in content
        assert "Quick preview rendered" in content
        assert "artifacts/hero.png" in content
        assert "artifacts/preview.mp4" in content

    def test_previews_inspect_cli_command(self, tmp_path):
        bundle_dir = _make_preview_bundle(tmp_path)
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["previews", "inspect", str(bundle_dir)])
        assert result.exit_code == 0
        assert "Quick preview rendered" in result.output

    def test_previews_html_cli_command(self, tmp_path):
        bundle_dir = _make_preview_bundle(tmp_path)
        output_path = tmp_path / "bundle-preview.html"
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["previews", "html", str(bundle_dir), "-o", str(output_path)])
        assert result.exit_code == 0
        assert str(output_path) in result.output
        assert output_path.is_file()

    def test_inspect_session(self, tmp_path):
        session_dir = _make_preview_session(tmp_path)
        payload = inspect_session(str(session_dir))
        assert payload["session"]["software"] == "shotcut"
        assert payload["current_bundle"]["manifest"]["bundle_id"] == "20260419T104530Z_deadbeef_quick"

    def test_inspect_session_loads_trajectory(self, tmp_path):
        session_dir = _make_preview_session(tmp_path, with_trajectory=True)
        payload = inspect_session(str(session_dir))
        assert payload["trajectory"]["protocol"] == "preview-trajectory/v1"
        assert payload["trajectory"]["step_count"] == 2
        assert payload["trajectory"]["current_step_id"] == "step-002"
        assert payload["trajectory"]["recent_publish_reason"] == "manual-push"

    def test_render_session_text(self, tmp_path):
        session_dir = _make_preview_session(tmp_path)
        text = render_session_text(str(session_dir))
        assert "Live Session:" in text
        assert "Watch:" in text
        assert "History" in text

    def test_render_session_text_with_trajectory(self, tmp_path):
        session_dir = _make_preview_session(tmp_path, with_trajectory=True)
        text = render_session_text(str(session_dir))
        assert "Trajectory" in text
        assert "Current step: step-002" in text
        assert "Recent publish: manual-push" in text
        assert "cli-anything-shotcut preview live push --recipe quick" in text

    def test_render_live_html(self, tmp_path):
        session_dir = _make_preview_session(tmp_path)
        output_path = tmp_path / "live.html"
        rendered = render_live_html(str(session_dir), str(output_path), poll_ms=800)
        assert rendered == str(output_path.resolve())
        content = output_path.read_text()
        assert "CLI-Anything Live Preview Session" in content
        assert 'const CURRENT_LINK = "current";' in content
        assert "manifest = await fetchJson(`${CURRENT_LINK}/manifest.json`);" in content
        assert "const POLL_MS = 800;" in content

    def test_render_live_html_with_trajectory(self, tmp_path):
        session_dir = _make_preview_session(tmp_path, with_trajectory=True)
        output_path = tmp_path / "live-trajectory.html"
        render_live_html(str(session_dir), str(output_path), poll_ms=600)
        content = output_path.read_text()
        assert 'const TRAJECTORY_CANDIDATES = ["trajectory.json", "timeline.json"];' in content
        assert "function normalizeTrajectory(session, payload)" in content
        assert "Trajectory Timeline" in content
        assert "trajectory_step_count" in content
        assert "latest_publish_reason" in content

    @patch("cli_hub.preview.subprocess.Popen")
    @patch("cli_hub.preview.shutil.which")
    def test_open_in_browser_prefers_app_mode(self, mock_which, mock_popen):
        mock_which.side_effect = lambda binary: f"/usr/bin/{binary}" if binary == "chromium" else None
        mock_popen.return_value = MagicMock(pid=4321)
        result = open_in_browser("http://127.0.0.1:9933/live.html")
        assert result["launched"] is True
        assert result["browser"] == "chromium"
        assert "--app=http://127.0.0.1:9933/live.html" in result["command"]

    def test_previews_inspect_cli_handles_session(self, tmp_path):
        session_dir = _make_preview_session(tmp_path)
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["previews", "inspect", str(session_dir)])
        assert result.exit_code == 0
        assert "Live Session:" in result.output

    def test_previews_html_cli_renders_session(self, tmp_path):
        session_dir = _make_preview_session(tmp_path)
        output_path = tmp_path / "session-live.html"
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["previews", "html", str(session_dir), "-o", str(output_path), "--poll-ms", "700"])
        assert result.exit_code == 0
        assert output_path.is_file()
        assert "const POLL_MS = 700;" in output_path.read_text()

    def test_previews_help_and_cli(self, tmp_path):
        session_dir = _make_preview_session(tmp_path, with_trajectory=True)
        runner = click.testing.CliRunner()
        help_result = runner.invoke(main, ["--help"])
        assert help_result.exit_code == 0
        assert "previews" in help_result.output
        assert "\n  review" not in help_result.output
        assert "\n  open-preview" not in help_result.output

        inspect_result = runner.invoke(main, ["previews", "inspect", str(session_dir)])
        assert inspect_result.exit_code == 0
        assert "Trajectory" in inspect_result.output
        assert "Current step: step-002" in inspect_result.output
