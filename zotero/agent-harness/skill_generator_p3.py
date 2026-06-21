# ruff: noqa: F403, F405, E501
from .skill_generator_base import *  # noqa: F403

# fmt: off
from .skill_generator_p1 import SkillMetadata  # noqa: E402,E501
from .skill_generator_p2 import _normalize_generated_markdown, extract_cli_metadata  # noqa: E402,E501
# fmt: on


def generate_skill_md_simple(metadata: SkillMetadata) -> str:
    lines = [
        "---",
        "name: >-",
        f"  {metadata.skill_name}",
        "description: >-",
        f"  {metadata.skill_description}",
        "---",
        "",
        f"# {metadata.skill_name}",
        "",
        metadata.skill_intro,
        "",
        "## Installation",
        "",
        "```bash",
        "pip install -e .",
        "```",
        "",
        "## Entry Points",
        "",
        "```bash",
        f"cli-anything-{metadata.software_name}",
        f"python -m cli_anything.{metadata.software_name}",
        "```",
        "",
    ]
    if metadata.important_constraints:
        lines.extend(["## Important Constraints", ""])
        for constraint in metadata.important_constraints:
            lines.append(f"- {constraint}")
        lines.append("")
    lines.extend(["## Command Groups", ""])
    for group in metadata.command_groups:
        lines.extend(
            [
                f"### {group.name}",
                "",
                group.description,
                "",
                "| Command | Description |",
                "|---------|-------------|",
            ]
        )
        for cmd in group.commands:
            lines.append(f"| `{cmd.name}` | {cmd.description} |")
        lines.append("")
    lines.extend(["## Examples", ""])
    for example in metadata.examples:
        lines.extend(
            [
                f"### {example.title}",
                "",
                example.description,
                "",
                "```bash",
                example.code,
                "```",
                "",
            ]
        )
    lines.extend(["## Version", "", metadata.version, ""])
    return _normalize_generated_markdown("\n".join(lines))


def generate_skill_md(
    metadata: SkillMetadata, template_path: Optional[str] = None
) -> str:
    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError:
        return generate_skill_md_simple(metadata)

    template = (
        Path(template_path)
        if template_path
        else Path(__file__).parent / "templates" / "SKILL.md.template"
    )
    if not template.exists():
        return generate_skill_md_simple(metadata)
    env = Environment(
        loader=FileSystemLoader(template.parent), trim_blocks=True, lstrip_blocks=True
    )
    tpl = env.get_template(template.name)
    rendered = tpl.render(
        skill_name=metadata.skill_name,
        skill_description=metadata.skill_description,
        software_name=metadata.software_name,
        skill_intro=metadata.skill_intro,
        version=metadata.version,
        important_constraints=metadata.important_constraints,
        command_groups=[
            {
                "name": group.name,
                "description": group.description,
                "commands": [
                    {"name": c.name, "description": c.description}
                    for c in group.commands
                ],
            }
            for group in metadata.command_groups
        ],
        examples=[
            {"title": ex.title, "description": ex.description, "code": ex.code}
            for ex in metadata.examples
        ],
    )
    return _normalize_generated_markdown(rendered)


def generate_skill_file(
    harness_path: str,
    output_path: Optional[str] = None,
    template_path: Optional[str] = None,
) -> str:
    metadata = extract_cli_metadata(harness_path)
    content = generate_skill_md(metadata, template_path=template_path)
    harness_root = Path(harness_path)
    skill_id = f"cli-anything-{harness_root.parent.name.replace('_', '-')}"
    output = (
        Path(output_path)
        if output_path
        else harness_root.parent.parent / "skills" / skill_id / "SKILL.md"
    )
    mirror = (
        harness_root / "cli_anything" / metadata.software_name / "skills" / "SKILL.md"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    if mirror != output:
        mirror.parent.mkdir(parents=True, exist_ok=True)
        mirror.write_text(content, encoding="utf-8")
    return str(output)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate SKILL.md for a CLI-Anything harness"
    )
    parser.add_argument("harness_path")
    parser.add_argument("-o", "--output", default=None)
    parser.add_argument("-t", "--template", default=None)
    args = parser.parse_args(argv)
    print(
        generate_skill_file(
            args.harness_path, output_path=args.output, template_path=args.template
        )
    )
    return 0
