# ruff: noqa: F403, F405, E501
from .skill_generator_base import *  # noqa: F403

# fmt: off
from .skill_generator_p1 import CommandGroup, CommandInfo, Example  # noqa: E402,E501
# fmt: on


def extract_commands_from_cli(cli_path: Path) -> list[CommandGroup]:
    content = cli_path.read_text(encoding="utf-8")
    groups: list[CommandGroup] = []

    group_pattern = (
        r"@(\w+)\.group\(([^)]*)\)"
        r"(?:\s*@[\w.]+(?:\([^)]*\))?)*"
        r"\s*def\s+(\w+)\([^)]*\)"
        r"(?:\s*->\s*[^:]+)?"
        r":\s*"
        r'(?:"""([\s\S]*?)"""|\'\'\'([\s\S]*?)\'\'\')?'
    )
    for match in re.finditer(group_pattern, content):
        decorator_owner = match.group(1)
        group_func = match.group(3)
        group_doc = (match.group(4) or match.group(5) or "").strip()
        if decorator_owner == "click" or group_func == "cli":
            continue
        groups.append(
            CommandGroup(
                name=group_func.replace("_", " ").title() or group_func.title(),
                description=group_doc
                or f"Commands for {group_func.replace('_', ' ')} operations.",
            )
        )

    command_pattern = (
        r"@(\w+)\.command\(([^)]*)\)"
        r"(?:\s*@[\w.]+(?:\([^)]*\))?)*"
        r"\s*def\s+(\w+)\([^)]*\)"
        r"(?:\s*->\s*[^:]+)?"
        r":\s*"
        r'(?:"""([\s\S]*?)"""|\'\'\'([\s\S]*?)\'\'\')?'
    )
    for match in re.finditer(command_pattern, content):
        group_name = match.group(1)
        decorator_args = match.group(2)
        cmd_name = match.group(3)
        cmd_doc = (match.group(4) or match.group(5) or "").strip()
        if group_name == "cli":
            continue
        explicit_name = re.search(r'["\']([^"\']+)["\']', decorator_args)
        command_display_name = (
            explicit_name.group(1) if explicit_name else cmd_name.replace("_", "-")
        )
        for group in groups:
            if group.name.lower().replace(" ", "_") == group_name.lower():
                group.commands.append(
                    CommandInfo(
                        name=command_display_name,
                        description=cmd_doc
                        or f"Execute {cmd_name.replace('_', '-')} operation.",
                    )
                )

    if not groups:
        default_group = CommandGroup(
            name="General", description="General commands for the CLI."
        )
        for match in re.finditer(command_pattern, content):
            decorator_args = match.group(2)
            cmd_name = match.group(3)
            cmd_doc = (match.group(4) or match.group(5) or "").strip()
            explicit_name = re.search(r'["\']([^"\']+)["\']', decorator_args)
            default_group.commands.append(
                CommandInfo(
                    name=explicit_name.group(1)
                    if explicit_name
                    else cmd_name.replace("_", "-"),
                    description=cmd_doc
                    or f"Execute {cmd_name.replace('_', '-')} operation.",
                )
            )
        if default_group.commands:
            groups.append(default_group)

    return groups


def generate_examples(
    software_name: str, command_groups: list[CommandGroup]
) -> list[Example]:
    examples = [
        Example(
            title="Interactive REPL Session",
            description="Start an interactive session with persistent document and node context.",
            code=f"""cli-anything-{software_name}
# Enter commands interactively
# Use 'help' to see builtins
# Use session commands to persist current-doc/current-node""",
        )
    ]

    group_names = {group.name.lower() for group in command_groups}
    if "discover" in group_names:
        examples.append(
            Example(
                title="Discover Current Daily Note",
                description="Resolve the current daily note from an explicit folder reference.",
                code=f"""cli-anything-{software_name} --json discover daily-current '<daily-folder-ref>'""",
            )
        )
    if "mutate" in group_names:
        examples.append(
            Example(
                title="Dry-Run Atomic Update",
                description="Inspect the exact outgoing payload before a live mutation.",
                code=(
                    f"cli-anything-{software_name} mutate update-text "
                    "'<doc-ref>' --node-id <node-id> --text 'new text' --json"
                ),
            )
        )
    return examples
