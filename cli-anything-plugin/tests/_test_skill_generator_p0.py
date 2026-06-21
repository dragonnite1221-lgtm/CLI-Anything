# ruff: noqa: F403, F405, E501
from ._test_skill_generator_base import *  # noqa: F403


class TestExtractCliMetadata:
    def test_extracts_software_name(self, harness_dir):
        metadata = extract_cli_metadata(str(harness_dir))
        assert metadata.software_name == "testapp"

    def test_extracts_skill_name(self, harness_dir):
        metadata = extract_cli_metadata(str(harness_dir))
        assert metadata.skill_name == "cli-anything-testapp"

    def test_extracts_version_from_setup_py(self, harness_dir):
        metadata = extract_cli_metadata(str(harness_dir))
        assert metadata.version == "2.1.0"

    def test_extracts_intro_from_readme(self, harness_dir):
        metadata = extract_cli_metadata(str(harness_dir))
        assert "powerful test application" in metadata.skill_intro

    def test_extracts_command_groups(self, harness_dir):
        metadata = extract_cli_metadata(str(harness_dir))
        assert len(metadata.command_groups) > 0

    def test_extracts_commands_from_cli_file(self, harness_dir):
        metadata = extract_cli_metadata(str(harness_dir))
        all_commands = []
        for group in metadata.command_groups:
            all_commands.extend(group.commands)
        # Should find at least 'export' and 'import-data'
        cmd_names = [c.name for c in all_commands]
        assert "export" in cmd_names
        assert "import-data" in cmd_names

    def test_generates_examples(self, harness_dir):
        metadata = extract_cli_metadata(str(harness_dir))
        assert len(metadata.examples) > 0

    def test_minimal_harness(self, minimal_harness):
        metadata = extract_cli_metadata(str(minimal_harness))
        assert metadata.software_name == "minimal"
        assert metadata.version == "1.0.0"  # Default when no setup.py

    def test_raises_on_missing_cli_anything_dir(self, tmp_path):
        with pytest.raises(ValueError, match="cli_anything directory not found"):
            extract_cli_metadata(str(tmp_path))

    def test_raises_on_empty_cli_anything_dir(self, tmp_path):
        (tmp_path / "cli_anything").mkdir()
        with pytest.raises(ValueError, match="No CLI package found"):
            extract_cli_metadata(str(tmp_path))

    def test_description_contains_software_name(self, harness_dir):
        metadata = extract_cli_metadata(str(harness_dir))
        assert "testapp" in metadata.skill_description.lower() or "Testapp" in metadata.skill_description


class TestExtractVersionFromSetup:
    def test_extracts_version(self, tmp_path):
        setup_py = tmp_path / "setup.py"
        setup_py.write_text('version="3.2.1"')
        assert extract_version_from_setup(setup_py) == "3.2.1"

    def test_extracts_version_single_quotes(self, tmp_path):
        setup_py = tmp_path / "setup.py"
        setup_py.write_text("version='1.0.0'")
        assert extract_version_from_setup(setup_py) == "1.0.0"

    def test_returns_default_when_no_version(self, tmp_path):
        setup_py = tmp_path / "setup.py"
        setup_py.write_text("# no version here")
        assert extract_version_from_setup(setup_py) == "1.0.0"


class TestExtractIntroFromReadme:
    def test_extracts_first_paragraph(self):
        content = "# My App\n\nThis is the intro paragraph.\n\n## Section\nMore text"
        intro = extract_intro_from_readme(content)
        assert "This is the intro paragraph" in intro

    def test_returns_default_for_empty(self):
        content = "# Title\n## Section\n"
        intro = extract_intro_from_readme(content)
        assert "CLI interface" in intro

    def test_handles_multiline_intro(self):
        content = "# App\nLine one.\nLine two.\n\n## Details"
        intro = extract_intro_from_readme(content)
        assert "Line one" in intro
        assert "Line two" in intro


class TestExtractSystemPackage:
    def test_apt_install(self):
        content = "Install with `apt install mytool`."
        result = extract_system_package(content)
        assert result == "apt install mytool"

    def test_brew_install(self):
        content = "Install with `brew install mytool`."
        result = extract_system_package(content)
        assert result == "brew install mytool"

    def test_apt_get_install_returns_apt_get_command(self):
        # Regression: apt-get pattern contains "apt" as a substring, so the
        # condition must check "apt-get" before "apt" to avoid returning the
        # wrong command ("apt install" instead of "apt-get install").
        content = "Install with `apt-get install mytool`."
        result = extract_system_package(content)
        assert result == "apt-get install mytool", (
            f"Expected 'apt-get install mytool', got {result!r}"
        )

    def test_returns_none_when_no_match(self):
        content = "No installation instructions here."
        assert extract_system_package(content) is None
