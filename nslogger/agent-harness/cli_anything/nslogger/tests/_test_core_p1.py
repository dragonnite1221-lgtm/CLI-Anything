# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import make_msg  # noqa: F401,E501


class TestFilterMessages:
    def _msgs(self):
        return [
            make_msg(sequence=1, level=0, tag="Auth", thread_id="main", text="error occurred"),
            make_msg(sequence=2, level=2, tag="Network", thread_id="bg", text="request sent"),
            make_msg(sequence=3, level=3, tag="Auth", thread_id="main", text="token refreshed"),
            make_msg(sequence=4, level=4, tag="UI", thread_id="main", text="view loaded"),
        ]

    def test_no_filter_passes_all(self):
        result = list(filter_messages(iter(self._msgs())))
        assert len(result) == 4

    def test_max_level(self):
        result = list(filter_messages(iter(self._msgs()), max_level=1))
        assert all(m.level <= 1 for m in result)
        assert len(result) == 1

    def test_min_level(self):
        result = list(filter_messages(iter(self._msgs()), min_level=3))
        assert all(m.level >= 3 for m in result)
        assert len(result) == 2

    def test_tag_filter(self):
        result = list(filter_messages(iter(self._msgs()), tags=["auth"]))
        assert all(m.tag == "Auth" for m in result)
        assert len(result) == 2

    def test_tag_case_insensitive(self):
        result = list(filter_messages(iter(self._msgs()), tags=["AUTH"]))
        assert len(result) == 2

    def test_thread_filter(self):
        result = list(filter_messages(iter(self._msgs()), thread_id="bg"))
        assert len(result) == 1
        assert result[0].sequence == 2

    def test_text_search(self):
        result = list(filter_messages(iter(self._msgs()), text_search="token"))
        assert len(result) == 1
        assert "token" in result[0].text.lower()

    def test_text_search_case_insensitive(self):
        result = list(filter_messages(iter(self._msgs()), text_search="ERROR"))
        assert len(result) == 1

    def test_regex_filter(self):
        result = list(filter_messages(iter(self._msgs()), text_regex=r"re(quest|freshed)"))
        assert len(result) == 2

    def test_limit(self):
        result = list(filter_messages(iter(self._msgs()), limit=2))
        assert len(result) == 2

    def test_combined_filters(self):
        result = list(filter_messages(iter(self._msgs()), max_level=2, tags=["auth"]))
        assert len(result) == 1
        assert result[0].level == 0

    def test_empty_input(self):
        result = list(filter_messages(iter([])))
        assert result == []


class TestComputeStats:
    def _msgs(self):
        return [
            make_msg(level=0, tag="Auth", thread_id="main",
                     timestamp=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)),
            make_msg(level=2, tag="Network", thread_id="bg",
                     timestamp=datetime(2024, 1, 1, 10, 1, tzinfo=timezone.utc)),
            make_msg(level=2, tag="Auth", thread_id="main",
                     timestamp=datetime(2024, 1, 1, 10, 2, tzinfo=timezone.utc)),
        ]

    def test_total(self):
        s = compute_stats(iter(self._msgs()))
        assert s["total"] == 3

    def test_by_level(self):
        s = compute_stats(iter(self._msgs()))
        assert s["by_level"]["ERROR"] == 1
        assert s["by_level"]["INFO"] == 2

    def test_by_tag(self):
        s = compute_stats(iter(self._msgs()))
        assert s["by_tag"]["Auth"] == 2
        assert s["by_tag"]["Network"] == 1

    def test_by_thread(self):
        s = compute_stats(iter(self._msgs()))
        assert s["by_thread"]["main"] == 2

    def test_duration(self):
        s = compute_stats(iter(self._msgs()))
        assert s["duration_seconds"] == 120.0

    def test_timestamps(self):
        s = compute_stats(iter(self._msgs()))
        assert "2024-01-01T10:00:00" in s["first_timestamp"]
        assert "2024-01-01T10:02:00" in s["last_timestamp"]

    def test_empty(self):
        s = compute_stats(iter([]))
        assert s["total"] == 0

    def test_by_type(self):
        s = compute_stats(iter(self._msgs()))
        assert "text" in s["by_type"]
