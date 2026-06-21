# ruff: noqa: F403, F405, E501
from .prefab_base import *  # noqa: F403


def _new_guid() -> str:
    """Generate a new UUID v4 string."""
    return str(uuid.uuid4())


def _write_json(path: str, data: Dict[str, Any]) -> None:
    """Write data as formatted JSON to path."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _build_root_object(
    name: str,
    components: Optional[List[Dict[str, Any]]] = None,
    children: Optional[List[Dict[str, Any]]] = None,
    network_mode: int = 0,
    network_transmit: bool = True,
    flags: int = 0,
) -> Dict[str, Any]:
    """Build a RootObject dict for a prefab."""
    resolved_components: List[Dict[str, Any]] = []
    if components:
        for comp in components:
            if isinstance(comp, str):
                # Treat as a preset name
                resolved_components.append(scene_mod._make_component(comp))
            elif isinstance(comp, dict):
                c = dict(comp)
                if "__guid" not in c:
                    c["__guid"] = _new_guid()
                resolved_components.append(c)

    resolved_children: List[Dict[str, Any]] = []
    if children:
        for child in children:
            if isinstance(child, dict):
                c = dict(child)
                if "__guid" not in c:
                    c["__guid"] = _new_guid()
                resolved_children.append(c)

    root: Dict[str, Any] = {
        "__guid": _new_guid(),
        "Flags": flags,
        "Name": name,
        "Enabled": True,
        "NetworkMode": network_mode,
        "NetworkInterpolation": True,
        "GizmoPersistence": 0,
        "RenderDirty": False,
        "Components": resolved_components,
        "Children": resolved_children,
    }

    if network_transmit:
        root["NetworkOrphaned"] = 1

    return root


def create_prefab(
    name: str,
    output_path: Optional[str] = None,
    components: Optional[List[Dict[str, Any]]] = None,
    children: Optional[List[Dict[str, Any]]] = None,
    network_mode: int = 0,
    network_transmit: bool = True,
) -> Dict[str, Any]:
    """Create a new .prefab file with given components and children.

    *components* can be a list of component dicts (with ``__type``) or
    preset name strings (resolved via ``scene.COMPONENT_PRESETS``).

    *children* is a list of child GameObject dicts.

    Returns the full prefab data dict.
    """
    root_object = _build_root_object(
        name=name,
        components=components,
        children=children,
        network_mode=network_mode,
        network_transmit=network_transmit,
    )

    prefab: Dict[str, Any] = {
        "RootObject": root_object,
        "SceneProperties": {},
        "ResourceVersion": 1,
        "__references": [],
        "__version": 1,
    }

    if output_path:
        _write_json(output_path, prefab)

    return prefab


def load_prefab(prefab_path: str) -> Dict[str, Any]:
    """Load and return parsed prefab JSON."""
    with open(prefab_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_prefab(prefab_path: str, data: Dict[str, Any]) -> None:
    """Save prefab JSON."""
    _write_json(prefab_path, data)
