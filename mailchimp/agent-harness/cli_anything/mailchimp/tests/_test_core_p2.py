# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestPagination(unittest.TestCase):
    def _mock_client(self, pages: list[list]) -> MagicMock:
        client = MagicMock()
        side_effects = [
            {"lists": page, "total_items": sum(len(p) for p in pages)}
            for page in pages
        ]
        client.get.side_effect = side_effects
        return client

    def test_single_page(self):
        from cli_anything.mailchimp.core.pagination import paginate

        client = self._mock_client([[{"id": "1"}, {"id": "2"}]])
        items = list(paginate(client, "/lists", "lists", page_size=100))
        assert items == [{"id": "1"}, {"id": "2"}]
        assert client.get.call_count == 1

    def test_multiple_pages(self):
        from cli_anything.mailchimp.core.pagination import paginate

        page1 = [{"id": str(i)} for i in range(5)]
        page2 = [{"id": str(i)} for i in range(5, 8)]
        client = self._mock_client([page1, page2])
        items = list(paginate(client, "/lists", "lists", page_size=5))
        assert len(items) == 8
        assert client.get.call_count == 2

    def test_empty_result(self):
        from cli_anything.mailchimp.core.pagination import paginate

        client = self._mock_client([[]])
        items = list(paginate(client, "/lists", "lists"))
        assert items == []

    def test_exact_page_boundary_no_extra_fetch(self):
        """When total_items == page_size, paginator must not fetch a second empty page (I6 fix)."""
        from cli_anything.mailchimp.core.pagination import paginate

        page = [{"id": str(i)} for i in range(5)]
        client = MagicMock()
        # First call returns exactly page_size items with total_items matching
        client.get.return_value = {"lists": page, "total_items": 5}
        items = list(paginate(client, "/lists", "lists", page_size=5))
        assert len(items) == 5
        assert client.get.call_count == 1  # must not make a second call

    def test_collect_returns_total(self):
        from cli_anything.mailchimp.core.pagination import collect

        client = MagicMock()
        client.get.return_value = {"lists": [{"id": "1"}], "total_items": 42}
        items, total = collect(client, "/lists", "lists")
        assert items == [{"id": "1"}]
        assert total == 42


class TestOutput(unittest.TestCase):
    def setUp(self):
        import cli_anything.mailchimp.utils.output as out
        self._orig = out.USE_JSON
        out.USE_JSON = False

    def tearDown(self):
        import cli_anything.mailchimp.utils.output as out
        out.USE_JSON = self._orig

    def test_json_mode_outputs_json(self):
        import cli_anything.mailchimp.utils.output as out
        import io

        out.USE_JSON = True
        captured = io.StringIO()
        with patch("builtins.print", lambda *a, **kw: captured.write(str(a[0]) + "\n")):
            out._out({"key": "value"})

        parsed = json.loads(captured.getvalue())
        assert parsed["key"] == "value"
