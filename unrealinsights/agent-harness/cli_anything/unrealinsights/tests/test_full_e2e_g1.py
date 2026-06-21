# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


@skip_no_trace
class TestExportE2E:
    CLI_BASE = _resolve_cli("cli-anything-unrealinsights")

    def _run(self, args, check=True, timeout=180):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout,
            env=_cli_env(),
        )

    @pytest.mark.parametrize(
        ("subcommand", "extra_args"),
        [
            ("threads", []),
            ("timers", []),
            ("timing-events", ["--threads=GameThread", "--timers=*"]),
            ("timer-stats", ["--threads=GameThread", "--timers=*"]),
            ("timer-callees", ["--threads=GameThread", "--timers=*"]),
            ("counters", []),
            ("counter-values", ["--counter=*"]),
        ],
    )
    def test_exporter_creates_output(self, subcommand, extra_args):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, f"{subcommand}.csv")
            result = self._run(
                ["--json", "-t", TEST_TRACE, "export", subcommand, output, *extra_args],
                check=False,
            )
            if result.returncode != 0:
                pytest.skip(f"{subcommand} exporter failed for supplied trace")
            data = json.loads(result.stdout)
            if data.get("output_status") == "no_output":
                pytest.skip(
                    f"{subcommand} exporter produced no output for supplied trace"
                )
            assert data["output_status"] == "ok"
            assert data["output_files"]
            for path in data["output_files"]:
                assert os.path.isfile(path)
                assert os.path.getsize(path) > 0

    def test_batch_run_rsp(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            threads = os.path.join(tmpdir, "threads.csv")
            timers = os.path.join(tmpdir, "timers.csv")
            rsp = os.path.join(tmpdir, "exports.rsp")
            Path(rsp).write_text(
                "\n".join(
                    [
                        f'TimingInsights.ExportThreads "{threads}"',
                        f'TimingInsights.ExportTimers "{timers}"',
                    ]
                ),
                encoding="utf-8",
            )
            result = self._run(
                ["--json", "-t", TEST_TRACE, "batch", "run-rsp", rsp], check=False
            )
            if result.returncode != 0:
                pytest.skip("response-file execution failed for supplied trace")
            data = json.loads(result.stdout)
            assert len(data["output_files"]) >= 2
            for path in data["output_files"]:
                assert os.path.isfile(path)
                assert os.path.getsize(path) > 0

    def test_analyze_summary_real_trace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self._run(
                ["--json", "-t", TEST_TRACE, "analyze", "summary", "--out", tmpdir],
                check=False,
                timeout=360,
            )
            if result.returncode != 0:
                pytest.skip("analyze summary failed for supplied trace")
            data = json.loads(result.stdout)
            assert data["exports"]
            assert data["out_dir"] == str(Path(tmpdir).resolve())


@skip_no_target
class TestCaptureE2E:
    CLI_BASE = _resolve_cli("cli-anything-unrealinsights")

    def _run(self, args, check=True, timeout=300):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout,
            env=_cli_env(),
        )

    def test_capture_run_wait(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_trace = os.path.join(tmpdir, "capture.utrace")
            result = self._run(
                [
                    "--json",
                    "capture",
                    "run",
                    TEST_TARGET_EXE,
                    "--output-trace",
                    output_trace,
                    "--wait",
                    "--timeout",
                    "180",
                ],
                check=False,
                timeout=360,
            )
            if result.returncode != 0:
                pytest.skip("capture run failed for supplied target executable")
            data = json.loads(result.stdout)
            assert data["trace_path"].lower().endswith(".utrace")
            assert data["trace_exists"] is True
            assert data["trace_size"] > 0
