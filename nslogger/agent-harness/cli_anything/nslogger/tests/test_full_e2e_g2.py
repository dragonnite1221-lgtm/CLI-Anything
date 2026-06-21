# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestBlocksCommand:
    def test_blocks_text_output(self, sample_file):
        result = run_cli("blocks", sample_file)
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0

    def test_blocks_json_output(self, sample_file):
        result = run_cli("blocks", sample_file, "--json")
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        for entry in data:
            assert "depth" in entry
            assert "sequence" in entry

    def test_blocks_indent_applied(self, tmp_path):
        from cli_anything.nslogger.utils.generate import encode_message
        from cli_anything.nslogger.core.message import (
            MSG_TYPE_BLOCK_START,
            MSG_TYPE_BLOCK_END,
        )

        path = str(tmp_path / "blk.rawnsloggerdata")
        with open(path, "wb") as f:
            f.write(encode_message(sequence=0, text="before"))
            f.write(
                encode_message(sequence=1, msg_type=MSG_TYPE_BLOCK_START, text="enter")
            )
            f.write(encode_message(sequence=2, text="inside"))
            f.write(
                encode_message(sequence=3, msg_type=MSG_TYPE_BLOCK_END, text="exit")
            )
        result = run_cli("blocks", path, "--indent", "4")
        lines = result.stdout.splitlines()
        # "inside" should be indented (4 spaces)
        inside_lines = [l for l in lines if "inside" in l]
        assert inside_lines and inside_lines[0].startswith("    ")


class TestMergeCommand:
    def test_merge_two_files(self, tmp_path):
        a = str(tmp_path / "a.rawnsloggerdata")
        b = str(tmp_path / "b.rawnsloggerdata")
        run_cli("generate", a, "--count", "5")
        run_cli("generate", b, "--count", "5")
        result = run_cli("merge", a, b, "--format", "json")
        data = json.loads(result.stdout)
        assert len(data) >= 10

    def test_merge_to_file(self, tmp_path):
        a = str(tmp_path / "c.rawnsloggerdata")
        b = str(tmp_path / "d.rawnsloggerdata")
        out = str(tmp_path / "merged.json")
        run_cli("generate", a, "--count", "5")
        run_cli("generate", b, "--count", "5")
        run_cli("merge", a, b, "--format", "json", "--output", out)
        assert os.path.exists(out)
        with open(out) as f:
            data = json.load(f)
        assert len(data) >= 10

    def test_merge_csv_format(self, tmp_path):
        a = str(tmp_path / "e.rawnsloggerdata")
        run_cli("generate", a, "--count", "5")
        result = run_cli("merge", a, "--format", "csv")
        assert "sequence" in result.stdout.splitlines()[0]


class TestFilterExtendedOptions:
    def test_filter_from_seq(self, tmp_path):
        out = str(tmp_path / "seqtest.rawnsloggerdata")
        run_cli("generate", out, "--count", "10")
        all_data = json.loads(run_cli("read", out, "--json").stdout)
        mid_seq = all_data[5]["sequence"]
        result = run_cli("filter", out, "--from-seq", str(mid_seq), "--json")
        data = json.loads(result.stdout)
        assert all(m["sequence"] >= mid_seq for m in data)

    def test_filter_to_seq(self, tmp_path):
        out = str(tmp_path / "seqtest2.rawnsloggerdata")
        run_cli("generate", out, "--count", "10")
        all_data = json.loads(run_cli("read", out, "--json").stdout)
        mid_seq = all_data[5]["sequence"]
        result = run_cli("filter", out, "--to-seq", str(mid_seq), "--json")
        data = json.loads(result.stdout)
        assert all(m["sequence"] <= mid_seq for m in data)
