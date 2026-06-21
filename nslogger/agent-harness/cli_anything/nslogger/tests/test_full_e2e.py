# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestGenerateCommand:
    def test_generate_creates_file(self, tmp_path):
        out = str(tmp_path / "gen.rawnsloggerdata")
        result = run_cli("generate", out, "--count", "10")
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_generate_output_mentions_count(self, tmp_path):
        out = str(tmp_path / "gen.rawnsloggerdata")
        result = run_cli("generate", out, "--count", "10")
        assert "10" in result.stdout

    def test_generate_parseable(self, tmp_path):
        out = str(tmp_path / "gen.rawnsloggerdata")
        run_cli("generate", out, "--count", "15")
        msgs = list(parse_raw_file(out))
        assert len(msgs) >= 15


class TestReadCommand:
    def test_read_outputs_messages(self, sample_file):
        result = run_cli("read", sample_file)
        lines = [l for l in result.stdout.strip().splitlines() if l]
        assert len(lines) > 0

    def test_read_json_valid(self, sample_file):
        result = run_cli("read", sample_file, "--json")
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_read_json_message_shape(self, sample_file):
        result = run_cli("read", sample_file, "--json")
        data = json.loads(result.stdout)
        msg = data[0]
        for key in ("sequence", "level", "level_name", "type", "text"):
            assert key in msg

    def test_read_level_filter(self, sample_file):
        result = run_cli("read", sample_file, "--level", "0", "--json")
        data = json.loads(result.stdout)
        assert all(m["level"] <= 0 for m in data)

    def test_read_limit(self, sample_file):
        result = run_cli("read", sample_file, "--limit", "5", "--json")
        data = json.loads(result.stdout)
        assert len(data) <= 5

    def test_read_search(self, sample_file):
        result = run_cli("read", sample_file, "--search", "error", "--json")
        data = json.loads(result.stdout)
        for m in data:
            assert "error" in m["text"].lower() or m["level"] == 0


class TestFilterCommand:
    def test_filter_by_level(self, sample_file):
        result = run_cli("filter", sample_file, "--level", "1", "--json")
        data = json.loads(result.stdout)
        assert all(m["level"] <= 1 for m in data)

    def test_filter_no_results(self, sample_file, tmp_path):
        # Generate file with no level-99 messages
        out = str(tmp_path / "g.rawnsloggerdata")
        generate_sample_file(out, count=5)
        result = run_cli("filter", out, "--search", "XYZZY_NEVER_MATCHES_ANYTHING")
        assert result.stdout.strip() == ""

    def test_filter_regex(self, sample_file):
        result = run_cli("filter", sample_file, "--regex", r"(error|failed)", "--json")
        data = json.loads(result.stdout)
        import re

        pattern = re.compile(r"(error|failed)", re.IGNORECASE)
        for m in data:
            assert pattern.search(m["text"]), f"No match in: {m['text']!r}"


class TestExportCommand:
    def test_export_text_stdout(self, sample_file):
        result = run_cli("export", sample_file, "--format", "text")
        assert len(result.stdout) > 0

    def test_export_json_stdout(self, sample_file):
        result = run_cli("export", sample_file, "--format", "json")
        data = json.loads(result.stdout)
        assert isinstance(data, list)

    def test_export_csv_stdout(self, sample_file):
        result = run_cli("export", sample_file, "--format", "csv")
        lines = result.stdout.strip().splitlines()
        assert "sequence" in lines[0]
        assert len(lines) > 1

    def test_export_to_file(self, sample_file, tmp_path):
        out = str(tmp_path / "export.json")
        run_cli("export", sample_file, "--format", "json", "--output", out)
        assert os.path.exists(out)
        with open(out) as f:
            data = json.load(f)
        assert isinstance(data, list)

    def test_export_with_level_filter(self, sample_file):
        result = run_cli("export", sample_file, "--format", "json", "--level", "1")
        data = json.loads(result.stdout)
        assert all(m["level"] <= 1 for m in data)


class TestStatsCommand:
    def test_stats_text_output(self, sample_file):
        result = run_cli("stats", sample_file)
        assert "Total" in result.stdout or "total" in result.stdout.lower()

    def test_stats_json_output(self, sample_file):
        result = run_cli("stats", sample_file, "--json")
        data = json.loads(result.stdout)
        assert "total" in data
        assert data["total"] > 0

    def test_stats_json_has_by_level(self, sample_file):
        result = run_cli("stats", sample_file, "--json")
        data = json.loads(result.stdout)
        assert "by_level" in data

    def test_stats_json_has_by_tag(self, sample_file):
        result = run_cli("stats", sample_file, "--json")
        data = json.loads(result.stdout)
        assert "by_tag" in data
