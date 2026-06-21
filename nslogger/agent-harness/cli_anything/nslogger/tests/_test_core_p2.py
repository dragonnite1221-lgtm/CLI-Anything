# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import make_msg  # noqa: F401,E501


class TestExporter:
    def _msgs(self):
        return [
            make_msg(sequence=1, level=0, tag="A", text="first message"),
            make_msg(sequence=2, level=2, tag="B", text="second message"),
        ]

    def test_export_text(self):
        out = export_text(self._msgs())
        assert "first message" in out
        assert "second message" in out

    def test_export_json_valid(self):
        out = export_json(self._msgs())
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["sequence"] == 1

    def test_export_json_has_all_fields(self):
        out = export_json(self._msgs())
        data = json.loads(out)
        for key in ("sequence", "timestamp", "level", "level_name", "tag", "text", "type"):
            assert key in data[0]

    def test_export_csv_has_header(self):
        out = export_csv(self._msgs())
        assert "sequence" in out.splitlines()[0]

    def test_export_csv_has_data(self):
        out = export_csv(self._msgs())
        lines = out.strip().splitlines()
        assert len(lines) == 3  # header + 2 rows

    def test_export_messages_text(self):
        out = export_messages(iter(self._msgs()), fmt="text")
        assert "first message" in out

    def test_export_messages_json(self):
        out = export_messages(iter(self._msgs()), fmt="json")
        json.loads(out)  # must be valid JSON

    def test_export_messages_csv(self):
        out = export_messages(iter(self._msgs()), fmt="csv")
        assert "," in out


class TestWireProtocol:
    def _encode_and_parse(self, **kwargs):
        raw_file_bytes = encode_message(sequence=1, **kwargs)
        # raw_file_bytes = [4-byte length][body]
        body = raw_file_bytes[4:]
        return _parse_message(body)

    def test_round_trip_text(self):
        msg = self._encode_and_parse(text="hello", level=2, tag="TAG", thread_id="main")
        assert msg.text == "hello"
        assert msg.level == 2
        assert msg.tag == "TAG"
        assert msg.thread_id == "main"
        assert msg.sequence == 1

    def test_round_trip_timestamp(self):
        ts = 1700000000.5
        msg = self._encode_and_parse(timestamp=ts, text="x")
        assert msg.timestamp is not None
        assert abs(msg.timestamp.timestamp() - int(ts)) < 1

    def test_round_trip_client_info(self):
        msg = self._encode_and_parse(
            msg_type=3,
            client_name="TestApp",
            client_version="2.0",
            os_name="iOS",
            os_version="17.0",
            machine="iPhone15,2",
        )
        assert msg.client_name == "TestApp"
        assert msg.os_name == "iOS"

    def test_encode_message_has_length_prefix(self):
        raw = encode_message(sequence=0, text="x")
        declared_len = struct.unpack(">I", raw[:4])[0]
        assert declared_len == len(raw) - 4

    def test_official_integer_parts_do_not_have_length_fields(self):
        body = encode_message(sequence=7, text="official", level=1)[4:]
        msg = _parse_message(body)
        assert msg.sequence == 7
        assert msg.level == 1
        assert msg.text == "official"

    def test_legacy_lengthful_integer_parts_still_parse(self):
        parts = b""
        parts += bytes([0, 3]) + struct.pack(">I", 4) + struct.pack(">I", 0)
        parts += bytes([10, 3]) + struct.pack(">I", 4) + struct.pack(">I", 8)
        text = b"legacy"
        parts += bytes([7, 0]) + struct.pack(">I", len(text)) + text
        body = struct.pack(">H", 3) + parts
        msg = _parse_message(body)
        assert msg.sequence == 8
        assert msg.text == "legacy"
