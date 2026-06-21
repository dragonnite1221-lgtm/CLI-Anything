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
    important_constraints: list[str] = field(default_factory=list)
    command_groups: list[CommandGroup] = field(default_factory=list)
    examples: list[Example] = field(default_factory=list)


def extract_intro_from_readme(content: str) -> str:
    lines = content.splitlines()
    intro: list[str] = []
    seen_title = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if seen_title and intro:
                break
            continue
        if stripped.startswith("# "):
            seen_title = True
            continue
        if stripped.startswith("##"):
            break
        if seen_title:
            intro.append(stripped)
    return " ".join(intro) or "Agent-native CLI interface."


def extract_version_from_setup(setup_path: Path) -> str:
    content = setup_path.read_text(encoding="utf-8")
    match = re.search(r'PACKAGE_VERSION\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    return match.group(1) if match else "1.0.0"


def _string_literal(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _click_decorator_info(
    decorator: ast.AST,
) -> tuple[str | None, str | None, str | None]:
    target: ast.AST
    explicit_name: str | None = None
    if isinstance(decorator, ast.Call):
        target = decorator.func
        if decorator.args:
            explicit_name = _string_literal(decorator.args[0])
        if explicit_name is None:
            for keyword in decorator.keywords:
                if keyword.arg == "name":
                    explicit_name = _string_literal(keyword.value)
                    break
    else:
        target = decorator
    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
        return target.value.id, target.attr, explicit_name
    return None, None, explicit_name


def _default_group_name(function_name: str) -> str:
    return re.sub(r"_group$", "", function_name).replace("_", " ")


def _default_command_name(function_name: str) -> str:
    return re.sub(r"_command$", "", function_name).replace("_", "-")
