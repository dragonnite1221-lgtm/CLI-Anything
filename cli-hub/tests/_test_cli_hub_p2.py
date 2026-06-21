# ruff: noqa: F403, F405, E501
from ._test_cli_hub_base import *  # noqa: F403


class TestRegistry:
    """Tests for registry.py — fetch, cache, search, and lookup."""

    @patch("cli_hub.registry.requests.get")
    @patch("cli_hub.registry.CACHE_FILE", Path(tempfile.mktemp()))
    def test_fetch_registry_from_remote(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = SAMPLE_REGISTRY
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = fetch_registry(force_refresh=True)
        assert result["clis"][0]["name"] == "gimp"
        mock_get.assert_called_once()

    @patch("cli_hub.registry.requests.get", side_effect=requests.ConnectionError("network down"))
    def test_fetch_registry_uses_cache_on_refresh_failure(self, mock_get, tmp_path):
        cache_file = tmp_path / "registry_cache.json"
        cache_payload = {"_cached_at": 0, "data": SAMPLE_REGISTRY}
        cache_file.write_text(json.dumps(cache_payload, indent=2))

        with patch("cli_hub.registry.CACHE_FILE", cache_file):
            result = fetch_registry(force_refresh=True)

        assert result["clis"][0]["name"] == "gimp"
        mock_get.assert_called_once()

    @patch("cli_hub.registry.fetch_public_registry", return_value=None)
    @patch("cli_hub.registry.fetch_registry")
    def test_fetch_all_clis_does_not_mutate_registry_entries(self, mock_fetch_registry, mock_fetch_public):
        registry = {
            "meta": SAMPLE_REGISTRY["meta"],
            "clis": [dict(SAMPLE_REGISTRY["clis"][0])],
        }
        mock_fetch_registry.return_value = registry

        result = fetch_all_clis()

        assert result[0]["_source"] == "harness"
        assert "_source" not in registry["clis"][0]

    @patch("cli_hub.registry.fetch_all_clis", return_value=SAMPLE_REGISTRY["clis"])
    def test_get_cli_found(self, mock_fetch):
        cli = get_cli("gimp")
        assert cli is not None
        assert cli["display_name"] == "GIMP"

    @patch("cli_hub.registry.fetch_all_clis", return_value=SAMPLE_REGISTRY["clis"])
    def test_get_cli_case_insensitive(self, mock_fetch):
        cli = get_cli("GIMP")
        assert cli is not None
        assert cli["name"] == "gimp"

    @patch("cli_hub.registry.fetch_all_clis", return_value=SAMPLE_REGISTRY["clis"])
    def test_get_cli_not_found(self, mock_fetch):
        cli = get_cli("nonexistent")
        assert cli is None

    @patch("cli_hub.registry.fetch_all_clis", return_value=SAMPLE_REGISTRY["clis"])
    def test_search_by_name(self, mock_fetch):
        results = search_clis("gimp")
        assert len(results) == 1
        assert results[0]["name"] == "gimp"

    @patch("cli_hub.registry.fetch_all_clis", return_value=SAMPLE_REGISTRY["clis"])
    def test_search_by_category(self, mock_fetch):
        results = search_clis("3d")
        assert len(results) == 1
        assert results[0]["name"] == "blender"

    @patch("cli_hub.registry.fetch_all_clis", return_value=SAMPLE_REGISTRY["clis"])
    def test_search_by_description(self, mock_fetch):
        results = search_clis("audio")
        assert len(results) == 1
        assert results[0]["name"] == "audacity"

    @patch("cli_hub.registry.fetch_all_clis", return_value=SAMPLE_REGISTRY["clis"])
    def test_search_no_results(self, mock_fetch):
        results = search_clis("nonexistent_xyz")
        assert len(results) == 0

    @patch("cli_hub.registry.fetch_all_clis", return_value=SAMPLE_REGISTRY["clis"])
    def test_list_categories(self, mock_fetch):
        cats = list_categories()
        assert cats == ["3d", "audio", "image"]
