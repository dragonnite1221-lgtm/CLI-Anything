# ruff: noqa: F403, F405, E501
from .skill_generator_base import *  # noqa: F403

# fmt: off
from .skill_generator_p1 import CommandGroup, CommandInfo  # noqa: E402,E501
# fmt: on


def extract_commands_from_cli(cli_path: Path) -> list[CommandGroup]:
    """Extract command groups and commands from CLI file."""
    content = cli_path.read_text(encoding="utf-8")
    groups = []

    # Find Click group decorators
    # Pattern handles:
    # - Multi-line decorators (decorators on separate lines)
    # - Docstrings on the same line or following line after function definition
    # - Various Click decorator patterns like @click.option(), @click.argument()
    # Uses re.DOTALL to match across newlines between decorator and def
    group_pattern = (
        r"@(\w+)\.group\([^)]*\)"  # @xxx.group(...)
        r"(?:\s*@[\w.]+\([^)]*\))*"  # optional additional decorators
        r"\s*def\s+(\w+)\([^)]*\)"  # def xxx(...):
        r":\s*"  # colon with optional whitespace
        r'(?:"""([\s\S]*?)"""|\'\'\'([\s\S]*?)\'\'\')?'  # optional docstring (""" or ''')
    )

    for match in re.finditer(group_pattern, content):
        group_func = match.group(2)
        # Docstring can be in group 3 (triple-double) or group 4 (triple-single)
        group_doc = (match.group(3) or match.group(4) or "").strip()

        group_name = group_func.replace("_", " ").title()
        if not group_name:
            group_name = group_func.title()

        groups.append(
            CommandGroup(
                name=group_name,
                description=group_doc
                or f"Commands for {group_name.lower()} operations.",
                commands=[],
            )
        )

    # Find Click command decorators
    # Pattern handles:
    # - Multi-line decorators (decorators on separate lines)
    # - Docstrings on the same line or following line after function definition
    # - Various Click decorator patterns like @click.option(), @click.argument()
    command_pattern = (
        r"@(\w+)\.command\([^)]*\)"  # @xxx.command(...)
        r"(?:\s*@[\w.]+\([^)]*\))*"  # optional additional decorators
        r"\s*def\s+(\w+)\([^)]*\)"  # def xxx(...):
        r":\s*"  # colon with optional whitespace
        r'(?:"""([\s\S]*?)"""|\'\'\'([\s\S]*?)\'\'\')?'  # optional docstring (""" or ''')
    )

    for match in re.finditer(command_pattern, content):
        group_name = match.group(1)
        cmd_name = match.group(2)
        # Docstring can be in group 3 (triple-double) or group 4 (triple-single)
        cmd_doc = (match.group(3) or match.group(4) or "").strip()

        # Find the matching group
        for group in groups:
            if group.name.lower().replace(" ", "_") == group_name.lower():
                group.commands.append(
                    CommandInfo(
                        name=cmd_name.replace("_", "-"),
                        description=cmd_doc or f"Execute {cmd_name} operation.",
                    )
                )

    # If no groups found, create a default one with all commands
    if not groups:
        default_group = CommandGroup(
            name="General", description="General commands for the CLI.", commands=[]
        )

        for match in re.finditer(command_pattern, content):
            cmd_name = match.group(2)
            # Docstring can be in group 3 (triple-double) or group 4 (triple-single)
            cmd_doc = (match.group(3) or match.group(4) or "").strip()
            default_group.commands.append(
                CommandInfo(
                    name=cmd_name.replace("_", "-"),
                    description=cmd_doc or f"Execute {cmd_name} operation.",
                )
            )

        if default_group.commands:
            groups.append(default_group)

    return groups
