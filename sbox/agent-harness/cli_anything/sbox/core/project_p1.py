# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403


EDITORCONFIG_CONTENT = """\
root = true

[*]
indent_style = tab
indent_size = 4
end_of_line = crlf
insert_final_newline = true

[*.cs]
csharp_new_line_before_open_brace = all
csharp_space_between_method_declaration_parameter_list_parentheses = true
csharp_space_between_method_call_parameter_list_parentheses = true
csharp_space_after_keywords_in_control_flow_statements = true
csharp_preferred_modifier_order = public, private, protected, internal, static, extern, new, virtual, abstract, sealed, override, readonly, unsafe, volatile, async:suggestion
"""
CODE_ASSEMBLY_CS = """\
global using Sandbox;
global using System.Collections.Generic;
global using System.Linq;
"""
EDITOR_ASSEMBLY_CS = """\
global using Sandbox;
global using Editor;
global using System.Collections.Generic;
global using System.Linq;
"""
DEFAULT_INPUT_CONFIG: Dict[str, Any] = {
    "Actions": [
        {"Name": "Forward", "GroupName": "Movement", "Title": None, "KeyboardCode": "W", "GamepadCode": "None"},
        {"Name": "Backward", "GroupName": "Movement", "Title": None, "KeyboardCode": "S", "GamepadCode": "None"},
        {"Name": "Left", "GroupName": "Movement", "Title": None, "KeyboardCode": "A", "GamepadCode": "None"},
        {"Name": "Right", "GroupName": "Movement", "Title": None, "KeyboardCode": "D", "GamepadCode": "None"},
        {"Name": "Jump", "GroupName": "Movement", "Title": None, "KeyboardCode": "space", "GamepadCode": "A"},
        {"Name": "Run", "GroupName": "Movement", "Title": None, "KeyboardCode": "shift", "GamepadCode": "LeftJoystickButton"},
        {"Name": "Walk", "GroupName": "Movement", "Title": None, "KeyboardCode": "alt", "GamepadCode": "None"},
        {"Name": "Duck", "GroupName": "Movement", "Title": None, "KeyboardCode": "ctrl", "GamepadCode": "B"},
        {"Name": "Attack1", "GroupName": "Actions", "Title": "Primary Attack", "KeyboardCode": "mouse1", "GamepadCode": "RightTrigger"},
        {"Name": "Attack2", "GroupName": "Actions", "Title": "Secondary Attack", "KeyboardCode": "mouse2", "GamepadCode": "LeftTrigger"},
        {"Name": "Reload", "GroupName": "Actions", "Title": None, "KeyboardCode": "r", "GamepadCode": "X"},
        {"Name": "Use", "GroupName": "Actions", "Title": None, "KeyboardCode": "e", "GamepadCode": "Y"},
        {"Name": "Slot1", "GroupName": "Inventory", "Title": "Slot #1", "KeyboardCode": "1", "GamepadCode": "DpadWest"},
        {"Name": "Slot2", "GroupName": "Inventory", "Title": "Slot #2", "KeyboardCode": "2", "GamepadCode": "DpadEast"},
        {"Name": "Slot3", "GroupName": "Inventory", "Title": "Slot #3", "KeyboardCode": "3", "GamepadCode": "DpadSouth"},
        {"Name": "Slot4", "GroupName": "Inventory", "Title": "Slot #4", "KeyboardCode": "4", "GamepadCode": "None"},
        {"Name": "Slot5", "GroupName": "Inventory", "Title": "Slot #5", "KeyboardCode": "5", "GamepadCode": "None"},
        {"Name": "Slot6", "GroupName": "Inventory", "Title": "Slot #6", "KeyboardCode": "6", "GamepadCode": "None"},
        {"Name": "Slot7", "GroupName": "Inventory", "Title": "Slot #7", "KeyboardCode": "7", "GamepadCode": "None"},
        {"Name": "Slot8", "GroupName": "Inventory", "Title": "Slot #8", "KeyboardCode": "8", "GamepadCode": "None"},
        {"Name": "Slot9", "GroupName": "Inventory", "Title": "Slot #9", "KeyboardCode": "9", "GamepadCode": "None"},
        {"Name": "Slot0", "GroupName": "Inventory", "Title": "Slot #0", "KeyboardCode": "0", "GamepadCode": "None"},
        {"Name": "SlotPrev", "GroupName": "Inventory", "Title": "Previous Slot", "KeyboardCode": "mouse4", "GamepadCode": "SwitchLeftBumper"},
        {"Name": "SlotNext", "GroupName": "Inventory", "Title": "Next Slot", "KeyboardCode": "mouse5", "GamepadCode": "SwitchRightBumper"},
        {"Name": "View", "GroupName": "Other", "Title": None, "KeyboardCode": "C", "GamepadCode": "RightJoystickButton"},
        {"Name": "Voice", "GroupName": "Other", "Title": None, "KeyboardCode": "v", "GamepadCode": "None"},
        {"Name": "Drop", "GroupName": "Other", "Title": None, "KeyboardCode": "g", "GamepadCode": "None"},
        {"Name": "Flashlight", "GroupName": "Other", "Title": None, "KeyboardCode": "f", "GamepadCode": "DpadNorth"},
        {"Name": "Score", "GroupName": "Other", "Title": "Scoreboard", "KeyboardCode": "tab", "GamepadCode": "SwitchLeftMenu"},
        {"Name": "Menu", "GroupName": "Other", "Title": None, "KeyboardCode": "Q", "GamepadCode": "SwitchRightMenu"},
        {"Name": "Chat", "GroupName": "Other", "Title": None, "KeyboardCode": "enter", "GamepadCode": "None"},
    ],
    "__guid": str( uuid.uuid4() ),
    "__schema": "configdata",
    "__type": "InputSettings",
    "__version": 1,
}
DEFAULT_COLLISION_CONFIG: Dict[str, Any] = {
    "Version": 2,
    "Defaults": {
        "solid": "Collide",
        "world": "Collide",
        "trigger": "Trigger",
        "ladder": "Ignore",
        "water": "Trigger",
    },
    "Pairs": [
        {"a": "solid", "b": "solid", "r": "Collide"},
        {"a": "trigger", "b": "playerclip", "r": "Ignore"},
        {"a": "trigger", "b": "solid", "r": "Trigger"},
        {"a": "playerclip", "b": "solid", "r": "Collide"},
    ],
    "__guid": str( uuid.uuid4() ),
    "__schema": "configdata",
    "__type": "CollisionRules",
    "__version": 2,
}
def _default_minimal_scene() -> Dict[str, Any]:
    """Return a minimal scene structure with Sun, Skybox, Plane, and Camera."""
    # Import here to avoid circular dependency at module level
    from .scene import _build_default_objects

    scene: Dict[str, Any] = {
        "GameObjects": _build_default_objects(),
        "SceneProperties": {
            "FixedUpdateFrequency": 50,
            "MaxFixedUpdates": 5,
            "NetworkFrequency": 60,
            "NetworkInterpolation": True,
            "PhysicsSubSteps": 1,
            "ThreadedAnimation": True,
            "TimeScale": 1,
            "UseFixedUpdate": True,
        },
        "Title": "minimal",
        "Description": "",
        "ResourceVersion": 1,
        "__references": [],
        "__version": 1,
    }
    return scene
