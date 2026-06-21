# ruff: noqa: F403, F405, E501
from .skill_generator_base import *  # noqa: F403


def _format_display_name(name: str) -> str:
    return name.replace("_", " ").replace("-", " ").title()


@dataclass
class CommandInfo:
    name: str
    description: str


@dataclass
class CommandGroup:
    name: str
    description: str
    commands: list[CommandInfo] = field(default_factory=list)


@dataclass
class Example:
    title: str
    description: str
    code: str


@dataclass
class SkillMetadata:
    skill_name: str
    skill_description: str
    software_name: str
    skill_intro: str
    version: str
    system_package: Optional[str] = None
    command_groups: list[CommandGroup] = field(default_factory=list)
    examples: list[Example] = field(default_factory=list)


def extract_intro_from_readme(content: str) -> str:
    lines = content.split("\n")
    intro_lines: list[str] = []
    in_intro = False

    for line in lines:
        line = line.strip()
        if not line:
            if in_intro and intro_lines:
                break
            continue
        if line.startswith("# "):
            in_intro = True
            continue
        if line.startswith("##"):
            break
        if in_intro:
            intro_lines.append(line)

    return " ".join(intro_lines) or "CLI interface for the software."


def extract_system_package(content: str) -> Optional[str]:
    patterns = [
        r"`apt install ([\w\-]+)`",
        r"`brew install ([\w\-]+)`",
        r"`apt-get install ([\w\-]+)`",
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            package = match.group(1)
            if "apt-get" in pattern:
                return f"apt-get install {package}"
            elif "apt" in pattern:
                return f"apt install {package}"
            elif "brew" in pattern:
                return f"brew install {package}"
    return None


def extract_version_from_setup(setup_path: Path) -> str:
    content = setup_path.read_text(encoding="utf-8")
    direct_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    if direct_match:
        return direct_match.group(1)

    constant_match = re.search(r'PACKAGE_VERSION\s*=\s*["\']([^"\']+)["\']', content)
    if constant_match:
        return constant_match.group(1)

    return "1.0.0"
