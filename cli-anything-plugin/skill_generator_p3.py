# ruff: noqa: F403, F405, E501
from .skill_generator_base import *  # noqa: F403

# fmt: off
from .skill_generator_p1 import CommandGroup, Example, SkillMetadata, _canonical_skill_name, _format_display_name, extract_intro_from_readme, extract_system_package, extract_version_from_setup  # noqa: E402,E501
from .skill_generator_p2 import extract_commands_from_cli  # noqa: E402,E501
# fmt: on


def generate_examples(
    software_name: str, command_groups: list[CommandGroup]
) -> list[Example]:
    """Generate usage examples based on software type and available commands."""
    examples = []

    # Basic project creation example
    examples.append(
        Example(
            title="Create a New Project",
            description=f"Create a new {software_name} project file.",
            code=f"""cli-anything-{software_name} project new -o myproject.json
# Or with JSON output for programmatic use
cli-anything-{software_name} --json project new -o myproject.json""",
        )
    )

    # REPL usage example
    examples.append(
        Example(
            title="Interactive REPL Session",
            description="Start an interactive session with undo/redo support.",
            code=f"""cli-anything-{software_name}
# Enter commands interactively
# Use 'help' to see available commands
# Use 'undo' and 'redo' for history navigation""",
        )
    )

    # Export example if export commands exist
    for group in command_groups:
        if "export" in group.name.lower():
            examples.append(
                Example(
                    title="Export Project",
                    description="Export the project to a final output format.",
                    code=f"""cli-anything-{software_name} --project myproject.json export render output.pdf --overwrite""",
                )
            )
            break

    return examples


def extract_cli_metadata(harness_path: str) -> SkillMetadata:
    """
    Extract metadata from a CLI-Anything harness directory.

    Args:
        harness_path: Path to the agent-harness directory

    Returns:
        SkillMetadata containing extracted information
    """
    harness_path = Path(harness_path)

    # Find the cli_anything/<software> directory
    cli_anything_dir = harness_path / "cli_anything"
    if not cli_anything_dir.exists():
        raise ValueError(
            f"cli_anything directory not found in {harness_path}. "
            "Ensure the harness structure includes cli_anything/<software>/"
        )
    software_dirs = [
        d
        for d in cli_anything_dir.iterdir()
        if d.is_dir() and (d / "__init__.py").exists()
    ]

    if not software_dirs:
        raise ValueError(f"No CLI package found in {harness_path}")

    software_dir = software_dirs[0]
    software_name = software_dir.name

    # Extract metadata from README.md
    readme_path = software_dir / "README.md"
    skill_intro = ""
    system_package = None

    if readme_path.exists():
        readme_content = readme_path.read_text(encoding="utf-8")
        skill_intro = extract_intro_from_readme(readme_content)
        system_package = extract_system_package(readme_content)

    # Extract version from setup.py
    setup_path = harness_path / "setup.py"
    version = "1.0.0"

    if setup_path.exists():
        version = extract_version_from_setup(setup_path)

    # Extract commands from CLI file
    cli_file = software_dir / f"{software_name}_cli.py"
    command_groups = []

    if cli_file.exists():
        command_groups = extract_commands_from_cli(cli_file)

    # Generate examples based on software type
    examples = generate_examples(software_name, command_groups)

    # Build skill name and description
    skill_name = _canonical_skill_name(harness_path, software_name)
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
