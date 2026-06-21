# ruff: noqa: F403, F405, E501
from .skill_generator_base import *  # noqa: F403

# fmt: off
from .skill_generator_p1 import CommandGroup, CommandInfo, Example, SkillMetadata, _click_decorator_info, _default_command_name, _default_group_name, _format_display_name, extract_intro_from_readme, extract_version_from_setup  # noqa: E402,E501
# fmt: on


def extract_commands_from_cli(cli_path: Path) -> list[CommandGroup]:
    module = ast.parse(cli_path.read_text(encoding="utf-8"), filename=str(cli_path))
    groups: list[CommandGroup] = []
    group_name_by_function: dict[str, str] = {}
    group_by_display_name: dict[str, CommandGroup] = {}
    functions = [
        node
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    for node in functions:
        for decorator in node.decorator_list:
            owner_name, decorator_name, explicit_name = _click_decorator_info(decorator)
            if owner_name != "cli" or decorator_name != "group":
                continue
            raw_name = explicit_name or _default_group_name(node.name)
            display_name = raw_name.replace("-", " ").title()
            group = CommandGroup(
                name=display_name,
                description=ast.get_docstring(node) or f"Commands for {raw_name}.",
            )
            group_name_by_function[node.name] = display_name
            group_by_display_name[display_name] = group
            groups.append(group)
            break

    for node in functions:
        for decorator in node.decorator_list:
            owner_name, decorator_name, explicit_name = _click_decorator_info(decorator)
            if decorator_name != "command" or owner_name not in group_name_by_function:
                continue
            display_name = group_name_by_function[owner_name]
            cmd_name = explicit_name or _default_command_name(node.name)
            group_by_display_name[display_name].commands.append(
                CommandInfo(
                    cmd_name, ast.get_docstring(node) or f"Execute `{cmd_name}`."
                )
            )
            break
    return groups


def generate_examples(software_name: str) -> list[Example]:
    return [
        Example(
            "Runtime Status",
            "Inspect Zotero paths and backend availability.",
            f"cli-anything-{software_name} app status --json",
        ),
        Example(
            "Read Selected Collection",
            "Persist the collection selected in the Zotero GUI.",
            f"cli-anything-{software_name} collection use-selected --json",
        ),
        Example(
            "Render Citation",
            "Render a citation using Zotero's Local API.",
            f"cli-anything-{software_name} item citation <item-key> --style apa --locale en-US --json",
        ),
        Example(
            "Add Child Note",
            "Create a child note under an existing Zotero item.",
            f'cli-anything-{software_name} note add <item-key> --text "Key takeaway" --json',
        ),
        Example(
            "Build LLM Context",
            "Assemble structured context for downstream model analysis.",
            f"cli-anything-{software_name} item context <item-key> --include-notes --include-links --json",
        ),
    ]


def generate_important_constraints(software_name: str) -> list[str]:
    if software_name != "zotero":
        return []
    return [
        "`search items`, `item export`, `item citation`, and `item bibliography` require Zotero's Local API to be enabled.",
        "`note add` depends on the live Zotero GUI context and expects the same library to be selected in the app.",
        "Import-time PDF attachment support is limited to items created in the same connector session; arbitrary existing-item attachment upload is still out of scope.",
        "Experimental SQLite write commands are local-only, user-library-only, and should be treated as non-stable power-user operations.",
        "If a bare key is duplicated across libraries, set `session use-library <id>` before follow-up commands.",
    ]


def extract_cli_metadata(harness_path: str) -> SkillMetadata:
    harness_root = Path(harness_path)
    cli_root = harness_root / "cli_anything"
    software_dir = next(
        path
        for path in cli_root.iterdir()
        if path.is_dir() and (path / "__init__.py").exists()
    )
    software_name = software_dir.name
    intro = extract_intro_from_readme(
        (software_dir / "README.md").read_text(encoding="utf-8")
    )
    version = extract_version_from_setup(harness_root / "setup.py")
    groups = extract_commands_from_cli(software_dir / f"{software_name}_cli.py")
    return SkillMetadata(
        skill_name=f"cli-anything-{software_name}",
        skill_description=f"CLI harness for {_format_display_name(software_name)}.",
        software_name=software_name,
        skill_intro=intro,
        version=version,
        important_constraints=generate_important_constraints(software_name),
        command_groups=groups,
        examples=generate_examples(software_name),
    )


def _normalize_generated_markdown(content: str) -> str:
    content = re.sub(r"(\|\s*\n)(#{2,3}\s)", r"\1\n\2", content)
    content = re.sub(r"(```\n)(#{2,3}\s)", r"\1\n\2", content)
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip() + "\n"
