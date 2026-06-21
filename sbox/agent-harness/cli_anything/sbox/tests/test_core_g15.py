# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCodegenClass:
    """Tests for generate_class."""

    def test_generate_static_class(self):
        result = generate_class(
            "GameUtils",
            is_static=True,
            properties=[
                {"name": "Version", "type": "string", "default": '"1.0"'},
            ],
        )
        assert result["filename"] == "GameUtils.cs"
        assert "public static class GameUtils" in result["content"]
        assert "public static string Version" in result["content"]
        assert "\r\n" in result["content"]

    def test_generate_class_with_base(self):
        result = generate_class("EnemyManager", base_class="BaseManager")
        assert "public class EnemyManager : BaseManager" in result["content"]
        assert "using Sandbox;" in result["content"]

    def test_generate_class_method_with_multiline_body(self):
        """Method body containing newlines must be split into separate output lines.

        Regression test for a bug where the body was split on the literal
        two-character string ``\\n`` instead of an actual newline, collapsing
        every multi-line method body into a single line of malformed C#.
        """
        result = generate_class(
            "Counter",
            methods=[
                {
                    "name": "Tick",
                    "return_type": "void",
                    "body": "var x = 1;\nvar y = 2;\nreturn;",
                }
            ],
        )
        content = result["content"]
        assert "\t\tvar x = 1;" in content
        assert "\t\tvar y = 2;" in content
        assert "\t\treturn;" in content
        # The literal two-character sequence \n must NOT appear as a body
        # line - that would mean the buggy split was still in effect.
        assert "\t\tvar x = 1;\\nvar y = 2;" not in content


class TestLocalizationBulkSet:
    """Test bulk_set for localization."""

    def test_bulk_set(self, tmp_path):
        path = str(tmp_path / "en.json")
        create_translation_file(
            lang="en", initial_keys={"existing": "value"}, output_path=path
        )
        result = bulk_set(
            path, {"game.title": "My Game", "game.desc": "A game", "ui.start": "Start"}
        )
        assert len(result) == 4
        assert result["game.title"] == "My Game"
        assert result["existing"] == "value"
        keys = list_keys(path)
        assert "game.title" in keys
        assert "ui.start" in keys
