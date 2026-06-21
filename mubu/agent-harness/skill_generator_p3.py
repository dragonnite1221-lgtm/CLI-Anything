# ruff: noqa: F403, F405, E501
from .skill_generator_base import *  # noqa: F403

# fmt: off
from .skill_generator_p1 import SkillMetadata, _format_display_name, extract_intro_from_readme, extract_system_package, extract_version_from_setup  # noqa: E402,E501
from .skill_generator_p2 import extract_commands_from_cli, generate_examples  # noqa: E402,E501
# fmt: on


def extract_cli_metadata(harness_path: str) -> SkillMetadata:
    harness_root = Path(harness_path)
    cli_anything_dir = harness_root / "cli_anything"
    if not cli_anything_dir.exists():
        raise ValueError(f"cli_anything directory not found in {harness_root}")

    software_dirs = [
        path
        for path in cli_anything_dir.iterdir()
        if path.is_dir() and (path / "__init__.py").exists()
    ]
    if not software_dirs:
        raise ValueError(f"No CLI package found in {harness_root}")

    software_dir = software_dirs[0]
    software_name = software_dir.name
    readme_path = software_dir / "README.md"
    skill_intro = ""
    system_package = None
    if readme_path.exists():
        readme_content = readme_path.read_text(encoding="utf-8")
        skill_intro = extract_intro_from_readme(readme_content)
        system_package = extract_system_package(readme_content)

    setup_path = harness_root / "setup.py"
    version = extract_version_from_setup(setup_path) if setup_path.exists() else "1.0.0"

    cli_file = software_dir / f"{software_name}_cli.py"
    command_groups = extract_commands_from_cli(cli_file) if cli_file.exists() else []
    examples = generate_examples(software_name, command_groups)
    skill_name = f"cli-anything-{software_name}"
    if skill_intro:
        intro_snippet = skill_intro[:100]
        suffix = "..." if len(skill_intro) > 100 else ""
        skill_description = f"Command-line interface for {_format_display_name(software_name)} - {intro_snippet}{suffix}"
    else:
        skill_description = (
            f"Command-line interface for {_format_display_name(software_name)}"
        )

    return SkillMetadata(
        skill_name=skill_name,
        skill_description=skill_description,
        software_name=software_name,
        skill_intro=skill_intro,
        version=version,
        system_package=system_package,
        command_groups=command_groups,
        examples=examples,
    )
