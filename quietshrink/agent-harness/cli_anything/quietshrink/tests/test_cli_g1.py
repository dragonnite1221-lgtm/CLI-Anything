# ruff: noqa: F403, F405, E501
from .test_cli_helpers import *  # noqa: F403


class TestCompress:
    @patch("cli_anything.quietshrink.quietshrink_cli.find_bash_cli")
    @patch("subprocess.run")
    def test_compress_emits_bash_json(
        self,
        mock_run: MagicMock,
        mock_find: MagicMock,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        mock_find.return_value = Path("/fake/quietshrink")
        sample = tmp_path / "rec.mov"
        sample.write_bytes(b"x" * 1024)

        bash_response = {
            "input": str(sample),
            "output": str(tmp_path / "out.mov"),
            "input_size": 1024,
            "output_size": 256,
            "saved_percent": 75.0,
            "quality_preset": "transparent",
            "q_value": 60,
        }
        mock_run.return_value = MagicMock(
            returncode=0, stdout=json.dumps(bash_response), stderr=""
        )

        result = runner.invoke(cli, ["compress", str(sample), "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["quality_preset"] == "transparent"
        assert data["saved_percent"] == 75.0

    @patch("cli_anything.quietshrink.quietshrink_cli.find_bash_cli")
    @patch("subprocess.run")
    def test_compress_passes_quality_flag(
        self,
        mock_run: MagicMock,
        mock_find: MagicMock,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        mock_find.return_value = Path("/fake/quietshrink")
        sample = tmp_path / "rec.mov"
        sample.write_bytes(b"x")

        mock_run.return_value = MagicMock(
            returncode=0, stdout='{"saved_percent": 90}', stderr=""
        )

        result = runner.invoke(cli, ["compress", str(sample), "-q", "tiny", "--json"])
        assert result.exit_code == 0
        invoked_args = mock_run.call_args[0][0]
        assert "--quality" in invoked_args
        assert "tiny" in invoked_args

    @patch("cli_anything.quietshrink.quietshrink_cli.find_bash_cli")
    @patch("subprocess.run")
    def test_compress_handles_bash_failure(
        self,
        mock_run: MagicMock,
        mock_find: MagicMock,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        mock_find.return_value = Path("/fake/quietshrink")
        sample = tmp_path / "rec.mov"
        sample.write_bytes(b"x")

        mock_run.side_effect = subprocess.CalledProcessError(
            1,
            ["quietshrink"],
            stderr="ffmpeg crashed",
        )

        result = runner.invoke(cli, ["compress", str(sample), "--json"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["error"] == "compression_failed"
        assert "ffmpeg crashed" in data["stderr"]
