# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


def make_msg(**kwargs) -> LogMessage:
    defaults = dict(
        sequence=0,
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        timestamp_ms=500,
        level=2,
        tag="Test",
        thread_id="main",
        text="hello world",
        message_type=MSG_TYPE_LOG,
    )
    defaults.update(kwargs)
    return LogMessage(**defaults)


class TestLogMessage:
    def test_level_name_known(self):
        msg = make_msg(level=0)
        assert msg.level_name == "ERROR"

    def test_level_name_unknown(self):
        msg = make_msg(level=99)
        assert "99" in msg.level_name

    def test_type_name_text(self):
        msg = make_msg(text="hello")
        assert msg.type_name == "text"

    def test_type_name_image(self):
        msg = make_msg(image_data=b"\xff\xd8\xff", image_width=100, image_height=200)
        assert msg.type_name == "image"

    def test_type_name_data(self):
        msg = make_msg(binary_data=b"\x00\x01")
        assert msg.type_name == "data"

    def test_type_name_client_info(self):
        msg = make_msg(message_type=MSG_TYPE_CLIENT_INFO)
        assert msg.type_name == "client_info"

    def test_to_dict_keys(self):
        msg = make_msg()
        d = msg.to_dict()
        assert "sequence" in d
        assert "timestamp" in d
        assert "level_name" in d
        assert "type" in d
        assert "text" in d

    def test_to_dict_timestamp_isoformat(self):
        msg = make_msg()
        d = msg.to_dict()
        assert "2024-01-01" in d["timestamp"]

    def test_to_text_line_contains_text(self):
        msg = make_msg(text="SAMPLE_TEXT")
        line = msg.to_text_line()
        assert "SAMPLE_TEXT" in line

    def test_to_text_line_contains_level(self):
        msg = make_msg(level=0)
        line = msg.to_text_line()
        assert "ERROR" in line

    def test_to_text_line_contains_tag(self):
        msg = make_msg(tag="NetworkOps")
        line = msg.to_text_line()
        assert "NetworkOps" in line

    def test_to_text_line_no_timestamp(self):
        msg = make_msg(timestamp=None)
        line = msg.to_text_line()
        assert "??" in line

    def test_to_text_line_image(self):
        msg = make_msg(image_data=b"x", image_width=320, image_height=240)
        line = msg.to_text_line()
        assert "image" in line
        assert "320" in line

    def test_to_text_line_binary(self):
        msg = make_msg(binary_data=b"\x00" * 10)
        line = msg.to_text_line()
        assert "10" in line
