# ruff: noqa: F403, F405, E501
from .codegen_base import *  # noqa: F403

# fmt: off
from .codegen_p4 import generate_razor  # noqa: E402,E501
# fmt: on


def generate_panel_component(
    class_name: str,
    properties: Optional[list[dict]] = None,
    namespace: Optional[str] = None,
    z_index: int = 100,
    opacity: float = 1.0,
    root_class: Optional[str] = None,
) -> dict:
    """Scaffold a Razor PanelComponent intended to live on the same GameObject
    as a ScreenPanel.

    s&box quirk (see project CLAUDE.md): ``PanelComponent`` input only works
    when both ``ScreenPanel`` and the ``PanelComponent`` are on the same
    ``GameObject``. This generator emits the .razor + .razor.scss pair *and*
    a ready-to-paste partial scene snippet that wires both components onto the
    same GameObject with the correct GUIDs.

    Args:
        class_name: PascalCase name, e.g. "HudPanel".
        properties: Optional list of [Property] dicts (same shape as generate_razor).
        namespace: Optional namespace for the .razor.
        z_index: ScreenPanel ZIndex value (defaults to 100).
        opacity: ScreenPanel Opacity (defaults to 1.0).
        root_class: CSS class for root element (defaults to kebab-case).

    Returns:
        Dict with: filename, content, scss_filename, scss_content,
        scene_snippet (str - ready-to-paste GameObject JSON), class_name.
    """
    import json as _json
    import uuid as _uuid

    razor = generate_razor(
        class_name=class_name,
        inherits="PanelComponent",
        properties=properties,
        root_class=root_class,
        namespace=namespace,
    )

    screen_panel_guid = str(_uuid.uuid4())
    panel_comp_guid = str(_uuid.uuid4())
    object_guid = str(_uuid.uuid4())
    type_name = f"{namespace}.{class_name}" if namespace else class_name

    snippet_obj = {
        "__guid": object_guid,
        "Flags": 0,
        "Name": class_name,
        "Enabled": True,
        "Position": "0,0,0",
        "Rotation": "0,0,0,1",
        "Scale": "1,1,1",
        "Tags": "",
        "Components": [
            {
                "__guid": screen_panel_guid,
                "__type": "Sandbox.ScreenPanel",
                "ZIndex": z_index,
                "Opacity": opacity,
            },
            {
                "__guid": panel_comp_guid,
                "__type": type_name,
            },
        ],
        "Children": [],
    }
    scene_snippet = _json.dumps(snippet_obj, indent=2)

    return {
        "filename": razor["filename"],
        "content": razor["content"],
        "scss_filename": razor["scss_filename"],
        "scss_content": razor["scss_content"],
        "scene_snippet": scene_snippet,
        "class_name": class_name,
        "screen_panel_guid": screen_panel_guid,
        "panel_component_guid": panel_comp_guid,
        "object_guid": object_guid,
    }
