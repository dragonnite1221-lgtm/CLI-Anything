# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestQueryTask:
    @patch("cli_anything.anygen.utils.anygen_backend.requests.get")
    def test_query_returns_dict(self, mock_get):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"status": "running", "progress": 42}
        mock_get.return_value = resp
        from cli_anything.anygen.utils.anygen_backend import query_task

        result = query_task("sk-test", "task_001")
        assert result["status"] == "running"
        assert result["progress"] == 42

    @patch("cli_anything.anygen.utils.anygen_backend.requests.get")
    def test_query_completed_with_output(self, mock_get):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "status": "completed",
            "progress": 100,
            "output": {
                "file_url": "https://dl.example.com/f.pptx",
                "file_name": "f.pptx",
            },
        }
        mock_get.return_value = resp
        from cli_anything.anygen.utils.anygen_backend import query_task

        result = query_task("sk-test", "task_001")
        assert result["output"]["file_name"] == "f.pptx"

    @patch("cli_anything.anygen.utils.anygen_backend.requests.get")
    def test_query_http_error(self, mock_get):
        resp = MagicMock()
        resp.status_code = 404
        resp.text = "Not found"
        mock_get.return_value = resp
        from cli_anything.anygen.utils.anygen_backend import query_task

        with pytest.raises(RuntimeError, match="HTTP 404"):
            query_task("sk-test", "task_bad")


class TestPollTask:
    @patch("cli_anything.anygen.utils.anygen_backend.time.sleep")
    @patch("cli_anything.anygen.utils.anygen_backend.query_task")
    def test_poll_until_completed(self, mock_query, mock_sleep):
        mock_query.side_effect = [
            {"status": "running", "progress": 30},
            {"status": "running", "progress": 70},
            {"status": "completed", "progress": 100, "output": {}},
        ]
        from cli_anything.anygen.utils.anygen_backend import poll_task

        result = poll_task("sk-test", "task_001")
        assert result["status"] == "completed"
        assert mock_sleep.call_count == 2

    @patch("cli_anything.anygen.utils.anygen_backend.time.sleep")
    @patch("cli_anything.anygen.utils.anygen_backend.query_task")
    def test_poll_failed_raises(self, mock_query, mock_sleep):
        mock_query.return_value = {"status": "failed", "error": "server error"}
        from cli_anything.anygen.utils.anygen_backend import poll_task

        with pytest.raises(RuntimeError, match="failed"):
            poll_task("sk-test", "task_001")

    @patch("cli_anything.anygen.utils.anygen_backend.time.time")
    @patch("cli_anything.anygen.utils.anygen_backend.time.sleep")
    @patch("cli_anything.anygen.utils.anygen_backend.query_task")
    def test_poll_timeout(self, mock_query, mock_sleep, mock_time):
        mock_time.side_effect = [0, 0, 9999]
        mock_query.return_value = {"status": "running", "progress": 10}
        from cli_anything.anygen.utils.anygen_backend import poll_task

        with pytest.raises(TimeoutError, match="timeout"):
            poll_task("sk-test", "task_001", max_time=5)

    @patch("cli_anything.anygen.utils.anygen_backend.time.sleep")
    @patch("cli_anything.anygen.utils.anygen_backend.query_task")
    def test_poll_progress_callback(self, mock_query, mock_sleep):
        mock_query.side_effect = [
            {"status": "running", "progress": 50},
            {"status": "completed", "progress": 100, "output": {}},
        ]
        cb = MagicMock()
        from cli_anything.anygen.utils.anygen_backend import poll_task

        poll_task("sk-test", "task_001", on_progress=cb)
        assert cb.call_count == 2
        cb.assert_any_call("running", 50)
        cb.assert_any_call("completed", 100)
