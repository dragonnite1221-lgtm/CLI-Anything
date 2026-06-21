# ruff: noqa: F403, F405, E501
from .test_orchestrator_base import *  # noqa: F403

# fmt: off
from .test_orchestrator_p1 import build_combo_matrix, cleanup_data_files, collect_screenshot, kill_sbox_process, poll_for_sentinel, swap_startup_scene, write_test_config  # noqa: E402,E501
# fmt: on


def run_single_combo(
    combo: Dict[str, Any],
    data_path: str,
    output_dir: str,
    sbproj_path: str,
    timeout: float = 60.0,
) -> Dict[str, Any]:
    """Run a single strategy/size/seed combo through s&box."""
    from cli_anything.sbox.utils import sbox_backend

    strategy = combo["strategy"]
    size = combo["size"]
    seed = combo["seed"]

    cleanup_data_files(data_path)
    write_test_config(data_path, strategy, size, seed)

    project_dir = os.path.dirname(sbproj_path)
    proc = sbox_backend.launch_editor(project_dir)

    try:
        sentinel = poll_for_sentinel(data_path, timeout)

        if sentinel is None:
            return {"success": False, "error": "timeout", "combo": combo}

        if not sentinel.get("success"):
            return {
                "success": False,
                "error": sentinel.get("error", "unknown error"),
                "combo": combo,
            }

        png_path = collect_screenshot(data_path, output_dir, strategy, size, seed)
        # If sentinel reported success but no screenshot was produced, surface
        # this as a failure rather than reporting a successful run with no PNG.
        if png_path is None:
            return {
                "success": False,
                "error": "screenshot files not produced (no metadata.json or rgba)",
                "combo": combo,
            }
        return {"success": True, "png_path": png_path, "combo": combo}

    finally:
        kill_sbox_process(proc)
        cleanup_data_files(data_path)


def run_test_pipeline(
    sbproj_path: str,
    data_path: str,
    output_dir: str,
    strategies: Optional[List[str]] = None,
    sizes: Optional[List[str]] = None,
    seeds: Optional[List[int]] = None,
    seed_count: int = 1,
    timeout: float = 60.0,
) -> List[Dict[str, Any]]:
    """Run the full test pipeline across all combos."""
    combos = build_combo_matrix(strategies, sizes, seeds, seed_count)

    previous_scene = swap_startup_scene(sbproj_path, "scenes/test_map.scene")

    results = []
    try:
        for i, combo in enumerate(combos):
            label = f"{combo['strategy']}/{combo['size']}/seed{combo['seed']}"
            print(f"[{i + 1}/{len(combos)}] Running {label}...")

            result = run_single_combo(
                combo, data_path, output_dir, sbproj_path, timeout
            )
            results.append(result)

            if result["success"]:
                print(f"  -> captured: {result['png_path']}")
            else:
                print(f"  -> FAILED: {result['error']}")
    finally:
        swap_startup_scene(sbproj_path, previous_scene)

    return results
