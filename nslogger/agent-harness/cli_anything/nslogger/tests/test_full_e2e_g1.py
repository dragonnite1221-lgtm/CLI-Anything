# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestWorkflow:
    def test_generate_filter_export_pipeline(self, tmp_path):
        """Generate → filter errors → export JSON."""
        log_file = str(tmp_path / "app.rawnsloggerdata")
        generate_sample_file(log_file, count=50)

        msgs = list(parse_raw_file(log_file))
        assert len(msgs) > 0

        errors = list(filter_messages(iter(msgs), max_level=0))
        assert isinstance(errors, list)

        out = export_messages(iter(errors), fmt="json")
        data = json.loads(out)
        for m in data:
            assert m["level"] <= 0

    def test_stats_on_generated_file(self, tmp_path):
        log_file = str(tmp_path / "app.rawnsloggerdata")
        generate_sample_file(log_file, count=40)
        msgs = list(parse_raw_file(log_file))
        s = compute_stats(iter(msgs))
        assert s["total"] >= 40
        assert "by_level" in s
        assert "by_tag" in s

    def test_cli_help_shows_commands(self):
        result = run_cli("--help")
        for cmd in ("read", "filter", "export", "stats", "listen", "generate"):
            assert cmd in result.stdout


class TestCLISubprocess:
    def test_installed_cli_help(self):
        cmd = _resolve_cli("cli-anything-nslogger") + ["--help"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        assert "NSLogger" in result.stdout

    def test_installed_generate_and_read(self, tmp_path):
        out = str(tmp_path / "sub.rawnsloggerdata")
        run_cli("generate", out, "--count", "5")
        result = run_cli("read", out, "--json")
        data = json.loads(result.stdout)
        assert len(data) >= 5

    def test_installed_stats_json(self, tmp_path):
        out = str(tmp_path / "sub2.rawnsloggerdata")
        run_cli("generate", out, "--count", "8")
        result = run_cli("stats", out, "--json")
        data = json.loads(result.stdout)
        assert data["total"] >= 8

    def test_installed_export_csv(self, tmp_path):
        out = str(tmp_path / "sub3.rawnsloggerdata")
        run_cli("generate", out, "--count", "5")
        result = run_cli("export", out, "--format", "csv")
        assert "sequence" in result.stdout.splitlines()[0]


class TestTailCommand:
    def test_tail_returns_last_n(self, tmp_path):
        out = str(tmp_path / "tail.rawnsloggerdata")
        run_cli("generate", out, "--count", "20")
        result_all = run_cli("read", out, "--json")
        result_tail = run_cli("tail", out, "--count", "5", "--json")
        all_msgs = json.loads(result_all.stdout)
        tail_msgs = json.loads(result_tail.stdout)
        assert len(tail_msgs) == 5
        # Last 5 of all should match tail
        assert [m["sequence"] for m in tail_msgs] == [
            m["sequence"] for m in all_msgs[-5:]
        ]

    def test_tail_default_count(self, tmp_path):
        out = str(tmp_path / "tail2.rawnsloggerdata")
        run_cli("generate", out, "--count", "30")
        result = run_cli("tail", out, "--json")
        data = json.loads(result.stdout)
        assert len(data) == 20  # default is 20

    def test_tail_text_output(self, tmp_path):
        out = str(tmp_path / "tail3.rawnsloggerdata")
        run_cli("generate", out, "--count", "5")
        result = run_cli("tail", out)
        assert len(result.stdout.strip().splitlines()) > 0


class TestClientsCommand:
    def test_clients_json_output(self, sample_file):
        result = run_cli("clients", sample_file, "--json")
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        # sample file should have at least one client_info
        if data:
            assert "client_name" in data[0]

    def test_clients_text_output(self, sample_file):
        result = run_cli("clients", sample_file)
        assert result.returncode == 0  # may output "No client_info" or real clients

    def test_clients_empty_file(self, tmp_path):
        # File with only plain log messages, no client_info
        from cli_anything.nslogger.utils.generate import encode_message

        path = str(tmp_path / "no_clients.rawnsloggerdata")
        with open(path, "wb") as f:
            f.write(encode_message(sequence=0, text="plain log"))
        result = run_cli("clients", path)
        assert result.returncode == 0
        assert "No client_info" in result.stdout
