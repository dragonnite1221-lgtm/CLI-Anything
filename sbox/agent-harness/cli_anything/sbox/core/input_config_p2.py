# ruff: noqa: F403, F405, E501
from .input_config_base import *  # noqa: F403
# fmt: off
from .input_config_p1 import load_input_config, save_input_config  # noqa: E402,E501
# fmt: on


def set_action(
    config_path: str,
    name: str,
    keyboard_code: Optional[str] = None,
    gamepad_code: Optional[str] = None,
    group: Optional[str] = None,
    title: Optional[str] = None,
) -> dict:
    """Modify an existing input action's bindings.

    Args:
        config_path: Absolute path to the Input.config file.
        name: Action name to modify.
        keyboard_code: New keyboard binding (or None to leave unchanged).
        gamepad_code: New gamepad binding (or None to leave unchanged).
        group: New group name (or None to leave unchanged).
        title: New display title (or None to leave unchanged).

    Returns:
        The updated action dict.

    Raises:
        KeyError: If the action does not exist.
    """
    data = load_input_config( config_path )
    actions = data.get( "Actions", [] )

    for action in actions:
        if action["Name"] == name:
            if keyboard_code is not None:
                action["KeyboardCode"] = keyboard_code
            if gamepad_code is not None:
                action["GamepadCode"] = gamepad_code
            if group is not None:
                action["GroupName"] = group
            if title is not None:
                action["Title"] = title

            save_input_config( config_path, data )
            return action

    raise KeyError( f"Action '{name}' not found" )
def get_default_input_config() -> dict:
    """Return the default s&box Input.config with standard FPS bindings.

    Returns:
        A complete Input.config dict ready to be saved.
    """
    return {
        "Actions": [
            # Movement
            {"Name": "Forward", "GroupName": "Movement", "Title": None, "KeyboardCode": "W", "GamepadCode": "None"},
            {"Name": "Backward", "GroupName": "Movement", "Title": None, "KeyboardCode": "S", "GamepadCode": "None"},
            {"Name": "Left", "GroupName": "Movement", "Title": None, "KeyboardCode": "A", "GamepadCode": "None"},
            {"Name": "Right", "GroupName": "Movement", "Title": None, "KeyboardCode": "D", "GamepadCode": "None"},
            {"Name": "Jump", "GroupName": "Movement", "Title": None, "KeyboardCode": "space", "GamepadCode": "A"},
            {"Name": "Run", "GroupName": "Movement", "Title": None, "KeyboardCode": "shift", "GamepadCode": "LeftJoystickButton"},
            {"Name": "Walk", "GroupName": "Movement", "Title": None, "KeyboardCode": "alt", "GamepadCode": "None"},
            {"Name": "Duck", "GroupName": "Movement", "Title": None, "KeyboardCode": "ctrl", "GamepadCode": "B"},
            # Actions
            {"Name": "Attack1", "GroupName": "Actions", "Title": "Primary Attack", "KeyboardCode": "mouse1", "GamepadCode": "RightTrigger"},
            {"Name": "Attack2", "GroupName": "Actions", "Title": "Secondary Attack", "KeyboardCode": "mouse2", "GamepadCode": "LeftTrigger"},
            {"Name": "Reload", "GroupName": "Actions", "Title": None, "KeyboardCode": "r", "GamepadCode": "X"},
            {"Name": "Use", "GroupName": "Actions", "Title": None, "KeyboardCode": "e", "GamepadCode": "Y"},
            # Inventory
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
            # Other
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
