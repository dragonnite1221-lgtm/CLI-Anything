# ruff: noqa: F403, F405, E501
from ._test_skill_generator_base import *  # noqa: F403


class TestEdgeCases:
    def test_harness_without_readme(self, tmp_path):
        """Harness with no README.md should have empty intro."""
        software = "noreadme"
        cli_pkg = tmp_path / "cli_anything" / software
        cli_pkg.mkdir(parents=True)
        (cli_pkg / "__init__.py").write_text("")
        # No README.md, no setup.py, no CLI file

        metadata = extract_cli_metadata(str(tmp_path))
        assert metadata.software_name == "noreadme"
        assert metadata.skill_intro == ""  # No README → empty intro
        assert metadata.version == "1.0.0"
        assert metadata.command_groups == []
        # skill_description must not contain trailing " - ..." when intro is empty
        assert " - " not in metadata.skill_description
        assert not metadata.skill_description.endswith("...")

    def test_harness_with_system_package(self, tmp_path):
        """README with apt install instructions should extract system_package."""
        software = "syspkg"
        cli_pkg = tmp_path / "cli_anything" / software
        cli_pkg.mkdir(parents=True)
        (cli_pkg / "__init__.py").write_text("")
        (cli_pkg / "README.md").write_text(
            "# Syspkg\n\nInstall via `apt install syspkg-tool`.\n"
        )

        metadata = extract_cli_metadata(str(tmp_path))
        assert metadata.system_package is not None
        assert "syspkg-tool" in metadata.system_package

    def test_malformed_setup_py(self, tmp_path):
        """Malformed setup.py should default to version 1.0.0."""
        software = "badsetup"
        cli_pkg = tmp_path / "cli_anything" / software
        cli_pkg.mkdir(parents=True)
        (cli_pkg / "__init__.py").write_text("")
        (tmp_path / "setup.py").write_text("THIS IS NOT VALID PYTHON { } }")

        metadata = extract_cli_metadata(str(tmp_path))
        assert metadata.version == "1.0.0"

    def test_empty_setup_py(self, tmp_path):
        """Empty setup.py should default to 1.0.0."""
        software = "emptysetup"
        cli_pkg = tmp_path / "cli_anything" / software
        cli_pkg.mkdir(parents=True)
        (cli_pkg / "__init__.py").write_text("")
        (tmp_path / "setup.py").write_text("")

        metadata = extract_cli_metadata(str(tmp_path))
        assert metadata.version == "1.0.0"
