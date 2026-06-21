# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import make_msg  # noqa: F401,E501


class TestIterBlockTree:
    def _block_msgs(self):
        return [
            make_msg(sequence=1, message_type=MSG_TYPE_LOG, text="before block"),
            make_msg(sequence=2, message_type=MSG_TYPE_BLOCK_START, text="enter"),
            make_msg(sequence=3, message_type=MSG_TYPE_LOG, text="inside"),
            make_msg(sequence=4, message_type=MSG_TYPE_BLOCK_END, text="exit"),
            make_msg(sequence=5, message_type=MSG_TYPE_LOG, text="after block"),
        ]

    def test_top_level_messages_have_depth_zero(self):
        pairs = list(iter_block_tree(iter(self._block_msgs())))
        assert pairs[0][0] == 0   # before block
        assert pairs[4][0] == 0   # after block

    def test_block_start_at_zero_before_increment(self):
        pairs = list(iter_block_tree(iter(self._block_msgs())))
        # block_start emitted at depth 0, then depth increments
        assert pairs[1][0] == 0
        assert pairs[1][1].message_type == MSG_TYPE_BLOCK_START

    def test_inside_block_has_depth_one(self):
        pairs = list(iter_block_tree(iter(self._block_msgs())))
        assert pairs[2][0] == 1

    def test_block_end_has_depth_zero_after_decrement(self):
        pairs = list(iter_block_tree(iter(self._block_msgs())))
        # block_end decrements first, so emitted at depth 0
        assert pairs[3][0] == 0

    def test_empty_input(self):
        assert list(iter_block_tree(iter([]))) == []


class TestExtractClients:
    def _msgs_with_client(self):
        client = LogMessage(
            sequence=0,
            message_type=MSG_TYPE_CLIENT_INFO,
            client_name="MyApp",
            client_version="3.1",
            os_name="iOS",
            os_version="17.0",
            machine="iPhone16,1",
        )
        log = make_msg(sequence=1, text="regular log")
        return [client, log]

    def test_returns_only_client_info(self):
        result = extract_clients(iter(self._msgs_with_client()))
        assert len(result) == 1

    def test_client_fields(self):
        result = extract_clients(iter(self._msgs_with_client()))
        c = result[0]
        assert c["client_name"] == "MyApp"
        assert c["client_version"] == "3.1"
        assert c["os_name"] == "iOS"
        assert c["machine"] == "iPhone16,1"

    def test_no_clients_returns_empty(self):
        result = extract_clients(iter([make_msg(text="log")]))
        assert result == []


class TestMergeFiles:
    def _write(self, tmp_path, name, *messages_kwargs):
        path = str(tmp_path / name)
        with open(path, "wb") as f:
            for i, kw in enumerate(messages_kwargs):
                f.write(encode_message(sequence=i, **kw))
        return path

    def test_merge_two_files_sorted(self, tmp_path):
        ts_early = 1700000000.0
        ts_late = 1700000100.0
        path_a = self._write(tmp_path, "a.rawnsloggerdata",
                             {"text": "late msg", "timestamp": ts_late})
        path_b = self._write(tmp_path, "b.rawnsloggerdata",
                             {"text": "early msg", "timestamp": ts_early})
        result = merge_files([path_a, path_b])
        assert len(result) == 2
        assert result[0].text == "early msg"
        assert result[1].text == "late msg"

    def test_merge_single_file(self, tmp_path):
        path = self._write(tmp_path, "c.rawnsloggerdata",
                           {"text": "only msg"})
        result = merge_files([path])
        assert len(result) == 1

    def test_merge_preserves_all_messages(self, tmp_path):
        path_a = self._write(tmp_path, "d.rawnsloggerdata",
                             {"text": "a1"}, {"text": "a2"})
        path_b = self._write(tmp_path, "e.rawnsloggerdata",
                             {"text": "b1"}, {"text": "b2"})
        result = merge_files([path_a, path_b])
        assert len(result) == 4


class TestListenWaitingMessage:
    def test_non_bonjour_message(self):
        assert _listen_waiting_message(50000, False) == "Waiting for a client connection on port 50000…"

    def test_bonjour_message(self):
        assert _listen_waiting_message(50000, True) == "[Bonjour] Waiting for an iOS client to connect on port 50000…"
