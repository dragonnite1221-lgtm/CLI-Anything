# ruff: noqa: F403, F405, E501
from .codegen_base import *  # noqa: F403

# fmt: off
from .codegen_p1 import _format_property  # noqa: E402,E501
# fmt: on


def generate_gameresource(
    class_name: str,
    display_name: str,
    extension: str,
    description: str = "",
    properties: Optional[list[dict]] = None,
    namespace: Optional[str] = None,
) -> dict:
    """Generate a GameResource class.

    Args:
        class_name: PascalCase name, e.g. "TowerData".
        display_name: Human-readable name shown in editor, e.g. "Tower Data".
        extension: File extension for the resource, e.g. "tower".
        description: Short description of the resource.
        properties: List of property dicts (same format as generate_component).
        namespace: Optional namespace wrapper.

    Returns:
        Dict with keys: filename, content, class_name.
    """
    properties = properties or []

    lines: list[str] = []
    lines.append("using Sandbox;")
    lines.append("")

    if namespace:
        lines.append(f"namespace {namespace}")
        lines.append("{")

    indent = "\t" if namespace else ""

    # GameResource attribute
    lines.append(
        f'{indent}[GameResource( "{display_name}", "{extension}", "{description}" )]'
    )
    lines.append(f"{indent}public class {class_name} : GameResource")
    lines.append(f"{indent}{{")

    for prop in properties:
        prop_str = _format_property(prop, is_networked=False)
        for pline in prop_str.split("\n"):
            lines.append(f"{indent}\t{pline}")

    lines.append(f"{indent}}}")

    if namespace:
        lines.append("}")

    lines.append("")
    content = "\r\n".join(lines)

    return {
        "filename": f"{class_name}.cs",
        "content": content,
        "class_name": class_name,
    }


def generate_editor_menu(
    class_name: str,
    menu_path: str,
    method_name: str = "OpenMenu",
    dialog_title: str = "",
    dialog_message: str = "",
) -> dict:
    """Generate an editor menu class.

    Args:
        class_name: PascalCase name, e.g. "MyEditorTool".
        menu_path: Menu path string, e.g. "Tools/My Tool".
        method_name: Name of the static method, default "OpenMenu".
        dialog_title: Title for the editor dialog (optional).
        dialog_message: Message for the editor dialog (optional).

    Returns:
        Dict with keys: filename, content, class_name.
    """
    lines: list[str] = []
    lines.append("using Editor;")
    lines.append("using Sandbox;")
    lines.append("")

    lines.append(f"public static class {class_name}")
    lines.append("{")

    lines.append(f'\t[Menu( "Editor", "{menu_path}" )]')
    lines.append(f"\tpublic static void {method_name}()")
    lines.append("\t{")

    if dialog_title or dialog_message:
        title = dialog_title or class_name
        message = dialog_message or ""
        lines.append(f'\t\tEditorUtility.DisplayDialog( "{title}", "{message}" );')
    else:
        lines.append(f'\t\tLog.Info( "{class_name}.{method_name} invoked" );')

    lines.append("\t}")
    lines.append("}")
    lines.append("")
    content = "\r\n".join(lines)

    return {
        "filename": f"{class_name}.cs",
        "content": content,
        "class_name": class_name,
    }
