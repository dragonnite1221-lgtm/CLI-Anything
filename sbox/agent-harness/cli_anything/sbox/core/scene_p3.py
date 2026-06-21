# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p2 import _new_guid  # noqa: E402,E501
# fmt: on


def _make_game_object(
    name: str,
    position: str = "0,0,0",
    rotation: str = "0,0,0,1",
    scale: str = "1,1,1",
    tags: str = "",
    components: Optional[List[Dict[str, Any]]] = None,
    children: Optional[List[Dict[str, Any]]] = None,
    flags: int = 0,
    enabled: bool = True,
) -> Dict[str, Any]:
    """Build a GameObject dict."""
    obj: Dict[str, Any] = {
        "__guid": _new_guid(),
        "Flags": flags,
        "Name": name,
        "Enabled": enabled,
        "Position": position,
        "Rotation": rotation,
        "Scale": scale,
        "Tags": tags,
        "Components": components if components else [],
        "Children": children if children else [],
    }
    return obj
