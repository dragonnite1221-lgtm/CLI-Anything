# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403


ASSET_REF_EXTENSIONS = (
    ".vmdl",
    ".vmat",
    ".vsnd",
    ".sound",
    ".vtex",
    ".vpcf",
    ".prefab",
    ".scene",
    ".vanmgrph",
    ".animgraph",
    ".shader",
)
_ASSET_PATH_FIELDS = {
    "Model",
    "Material",
    "MaterialOverride",
    "SkyMaterial",
    "Texture",
    "Sound",
    "Prefab",
    "PrefabSource",
    "TargetPrefab",
}


def _is_asset_ref(value: str) -> bool:
    """Return True if *value* looks like an asset path."""
    if not isinstance(value, str) or not value:
        return False
    lower = value.lower()
    return any(lower.endswith(ext) for ext in ASSET_REF_EXTENSIONS)


def _category_for_ref(ref: str, field: str = "") -> str:
    """Map an asset reference to a category bucket."""
    lower = ref.lower()
    if lower.endswith(".vmdl"):
        return "models"
    if lower.endswith(".vmat"):
        return "materials"
    if lower.endswith(".vsnd") or lower.endswith(".sound"):
        return "sounds"
    if lower.endswith(".vtex"):
        return "textures"
    if lower.endswith(".vpcf"):
        return "particles"
    if lower.endswith(".prefab"):
        return "prefabs"
    if lower.endswith(".scene"):
        return "scenes"
    if lower.endswith(".animgraph") or lower.endswith(".vanmgrph"):
        return "animgraphs"
    if lower.endswith(".shader"):
        return "shaders"
    if field == "Model":
        return "models"
    if field in ("Material", "MaterialOverride", "SkyMaterial"):
        return "materials"
    if field == "Texture":
        return "textures"
    if field == "Sound":
        return "sounds"
    if field in ("Prefab", "PrefabSource", "TargetPrefab"):
        return "prefabs"
    return "other"


def _walk_for_refs(
    node: Any, refs: Dict[str, List[str]], path_stack: List[str]
) -> None:
    """Recursively walk a JSON tree, recording asset references by category.

    Each detected reference is stored under its asset-extension key, with the
    JSON breadcrumb path indicating where it was found.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            new_stack = path_stack + [str(key)]
            if isinstance(value, str):
                hit = None
                if _is_asset_ref(value):
                    hit = value
                elif key in _ASSET_PATH_FIELDS and value.strip():
                    hit = value
                if hit:
                    # Categorize by extension if present, else by field
                    category = _category_for_ref(hit, key)
                    refs.setdefault(category, []).append(hit)
            else:
                _walk_for_refs(value, refs, new_stack)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            _walk_for_refs(item, refs, path_stack + [f"[{i}]"])
