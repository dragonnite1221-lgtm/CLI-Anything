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
    """
    Generate SKILL.md content from metadata using Jinja2 template.

    Args:
        metadata: SkillMetadata containing CLI information
        template_path: Optional path to custom template file

    Returns:
        Generated SKILL.md content as string
    """
    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError:
        # Fallback to simple string formatting if Jinja2 not available
        return generate_skill_md_simple(metadata)

    # Load template
    if template_path is None:
        template_path = Path(__file__).parent / "templates" / "SKILL.md.template"
    else:
        template_path = Path(template_path)

    if not template_path.exists():
        return generate_skill_md_simple(metadata)

    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(template_path.name)

    # Render template
    return template.render(
        skill_name=metadata.skill_name,
        skill_description=metadata.skill_description,
        software_name=metadata.software_name,
        skill_intro=metadata.skill_intro,
        version=metadata.version,
        system_package=metadata.system_package,
        command_groups=[
            {
                "name": g.name,
                "description": g.description,
                "commands": [
                    {"name": c.name, "description": c.description} for c in g.commands
                ],
            }
            for g in metadata.command_groups
        ],
        examples=[
            {"title": e.title, "description": e.description, "code": e.code}
            for e in metadata.examples
        ],
    )


def generate_skill_file(
    harness_path: str,
    output_path: Optional[str] = None,
    template_path: Optional[str] = None,
) -> str:
    """
    Generate a SKILL.md file for a CLI-Anything harness.

    Args:
        harness_path: Path to the agent-harness directory
        output_path: Optional output path for SKILL.md
                     (default: skills/cli-anything-<software>/SKILL.md)
        template_path: Optional path to custom Jinja2 template

    Returns:
        Path to the generated SKILL.md file
    """
    # Extract metadata
    metadata = extract_cli_metadata(harness_path)

    # Generate content
    content = generate_skill_md(metadata, template_path)

    # Determine output path
    harness_path_obj = Path(harness_path)
    compatibility_path = (
        harness_path_obj
        / "cli_anything"
        / metadata.software_name
        / "skills"
        / "SKILL.md"
    )
    if output_path is None:
        repo_root = harness_path_obj.parent.parent
        output_path = repo_root / "skills" / metadata.skill_name / "SKILL.md"
    else:
        output_path = Path(output_path)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    output_path.write_text(content, encoding="utf-8")
    if compatibility_path != output_path:
        compatibility_path.parent.mkdir(parents=True, exist_ok=True)
        compatibility_path.write_text(content, encoding="utf-8")

    return str(output_path)
