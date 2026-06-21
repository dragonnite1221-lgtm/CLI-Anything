# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSound:
    """Tests for sound event creation and parsing."""

    def test_create_sound_event(self, tmp_path):
        path = str(tmp_path / "bang.sound")
        result = create_sound_event(
            "bang", sounds=["sounds/bang.vsnd"], output_path=path
        )
        assert result["name"] == "bang"
        assert os.path.isfile(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["Sounds"] == ["sounds/bang.vsnd"]
        assert data["__version"] == 1

    def test_create_sound_multiple(self, tmp_path):
        result = create_sound_event(
            "footstep",
            sounds=["sounds/step1.vsnd", "sounds/step2.vsnd", "sounds/step3.vsnd"],
            volume="0.5",
        )
        assert len(result["data"]["Sounds"]) == 3
        assert result["data"]["Volume"] == "0.5"

    def test_parse_sound_event(self, tmp_path):
        path = str(tmp_path / "test.sound")
        create_sound_event(
            "test", sounds=["sounds/a.vsnd"], volume="0.7", output_path=path
        )
        parsed = parse_sound_event(path)
        assert parsed["name"] == "test"
        assert parsed["volume"] == "0.7"
        assert "sounds/a.vsnd" in parsed["sounds"]

    def test_sound_defaults(self):
        result = create_sound_event("default")
        data = result["data"]
        assert data["Volume"] == "1"
        assert data["Pitch"] == "1"
        assert data["Decibels"] == 70
        assert data["Occlusion"] is True
        assert data["UI"] is False


class TestLocalization:
    """Tests for translation file management."""

    def test_create_translation_file(self, tmp_path):
        path = str(tmp_path / "en.json")
        result = create_translation_file(
            lang="en",
            initial_keys={"game.title": "My Game"},
            output_path=path,
        )
        assert result["lang"] == "en"
        assert result["key_count"] == 1
        assert os.path.isfile(path)

    def test_set_and_get_key(self, tmp_path):
        path = str(tmp_path / "en.json")
        create_translation_file(lang="en", output_path=path)
        set_key(path, "ui.button.start", "Start Game")
        value = get_key(path, "ui.button.start")
        assert value == "Start Game"

    def test_list_keys(self, tmp_path):
        path = str(tmp_path / "en.json")
        create_translation_file(
            lang="en",
            initial_keys={"b.key": "B", "a.key": "A", "c.key": "C"},
            output_path=path,
        )
        keys = list_keys(path)
        assert keys == ["a.key", "b.key", "c.key"]  # sorted

    def test_remove_key(self, tmp_path):
        path = str(tmp_path / "en.json")
        create_translation_file(
            lang="en",
            initial_keys={"game.title": "Title", "game.desc": "Desc"},
            output_path=path,
        )
        removed = remove_key(path, "game.title")
        assert removed is True
        assert get_key(path, "game.title") is None
        assert get_key(path, "game.desc") == "Desc"

    def test_remove_key_not_found(self, tmp_path):
        path = str(tmp_path / "en.json")
        create_translation_file(lang="en", output_path=path)
        removed = remove_key(path, "nonexistent")
        assert removed is False
