# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p2 import _new_guid  # noqa: E402,E501
from .scene_p5 import load_scene, save_scene  # noqa: E402,E501
from .scene_p6 import find_object  # noqa: E402,E501
# fmt: on


def instantiate_prefab(
    scene_path: str,
    prefab_path: str,
    name: Optional[str] = None,
    position: str = "0,0,0",
    rotation: str = "0,0,0,1",
    scale: str = "1,1,1",
    parent_guid: Optional[str] = None,
) -> str:
    """Insert a prefab reference into a scene as a new GameObject.

    Reads the prefab to derive a default name (from RootObject.Name) and
    creates a GameObject in the scene with a PrefabSource reference, fresh
    GUIDs, and the given transform.  The prefab is referenced (not deep-copied
    or "exploded").

    Args:
        scene_path: Path to the .scene file to mutate.
        prefab_path: Path to the .prefab file to instantiate. Stored as a
                     relative-to-Assets reference if it lives under Assets/.
        name: Optional override for the new GameObject's Name. Defaults to
              the prefab RootObject's Name.
        position, rotation, scale: Transform of the new object.
        parent_guid: Optional parent GameObject guid (otherwise added at root).

    Returns:
        The new GameObject's guid.
    """
    # Load the prefab to extract its name
    with open(prefab_path, "r", encoding="utf-8") as f:
        prefab_data = json.load(f)

    root = prefab_data.get("RootObject", {})
    default_name = root.get("Name", os.path.splitext(os.path.basename(prefab_path))[0])
    obj_name = name if name is not None else default_name

    # Compute a project-relative reference for PrefabSource
    abs_prefab = os.path.abspath(prefab_path)
    prefab_ref = abs_prefab.replace("\\", "/")
    norm_lower = prefab_ref.lower()
    if "/assets/" in norm_lower:
        idx = norm_lower.rindex("/assets/")
        prefab_ref = prefab_ref[idx + len("/assets/") :]

    data = load_scene(scene_path)

    # Build the GameObject with a PrefabSource pointer
    new_obj: Dict[str, Any] = {
        "__guid": _new_guid(),
        "Flags": 0,
        "Name": obj_name,
        "Enabled": True,
        "Position": position,
        "Rotation": rotation,
        "Scale": scale,
        "Tags": "",
        "PrefabSource": prefab_ref,
        "Components": [],
        "Children": [],
    }

    if parent_guid:
        parent = find_object(data, guid=parent_guid)
        if parent is None:
            raise ValueError(f"Parent object with guid '{parent_guid}' not found")
        parent.setdefault("Children", []).append(new_obj)
    else:
        data.setdefault("GameObjects", []).append(new_obj)

    save_scene(scene_path, data)
    return new_obj["__guid"]
