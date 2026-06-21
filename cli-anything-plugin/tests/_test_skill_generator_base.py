# ruff: noqa: F403, F405, E501
"""
Tests for skill_generator.py — SKILL.md generation for CLI-Anything harnesses.

Verifies metadata extraction, SKILL.md generation, and edge cases.

Run with: pytest tests/test_skill_generator.py -v
"""
import os
import sys
import textwrap
import tempfile
from pathlib import Path
import pytest
from skill_generator import (
    extract_cli_metadata,
    generate_skill_md,
    generate_skill_md_simple,
    generate_skill_file,
    extract_intro_from_readme,
    extract_system_package,
    extract_version_from_setup,
    SkillMetadata,
    CommandInfo,
    CommandGroup,
    Example,
)


_PLUGIN_DIR = Path(__file__).resolve().parent.parent


_SCRIPTS_DIR = _PLUGIN_DIR / "scripts"


if (_SCRIPTS_DIR / "skill_generator.py").exists():
    sys.path.insert(0, str(_SCRIPTS_DIR))
else:
    sys.path.insert(0, str(_PLUGIN_DIR))


@pytest.fixture
def harness_dir(tmp_path):
    """Create a minimal harness directory structure."""
    software = "testapp"
    cli_pkg = tmp_path / "cli_anything" / software
    cli_pkg.mkdir(parents=True)

    # __init__.py
    (cli_pkg / "__init__.py").write_text('"""Test application CLI."""\n')

    # README.md
    (cli_pkg / "README.md").write_text(
        textwrap.dedent(f"""\
        # {software}

        A powerful test application for demonstrating CLI harness generation.
        This application supports batch processing and interactive use.
        """)
    )

    # setup.py
    (tmp_path / "setup.py").write_text(
        textwrap.dedent("""\
        from setuptools import setup, find_packages
        setup(
            name="cli-anything-testapp",
            version="2.1.0",
            packages=find_packages(),
        )
        """)
    )

    # CLI file with Click commands
    (cli_pkg / f"{software}_cli.py").write_text(
        textwrap.dedent("""\
        import click

        @click.group()
        def cli():
            \"\"\"Main CLI group.\"\"\"
            pass

        @cli.command()
        def export():
            \"\"\"Export data to file.\"\"\"
            pass

        @cli.command()
        def import_data():
            \"\"\"Import data from file.\"\"\"
            pass
        """)
    )

    return tmp_path


@pytest.fixture
def minimal_harness(tmp_path):
    """Create the absolute minimal harness (just __init__.py)."""
    software = "minimal"
    cli_pkg = tmp_path / "cli_anything" / software
    cli_pkg.mkdir(parents=True)
    (cli_pkg / "__init__.py").write_text("")
    return tmp_path


# fmt: off
__all__ = ['CommandGroup', 'CommandInfo', 'Example', 'Path', 'SkillMetadata', '_PLUGIN_DIR', '_SCRIPTS_DIR', 'extract_cli_metadata', 'extract_intro_from_readme', 'extract_system_package', 'extract_version_from_setup', 'generate_skill_file', 'generate_skill_md', 'generate_skill_md_simple', 'harness_dir', 'minimal_harness', 'os', 'pytest', 'sys', 'tempfile', 'textwrap']  # noqa: E501
# fmt: on
