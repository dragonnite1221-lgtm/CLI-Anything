# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestProject:
    """Tests for cli_anything.sbox.core.project."""

    def test_create_project(self, tmp_path):
        """Create a project and verify .sbproj, scene, configs are created."""
        info = create_project("MyGame", output_dir=str(tmp_path / "MyGame"))
        root = tmp_path / "MyGame"

        # Check returned info
        assert info["name"] == "MyGame"
        assert info["type"] == "game"
        assert info["max_players"] == 64
        assert info["tick_rate"] == 50

        # Check directory structure
        assert (root / "MyGame.sbproj").is_file()
        assert (root / ".editorconfig").is_file()
        assert (root / "Code" / "Assembly.cs").is_file()
        assert (root / "Editor" / "Assembly.cs").is_file()
        assert (root / "Assets" / "scenes" / "minimal.scene").is_file()
        assert (root / "ProjectSettings" / "Input.config").is_file()
        assert (root / "ProjectSettings" / "Collision.config").is_file()
        assert (root / "Libraries").is_dir()
        assert (root / "Localization").is_dir()

        # Verify .sbproj is valid JSON with StartupScene in Metadata
        with open(root / "MyGame.sbproj", "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["Title"] == "MyGame"
        assert data["Type"] == "game"
        assert "StartupScene" not in data, (
            "StartupScene should be in Metadata, not root"
        )
        assert data["Metadata"]["StartupScene"] == "scenes/minimal.scene"

        # Verify Input.config has all 31 actions including Slot0-Slot9
        with open(
            root / "ProjectSettings" / "Input.config", "r", encoding="utf-8"
        ) as f:
            input_data = json.load(f)
        action_names = [a["Name"] for a in input_data["Actions"]]
        assert len(action_names) == 31
        for slot in [
            "Slot0",
            "Slot1",
            "Slot2",
            "Slot3",
            "Slot4",
            "Slot5",
            "Slot6",
            "Slot7",
            "Slot8",
            "Slot9",
        ]:
            assert slot in action_names, f"Missing {slot} in Input.config"

    def test_create_project_custom_settings(self, tmp_path):
        """Create project with custom max_players, tick_rate, etc."""
        info = create_project(
            "CustomGame",
            output_dir=str(tmp_path / "CustomGame"),
            max_players=8,
            tick_rate=128,
            network_type="ServerOnly",
            org="myorg",
        )

        assert info["max_players"] == 8
        assert info["tick_rate"] == 128
        assert info["network_type"] == "ServerOnly"
        assert info["org"] == "myorg"

        # Verify persisted in JSON
        data = load_project(info["sbproj"])
        assert data["Metadata"]["MaxPlayers"] == 8
        assert data["Metadata"]["TickRate"] == 128
        assert data["Metadata"]["GameNetworkType"] == "ServerOnly"
        assert data["Org"] == "myorg"

    def test_load_save_project(self, tmp_path):
        """Load and re-save a project, verify round-trip."""
        info = create_project("RoundTrip", output_dir=str(tmp_path / "RoundTrip"))
        sbproj = info["sbproj"]

        data = load_project(sbproj)
        data["Title"] = "Modified"
        data["Metadata"]["MaxPlayers"] = 32
        save_project(sbproj, data)

        reloaded = load_project(sbproj)
        assert reloaded["Title"] == "Modified"
        assert reloaded["Metadata"]["MaxPlayers"] == 32

    def test_get_project_info(self, tmp_path):
        """Verify project info dict has all expected fields."""
        info = create_project("InfoTest", output_dir=str(tmp_path / "InfoTest"))
        proj_info = get_project_info(info["sbproj"])

        expected_keys = {
            "title",
            "type",
            "org",
            "ident",
            "startup_scene",
            "max_players",
            "min_players",
            "tick_rate",
            "network_type",
            "map_select",
            "map_list",
            "package_references",
            "path",
        }
        assert expected_keys.issubset(set(proj_info.keys()))
        assert proj_info["title"] == "InfoTest"
        assert proj_info["ident"] == "infotest"
        assert proj_info["max_players"] == 64
        assert proj_info["tick_rate"] == 50

    def test_configure_project(self, tmp_path):
        """Modify project settings and verify they persist."""
        info = create_project("ConfigTest", output_dir=str(tmp_path / "ConfigTest"))
        sbproj = info["sbproj"]

        updated = configure_project(
            sbproj,
            title="Renamed",
            max_players=16,
            tick_rate=30,
            org="neworg",
        )

        assert updated["title"] == "Renamed"
        assert updated["max_players"] == 16
        assert updated["tick_rate"] == 30
        assert updated["org"] == "neworg"

        # Confirm persistence by reloading raw JSON
        raw = load_project(sbproj)
        assert raw["Title"] == "Renamed"
        assert raw["Org"] == "neworg"
        assert raw["Metadata"]["MaxPlayers"] == 16
        assert raw["Metadata"]["TickRate"] == 30

    def test_find_sbproj(self, tmp_path):
        """Test finding .sbproj file in a directory."""
        info = create_project("FindMe", output_dir=str(tmp_path / "FindMe"))
        found = find_sbproj(str(tmp_path / "FindMe"))
        assert found is not None
        assert found.endswith("FindMe.sbproj")

    def test_find_sbproj_not_found(self, tmp_path):
        """Test when no .sbproj exists."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        result = find_sbproj(str(empty_dir))
        assert result is None
