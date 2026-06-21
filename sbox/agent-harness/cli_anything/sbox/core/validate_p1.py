# ruff: noqa: F403, F405, E501
from .validate_base import *  # noqa: F403


def _build_asset_index(project_dir: str) -> Tuple[Set[str], Set[str]]:
    """Index project assets by normalized path and by extension-less stem.

    Returns (full_paths, stems) - both sets of normalized strings.
    """
    full_paths: Set[str] = set()
    stems: Set[str] = set()
    for asset in export_mod.list_assets(project_dir, asset_type="all"):
        rel = asset["path"].replace("\\", "/").lower()
        full_paths.add(rel)
        stem, _ = os.path.splitext(rel)
        if stem:
            stems.add(stem)
    return full_paths, stems


def _is_engine_builtin(ref: str) -> bool:
    """Whether a ref points to an engine-shipped asset (not in the project's Assets/).

    Heuristic: refs starting with these prefixes ship with s&box itself.
    """
    lower = ref.lower().lstrip("/")
    builtins = (
        "models/dev/",
        "materials/dev/",
        "materials/default",
        "materials/skybox/",
        "textures/dev/",
        "textures/cubemaps/",
        "fonts/",
        "particles/dev/",
        "sounds/ui/",
    )
    return any(lower.startswith(prefix) for prefix in builtins)


def _check_refs_against_index(
    refs_by_category: Dict[str, List[str]],
    full_paths: Set[str],
    stems: Set[str],
) -> List[str]:
    """Return broken refs (those missing from the project asset index)."""
    broken: List[str] = []
    for category, paths in refs_by_category.items():
        for ref in paths:
            norm = ref.replace("\\", "/").lower()
            if norm.startswith("assets/"):
                norm = norm[len("assets/") :]
            if norm in full_paths or norm in stems:
                continue
            if _is_engine_builtin(ref):
                continue
            broken.append(ref)
    return broken


def _collect_guids(
    objects: List[Dict[str, Any]], collected: Dict[str, List[str]], context: str
) -> None:
    """Walk objects collecting all __guid values mapped to source contexts."""
    for obj in objects:
        guid = obj.get("__guid")
        if guid:
            collected.setdefault(guid, []).append(
                f"{context}:GameObject:{obj.get('Name', '?')}"
            )
        for comp in obj.get("Components", []):
            cguid = comp.get("__guid")
            if cguid:
                collected.setdefault(cguid, []).append(
                    f"{context}:Component:{comp.get('__type', '?')}"
                )
        children = obj.get("Children", [])
        if children:
            _collect_guids(children, collected, context)
