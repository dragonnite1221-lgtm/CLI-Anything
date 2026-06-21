# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import make_msg  # noqa: F401,E501


class TestGenerateSampleFile:
    def test_creates_file(self, tmp_path):
        path = str(tmp_path / "sample.rawnsloggerdata")
        generate_sample_file(path, count=5)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_parseable(self, tmp_path):
        path = str(tmp_path / "sample.rawnsloggerdata")
        generate_sample_file(path, count=10)
        msgs = list(parse_raw_file(path))
        assert len(msgs) >= 10  # 10 log + 1 client_info

    def test_varied_levels(self, tmp_path):
        path = str(tmp_path / "sample.rawnsloggerdata")
        generate_sample_file(path, count=50)
        msgs = list(parse_raw_file(path))
        levels = {m.level for m in msgs}
        assert len(levels) > 1


class TestParseRawFile:
    def _write_file(self, tmp_path, *messages_kwargs):
        path = str(tmp_path / "test.rawnsloggerdata")
        with open(path, "wb") as f:
            for i, kw in enumerate(messages_kwargs):
                f.write(encode_message(sequence=i, **kw))
        return path

    def test_single_message(self, tmp_path):
        path = self._write_file(tmp_path, {"text": "only one"})
        msgs = list(parse_raw_file(path))
        assert len(msgs) == 1
        assert msgs[0].text == "only one"

    def test_multiple_messages(self, tmp_path):
        path = self._write_file(
            tmp_path,
            {"text": "first", "level": 0},
            {"text": "second", "level": 2},
            {"text": "third", "level": 4},
        )
        msgs = list(parse_raw_file(path))
        assert len(msgs) == 3
        assert msgs[0].text == "first"
        assert msgs[2].text == "third"

    def test_empty_file(self, tmp_path):
        path = str(tmp_path / "empty.rawnsloggerdata")
        open(path, "wb").close()
        msgs = list(parse_raw_file(path))
        assert msgs == []


class TestFilterMessagesExtended:
    def _msgs_with_timestamps(self):
        t = lambda h, m: datetime(2024, 1, 1, h, m, 0, tzinfo=timezone.utc)
        return [
            make_msg(sequence=10, timestamp=t(10, 0), level=0, text="early error"),
            make_msg(sequence=20, timestamp=t(10, 30), level=2, text="mid info"),
            make_msg(sequence=30, timestamp=t(11, 0), level=3, text="late debug"),
        ]

    def test_after_filter(self):
        after = datetime(2024, 1, 1, 10, 15, tzinfo=timezone.utc)
        result = list(filter_messages(iter(self._msgs_with_timestamps()), after=after))
        assert len(result) == 2
        assert result[0].sequence == 20

    def test_before_filter(self):
        before = datetime(2024, 1, 1, 10, 45, tzinfo=timezone.utc)
        result = list(filter_messages(iter(self._msgs_with_timestamps()), before=before))
        assert len(result) == 2
        assert result[-1].sequence == 20

    def test_after_and_before_window(self):
        after = datetime(2024, 1, 1, 10, 15, tzinfo=timezone.utc)
        before = datetime(2024, 1, 1, 10, 45, tzinfo=timezone.utc)
        result = list(filter_messages(iter(self._msgs_with_timestamps()), after=after, before=before))
        assert len(result) == 1
        assert result[0].sequence == 20

    def test_from_seq(self):
        result = list(filter_messages(iter(self._msgs_with_timestamps()), from_seq=20))
        assert len(result) == 2
        assert result[0].sequence == 20

    def test_to_seq(self):
        result = list(filter_messages(iter(self._msgs_with_timestamps()), to_seq=20))
        assert len(result) == 2
        assert result[-1].sequence == 20

    def test_seq_range(self):
        result = list(filter_messages(iter(self._msgs_with_timestamps()), from_seq=20, to_seq=20))
        assert len(result) == 1
        assert result[0].sequence == 20

    def test_no_timestamp_excluded_by_after(self):
        msgs = [make_msg(sequence=1, timestamp=None, text="no ts")]
        after = datetime(2024, 1, 1, tzinfo=timezone.utc)
        result = list(filter_messages(iter(msgs), after=after))
        assert result == []
