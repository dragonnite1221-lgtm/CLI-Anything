# ruff: noqa: F403, F405, E501
from .sbox_backend_base import *  # noqa: F403

# fmt: off
from .sbox_backend_p1 import find_executable  # noqa: E402,E501
# fmt: on


def launch_server(
    game_ident: str,
    map_ident: Optional[str] = None,
) -> subprocess.Popen:
    """Launch sbox-server.exe (dedicated server) with a game.

    Args:
        game_ident: Game identifier string (e.g. 'org.gamename').
        map_ident: Optional map identifier to load.

    Returns:
        subprocess.Popen object for the launched server process.

    Raises:
        RuntimeError: If sbox-server.exe cannot be found.
    """
    exe = find_executable("sbox-server")
    cmd: List[str] = [exe, "-game", game_ident]

    if map_ident is not None:
        cmd.extend(["-map", map_ident])

    return subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def run_resource_compiler(
    asset_path: str,
    sbox_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Run resourcecompiler.exe on an asset file.

    Args:
        asset_path: Path to the asset file to compile.
        sbox_path: Optional explicit s&box installation path.
                   If None, auto-detected.

    Returns:
        Dict with keys:
        - 'success': bool
        - 'return_code': int
        - 'stdout': str
        - 'stderr': str
        - 'asset_path': str (absolute path of the input asset)
        - 'compiler_path': str (path of the compiler used)
    """
    if sbox_path is not None:
        compiler = os.path.join(sbox_path, EXECUTABLES["resourcecompiler"])
        if not os.path.isfile(compiler):
            raise RuntimeError(f"Resource compiler not found at {compiler}")
    else:
        compiler = find_executable("resourcecompiler")

    resolved_asset = os.path.abspath(asset_path)
    if not os.path.isfile(resolved_asset):
        raise FileNotFoundError(f"Asset file does not exist: {resolved_asset}")

    result = subprocess.run(
        [compiler, resolved_asset],
        capture_output=True,
        text=True,
        timeout=120,
    )

    return {
        "success": result.returncode == 0,
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "asset_path": resolved_asset,
        "compiler_path": compiler,
    }
