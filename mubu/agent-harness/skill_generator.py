# ruff: noqa: F403, F405, E501
from .skill_generator_base import *  # noqa: F403
from .skill_generator_p5 import main  # noqa: F401


if __name__ == "__main__":
    raise SystemExit(main())

# fmt: off
# re-export full surface
from .skill_generator_p1 import _format_display_name, CommandInfo, CommandGroup, Example, SkillMetadata, extract_intro_from_readme, extract_system_package, extract_version_from_setup  # noqa: F401,E501
from .skill_generator_p2 import extract_commands_from_cli, generate_examples  # noqa: F401,E501
from .skill_generator_p3 import extract_cli_metadata  # noqa: F401,E501
from .skill_generator_p4 import generate_skill_md_simple  # noqa: F401,E501
from .skill_generator_p5 import generate_skill_md, generate_skill_file  # noqa: F401,E501
# fmt: on
