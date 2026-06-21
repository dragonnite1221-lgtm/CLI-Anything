# ruff: noqa: F403, F405, E501
from .input_config_base import *  # noqa: F403


def load_input_config( config_path: str ) -> dict:
    """Load Input.config JSON from disk.

    Args:
        config_path: Absolute path to the Input.config file.

    Returns:
        Parsed JSON dict.
    """
    with open( config_path, "r", encoding="utf-8" ) as f:
        return json.load( f )
def save_input_config( config_path: str, data: dict ) -> None:
    """Save Input.config JSON to disk.

    Args:
        config_path: Absolute path to the Input.config file.
        data: The full config dict to write.
    """
    with open( config_path, "w", encoding="utf-8" ) as f:
        json.dump( data, f, indent=2 )
        f.write( "\n" )
def list_actions( config_path: str ) -> list[dict]:
    """Return list of all input actions with their bindings.

    Args:
        config_path: Absolute path to the Input.config file.

    Returns:
        List of action dicts, each with Name, GroupName, Title,
        KeyboardCode, and GamepadCode.
    """
    data = load_input_config( config_path )
    return data.get( "Actions", [] )
def add_action(
    config_path: str,
    name: str,
    group: str = "Other",
    keyboard_code: str = "None",
    gamepad_code: str = "None",
    title: Optional[str] = None,
) -> dict:
    """Add a new input action.

    Args:
        config_path: Absolute path to the Input.config file.
        name: Action name, e.g. "Sprint".
        group: Group name, e.g. "Movement".
        keyboard_code: Keyboard binding, e.g. "W".
        gamepad_code: Gamepad binding, e.g. "A".
        title: Optional display title.

    Returns:
        The newly created action dict.
    """
    data = load_input_config( config_path )
    actions = data.get( "Actions", [] )

    # Avoid duplicates
    for action in actions:
        if action["Name"] == name:
            raise ValueError( f"Action '{name}' already exists" )

    new_action = {
        "Name": name,
        "GroupName": group,
        "Title": title,
        "KeyboardCode": keyboard_code,
        "GamepadCode": gamepad_code,
    }

    actions.append( new_action )
    data["Actions"] = actions
    save_input_config( config_path, data )
    return new_action
def remove_action( config_path: str, name: str ) -> bool:
    """Remove an input action by name.

    Args:
        config_path: Absolute path to the Input.config file.
        name: Action name to remove.

    Returns:
        True if the action was found and removed, False otherwise.
    """
    data = load_input_config( config_path )
    actions = data.get( "Actions", [] )
    original_len = len( actions )
    data["Actions"] = [a for a in actions if a["Name"] != name]

    if len( data["Actions"] ) < original_len:
        save_input_config( config_path, data )
        return True

    return False
