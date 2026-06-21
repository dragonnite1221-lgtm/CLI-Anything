# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class PlainTextExtractionTests(unittest.TestCase):
    def test_none_returns_empty(self):
        self.assertEqual(extract_plain_text(None), "")

    def test_dict_with_text_key(self):
        self.assertEqual(extract_plain_text({"text": "<b>hello</b>"}), "hello")

    def test_dict_without_text_key(self):
        self.assertEqual(extract_plain_text({"foo": "bar"}), "")

    def test_nested_segment_list(self):
        segments = [{"type": 1, "text": "A"}, {"type": 1, "text": "B"}]
        self.assertEqual(extract_plain_text(segments), "AB")

    def test_html_entity_unescaping(self):
        self.assertEqual(extract_plain_text("<span>a&amp;b</span>"), "a&b")

    def test_zero_width_chars_removed(self):
        self.assertEqual(extract_plain_text("<span>\u200bhello\u200b</span>"), "hello")


class HtmlConversionTests(unittest.TestCase):
    def test_plain_text_to_html_wraps_in_span(self):
        result = plain_text_to_html("hello world")
        self.assertIn("<span>hello world</span>", result)

    def test_maybe_plain_text_to_html_always_wraps(self):
        # maybe_plain_text_to_html wraps any input (including existing html) in a span
        result = maybe_plain_text_to_html("plain text")
        self.assertIn("<span>", result)
        self.assertIn("plain text", result)

    def test_rich_text_to_html_handles_segment_list(self):
        segments = [{"type": 1, "text": "hello"}, {"type": 1, "text": " world"}]
        result = rich_text_to_html(segments)
        self.assertIn("hello", result)
        self.assertIn("world", result)


class NodeIdGenerationTests(unittest.TestCase):
    def test_generates_string_of_expected_length(self):
        node_id = generate_node_id()
        self.assertIsInstance(node_id, str)
        self.assertEqual(len(node_id), 10)

    def test_generates_unique_ids(self):
        ids = {generate_node_id() for _ in range(100)}
        self.assertEqual(len(ids), 100)


class NodePathConversionTests(unittest.TestCase):
    def test_single_level_path(self):
        self.assertEqual(node_path_to_api_path(("nodes", 0)), ["nodes", 0])

    def test_multi_level_path_inserts_children(self):
        self.assertEqual(
            node_path_to_api_path(("nodes", 1, 2, 3)),
            ["nodes", 1, "children", 2, "children", 3],
        )


class NodeIterationTests(unittest.TestCase):
    def test_iter_nodes_yields_all_nodes_depth_first(self):
        data = {
            "nodes": [
                {
                    "id": "a",
                    "text": "<span>A</span>",
                    "children": [
                        {"id": "b", "text": "<span>B</span>", "children": []},
                    ],
                },
                {"id": "c", "text": "<span>C</span>", "children": []},
            ]
        }
        ids = [node["id"] for _, node in iter_nodes(data["nodes"])]
        self.assertEqual(ids, ["a", "b", "c"])

    def test_iter_nodes_provides_correct_paths(self):
        data = {
            "nodes": [
                {
                    "id": "a",
                    "children": [
                        {"id": "b", "children": []},
                    ],
                },
            ]
        }
        paths = [("nodes", *path) for path, _ in iter_nodes(data["nodes"])]
        self.assertEqual(paths, [("nodes", 0), ("nodes", 0, 0)])


class ResolveNodeAtPathTests(unittest.TestCase):
    def test_resolves_root_node(self):
        data = {"nodes": [{"id": "root", "children": []}]}
        node = resolve_node_at_path(data, ("nodes", 0))
        self.assertEqual(node["id"], "root")

    def test_resolves_nested_child(self):
        data = {
            "nodes": [
                {
                    "id": "root",
                    "children": [
                        {"id": "child", "children": []},
                    ],
                }
            ]
        }
        node = resolve_node_at_path(data, ("nodes", 0, 0))
        self.assertEqual(node["id"], "child")


class SerializeNodeTests(unittest.TestCase):
    def test_serialize_node_flattens_text(self):
        node = {
            "id": "n1",
            "text": "<span>hello</span>",
            "note": "<span>note</span>",
            "modified": 100,
            "children": [],
        }
        result = serialize_node(node, depth=0)
        self.assertEqual(result["id"], "n1")
        self.assertEqual(result["text"], "hello")
        self.assertEqual(result["note"], "note")
        self.assertEqual(result["modified"], 100)
        self.assertEqual(result["children"], [])
