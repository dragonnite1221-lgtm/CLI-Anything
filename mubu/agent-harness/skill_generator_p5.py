# ruff: noqa: F403, F405, E501
from .skill_generator_base import *  # noqa: F403

# fmt: off
from .skill_generator_p1 import SkillMetadata  # noqa: E402,E501
from .skill_generator_p3 import extract_cli_metadata  # noqa: E402,E501
from .skill_generator_p4 import generate_skill_md_simple  # noqa: E402,E501
# fmt: on


def generate_skill_md(
    metadata: SkillMetadata, template_path: Optional[str] = None
) -> str:
    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError:
        return generate_skill_md_simple(metadata)

    if template_path is None:
        template_path = Path(__file__).parent / "templates" / "SKILL.md.template"
    else:
        template_path = Path(template_path)

    if not template_path.exists():
        return generate_skill_md_simple(metadata)

    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(template_path.name)
    return template.render(
        skill_name=metadata.skill_name,
        skill_description=metadata.skill_description,
        software_name=metadata.software_name,
        skill_intro=metadata.skill_intro,
        version=metadata.version,
        system_package=metadata.system_package,
        command_groups=[
            {
                "name": group.name,
                "description": group.description,
                "commands": [
                    {"name": command.name, "description": command.description}
                    for command in group.commands
                ],
            }
            for group in metadata.command_groups
        ],
        examples=[
            {
                "title": example.title,
                "description": example.description,
                "code": example.code,
            }
            for example in metadata.examples
        ],
    )


def generate_skill_file(
    harness_path: str,
    output_path: Optional[str] = None,
    template_path: Optional[str] = None,
) -> str:
    metadata = extract_cli_metadata(harness_path)
    content = generate_skill_md(metadata, template_path)
    harness_root = Path(harness_path)
    skill_id = f"cli-anything-{harness_root.parent.name.replace('_', '-')}"
    if output_path is None:
        output = harness_root.parent.parent / "skills" / skill_id / "SKILL.md"
    else:
        output = Path(output_path)
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
        description="Generate SKILL.md for CLI-Anything harnesses"
    )
    parser.add_argument("harness_path", help="Path to the agent-harness directory")
    parser.add_argument("-o", "--output", help="Output path for SKILL.md", default=None)
    parser.add_argument(
        "-t", "--template", help="Path to a custom Jinja2 template", default=None
    )
    args = parser.parse_args(argv)
    output_path = generate_skill_file(
        args.harness_path, output_path=args.output, template_path=args.template
    )
    print(output_path)
    return 0
