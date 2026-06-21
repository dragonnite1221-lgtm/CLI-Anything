# ruff: noqa: F403, F405, E501
from .test_orchestrator_base import *  # noqa: F403


def resolve_data_path(sbox_install: str, project_ident: str) -> str:
    """Compute the FileSystem.Data physical path for a project."""
    data_path = os.path.join(sbox_install, "data", "local", f"{project_ident}#local")
    if not os.path.isdir(data_path):
        raise FileNotFoundError(
            f"FileSystem.Data directory not found at {data_path}. "
            f"Run s&box once to create it."
        )
    return data_path


def build_combo_matrix(
    strategies: Optional[List[str]] = None,
    sizes: Optional[List[str]] = None,
    seeds: Optional[List[int]] = None,
    seed_count: int = 1,
) -> List[Dict[str, Any]]:
    """Build the full test combo matrix."""
    use_strategies = strategies or ALL_STRATEGIES
    use_sizes = sizes or ALL_SIZES
    if seeds is None:
        seeds = [random.randint(1, 999999) for _ in range(seed_count)]

    combos = []
    for strategy in use_strategies:
        for size in use_sizes:
            for seed in seeds:
                combos.append({"strategy": strategy, "size": size, "seed": seed})
    return combos


def write_test_config(data_path: str, strategy: str, size: str, seed: int) -> str:
    """Write test_config.json to the FileSystem.Data directory.

    Note: Keys are PascalCase to match s&box Json.Deserialize<TestConfig>().
    """
    config = {"Strategy": strategy, "Size": size, "Seed": seed}
    config_path = os.path.join(data_path, "test_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f)
    return config_path


def cleanup_data_files(data_path: str) -> None:
    """Remove test pipeline files from FileSystem.Data."""
    for name in DATA_FILES:
        path = os.path.join(data_path, name)
        if os.path.exists(path):
            os.remove(path)


def check_sentinel(data_path: str) -> Optional[Dict[str, Any]]:
    """Check for test_complete.json sentinel file."""
    sentinel_path = os.path.join(data_path, "test_complete.json")
    if not os.path.exists(sentinel_path):
        return None
    with open(sentinel_path, encoding="utf-8") as f:
        return json.load(f)


def poll_for_sentinel(
    data_path: str, timeout: float = 60.0
) -> Optional[Dict[str, Any]]:
    """Poll for sentinel file with timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = check_sentinel(data_path)
        if result is not None:
            return result
        time.sleep(0.5)
    return None


def rgba_to_png(rgba_path: str, png_path: str, width: int, height: int) -> None:
    """Convert raw RGBA bytes to a PNG file using Pillow."""
    if not os.path.exists(rgba_path):
        raise FileNotFoundError(f"RGBA file not found: {rgba_path}")

    from PIL import Image

    with open(rgba_path, "rb") as f:
        raw_bytes = f.read()

    img = Image.frombytes("RGBA", (width, height), raw_bytes)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    img.save(png_path, "PNG")


def collect_screenshot(
    data_path: str, output_dir: str, strategy: str, size: str, seed: int
) -> Optional[str]:
    """Copy screenshot from FileSystem.Data to test-results, convert to PNG.

    Handles both WriteAllBytes (raw) and Base64 fallback outputs.
    """
    metadata_path = os.path.join(data_path, "metadata.json")
    rgba_path = os.path.join(data_path, "screenshot.rgba")
    b64_path = os.path.join(data_path, "screenshot.rgba.b64")

    if not os.path.exists(metadata_path):
        return None

    with open(metadata_path, encoding="utf-8") as f:
        metadata = json.load(f)

    width = metadata.get("renderWidth", 2048)
    height = metadata.get("renderHeight", 2048)

    filename = f"{strategy.lower()}-{size.lower()}-seed{seed}.png"
    png_path = os.path.join(output_dir, "screenshots", filename)

    if os.path.exists(rgba_path):
        rgba_to_png(rgba_path, png_path, width, height)
    elif os.path.exists(b64_path):
        import base64
        from PIL import Image

        with open(b64_path, "r", encoding="utf-8") as f:
            raw_bytes = base64.b64decode(f.read())
        img = Image.frombytes("RGBA", (width, height), raw_bytes)
        os.makedirs(os.path.dirname(png_path), exist_ok=True)
        img.save(png_path, "PNG")
    else:
        return None

    meta_dest = os.path.join(
        output_dir,
        "screenshots",
        f"{strategy.lower()}-{size.lower()}-seed{seed}.metadata.json",
    )
    shutil.copy2(metadata_path, meta_dest)

    return png_path


def kill_sbox_process(proc: subprocess.Popen) -> None:
    """Kill an s&box process and its children."""
    if proc.poll() is not None:
        return

    proc.kill()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            capture_output=True,
        )


def swap_startup_scene(sbproj_path: str, scene: str) -> str:
    """Swap the StartupScene in a .sbproj file. Returns the previous value."""
    from cli_anything.sbox.core import project as project_mod

    info = project_mod.get_project_info(sbproj_path)
    previous = info.get("startup_scene", "scenes/minimal.scene")
    project_mod.configure_project(sbproj_path, startup_scene=scene)
    return previous
