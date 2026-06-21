# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBuildContentsParam:
    def test_none_mode_returns_none(self):
        assert build_contents_param("none") is None

    def test_highlights_mode(self):
        result = build_contents_param("highlights")
        assert "highlights" in result
        assert result["highlights"]["max_characters"] == 4_000

    def test_text_mode(self):
        result = build_contents_param("text")
        assert "text" in result
        assert result["text"]["max_characters"] == 10_000

    def test_summary_mode(self):
        result = build_contents_param("summary")
        assert result["summary"] is True

    def test_freshness_always(self):
        result = build_contents_param("highlights", freshness="always")
        assert result["max_age_hours"] == 0

    def test_freshness_never(self):
        result = build_contents_param("highlights", freshness="never")
        assert result["max_age_hours"] == -1

    def test_freshness_smart_omits_key(self):
        result = build_contents_param("highlights", freshness="smart")
        assert "max_age_hours" not in result


class TestCategorySlugMap:
    def test_hyphenated_slugs_map_to_api_values(self):
        assert CATEGORY_SLUG_MAP["research-paper"] == "research paper"
        assert CATEGORY_SLUG_MAP["personal-site"] == "personal site"
        assert CATEGORY_SLUG_MAP["financial-report"] == "financial report"

    def test_simple_slugs_pass_through(self):
        assert CATEGORY_SLUG_MAP["news"] == "news"
        assert CATEGORY_SLUG_MAP["company"] == "company"


class TestCLIHelp:
    def test_root_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Exa" in result.output

    def test_search_help(self, runner):
        result = runner.invoke(cli, ["search", "--help"])
        assert result.exit_code == 0
        assert "--type" in result.output
        assert "--num-results" in result.output
        assert "--content" in result.output

    def test_contents_help(self, runner):
        result = runner.invoke(cli, ["contents", "--help"])
        assert result.exit_code == 0

    def test_server_status_help(self, runner):
        result = runner.invoke(cli, ["server", "status", "--help"])
        assert result.exit_code == 0
