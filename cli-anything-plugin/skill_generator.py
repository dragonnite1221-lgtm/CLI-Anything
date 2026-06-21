# ruff: noqa: F403, F405, E501
from .skill_generator_base import *  # noqa: F403


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate SKILL.md for CLI-Anything harnesses"
    )
    parser.add_argument("harness_path", help="Path to the agent-harness directory")
    parser.add_argument(
        "-o",
        "--output",
        help="Output path for SKILL.md (default: skills/cli-anything-<software>/SKILL.md)",
        default=None,
    )
    parser.add_argument(
        "-t", "--template", help="Path to custom Jinja2 template", default=None
    )

    args = parser.parse_args()

    output_file = generate_skill_file(args.harness_path, args.output, args.template)

    print(f"Generated: {output_file}")

# fmt: off
# re-export full surface
from .skill_generator_p1 import _format_display_name, _canonical_skill_name, CommandInfo, CommandGroup, Example, SkillMetadata, extract_intro_from_readme, extract_system_package, extract_version_from_setup  # noqa: F401,E501
from .skill_generator_p2 import extract_commands_from_cli  # noqa: F401,E501
from .skill_generator_p3 import generate_examples, extract_cli_metadata  # noqa: F401,E501
from .skill_generator_p4 import generate_skill_md_simple  # noqa: F401,E501
from .skill_generator_p5 import generate_skill_md, generate_skill_file  # noqa: F401,E501
# fmt: on
