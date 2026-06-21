# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403
# fmt: off
from .project_p3 import get_project_info, load_project, save_project  # noqa: E402,E501
# fmt: on


def configure_project(sbproj_path: str, **kwargs: Any) -> Dict[str, Any]:
    """Update project metadata fields.

    Accepts: title, max_players, min_players, tick_rate, network_type,
    startup_scene, map_list, map_select, org, ident, etc.

    Returns updated project info dict.
    """
    data = load_project(sbproj_path)
    meta = data.setdefault("Metadata", {})

    # Top-level fields
    top_level_map = {
        "title": "Title",
        "org": "Org",
        "ident": "Ident",
        "type": "Type",
    }
    for kwarg_key, json_key in top_level_map.items():
        if kwarg_key in kwargs:
            data[json_key] = kwargs[kwarg_key]

    # Metadata fields
    meta_map = {
        "max_players": "MaxPlayers",
        "min_players": "MinPlayers",
        "tick_rate": "TickRate",
        "network_type": "GameNetworkType",
        "map_select": "MapSelect",
        "map_list": "MapList",
        "startup_scene": "StartupScene",
    }
    for kwarg_key, json_key in meta_map.items():
        if kwarg_key in kwargs:
            meta[json_key] = kwargs[kwarg_key]

    save_project(sbproj_path, data)
    return get_project_info(sbproj_path)
def add_package( sbproj_path: str, package_ref: str ) -> Dict[str, Any]:
    """Add a package reference to the project.

    Args:
        sbproj_path: Path to the .sbproj file.
        package_ref: Package identifier (e.g. "facepunch.libsdf", "org.package").

    Returns:
        Updated project info dict.

    Raises:
        ValueError: If the package is already referenced.
    """
    data = load_project( sbproj_path )
    refs = data.get( "PackageReferences", [] ) or []

    if package_ref in refs:
        raise ValueError( f"Package '{package_ref}' is already referenced" )

    refs.append( package_ref )
    data["PackageReferences"] = refs
    save_project( sbproj_path, data )

    return get_project_info( sbproj_path )
def remove_package( sbproj_path: str, package_ref: str ) -> Dict[str, Any]:
    """Remove a package reference from the project.

    Returns:
        Updated project info dict.

    Raises:
        ValueError: If the package is not found.
    """
    data = load_project( sbproj_path )
    refs = data.get( "PackageReferences", [] ) or []

    if package_ref not in refs:
        raise ValueError( f"Package '{package_ref}' not found in references" )

    refs.remove( package_ref )
    data["PackageReferences"] = refs
    save_project( sbproj_path, data )

    return get_project_info( sbproj_path )
def find_sbproj(directory: str) -> Optional[str]:
    """Find .sbproj file in a directory. Returns path or None."""
    if not os.path.isdir(directory):
        return None
    for entry in os.listdir(directory):
        if entry.endswith(".sbproj"):
            return os.path.join(directory, entry)
    return None
