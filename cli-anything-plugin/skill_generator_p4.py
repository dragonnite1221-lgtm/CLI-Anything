# ruff: noqa: F403, F405, E501
from .skill_generator_base import *  # noqa: F403

# fmt: off
from .skill_generator_p1 import SkillMetadata, _format_display_name  # noqa: E402,E501
# fmt: on


def generate_skill_md_simple(metadata: SkillMetadata) -> str:
    """Generate SKILL.md without Jinja2 dependency."""
    lines = [
        "---",
        f'name: "{metadata.skill_name}"',
        f'description: "{metadata.skill_description}"',
        "---",
        "",
        f"# {metadata.skill_name}",
        "",
        metadata.skill_intro,
        "",
        "## Installation",
        "",
        f"This CLI is installed as part of the cli-anything-{metadata.software_name} package:",
        "",
        f"```bash",
        f"pip install cli-anything-{metadata.software_name}",
        f"```",
        "",
        "**Prerequisites:**",
        "- Python 3.10+",
        f"- {_format_display_name(metadata.software_name)} must be installed on your system",
    ]

    if metadata.system_package:
        lines.extend(
            [f"- Install {metadata.software_name}: `{metadata.system_package}`"]
        )

    lines.extend(
        [
            "",
            "## Usage",
            "",
            "### Basic Commands",
            "",
            "```bash",
            "# Show help",
            f"cli-anything-{metadata.software_name} --help",
            "",
            "# Start interactive REPL mode",
            f"cli-anything-{metadata.software_name}",
            "",
            "# Create a new project",
            f"cli-anything-{metadata.software_name} project new -o project.json",
            "",
            "# Run with JSON output (for agent consumption)",
            f"cli-anything-{metadata.software_name} --json project info -p project.json",
            "```",
            "",
        ]
    )

    # Add command groups
    if metadata.command_groups:
        lines.append("## Command Groups")
        lines.append("")

        for group in metadata.command_groups:
            lines.append(f"### {group.name}")
            lines.append("")
            lines.append(group.description)
            lines.append("")

            if group.commands:
                lines.append("| Command | Description |")
                lines.append("|---------|-------------|")
                for cmd in group.commands:
                    lines.append(f"| `{cmd.name}` | {cmd.description} |")
                lines.append("")

    # Add examples
    if metadata.examples:
        lines.append("## Examples")
        lines.append("")

        for example in metadata.examples:
            lines.append(f"### {example.title}")
            lines.append("")
            lines.append(example.description)
            lines.append("")
            lines.append("```bash")
            lines.append(example.code)
            lines.append("```")
            lines.append("")

    # Add AI agent guidance
    lines.extend(
        [
            "## For AI Agents",
            "",
            "When using this CLI programmatically:",
            "",
            "1. **Always use `--json` flag** for parseable output",
            "2. **Check return codes** - 0 for success, non-zero for errors",
            "3. **Parse stderr** for error messages on failure",
            "4. **Use absolute paths** for all file operations",
            "5. **Verify outputs exist** after export operations",
            "",
            "## Version",
            "",
            metadata.version,
        ]
    )

    return "\n".join(lines)
