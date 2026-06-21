# ruff: noqa: F403, F405, E501
from .unrealinsights_backend_base import *  # noqa: F403

# fmt: off
from .unrealinsights_backend_p1 import _build_resolution, _candidate_binary_paths, _missing_resolution, resolve_binary_from_engine_root, resolve_engine_root  # noqa: E402,E501
# fmt: on


def resolve_windows_binary(
    binary_name: str,
    explicit_path: str | None = None,
    env_var_name: str | None = None,
    search_roots: Iterable[Path] | None = None,
    required: bool = True,
) -> dict[str, object]:
    """Resolve a UE program binary using explicit path, env var, then auto-discovery."""
    if explicit_path:
        explicit = Path(explicit_path).expanduser()
        if not explicit.is_file():
            raise RuntimeError(f"Explicit path does not exist: {explicit}")
        return _build_resolution(explicit.resolve(), "explicit")

    if env_var_name:
        env_value = os.environ.get(env_var_name, "").strip()
        if env_value:
            env_path = Path(env_value).expanduser()
            if not env_path.is_file():
                raise RuntimeError(
                    f"{env_var_name} points to a missing file: {env_path}"
                )
            return _build_resolution(env_path.resolve(), f"env:{env_var_name}")

    for candidate in _candidate_binary_paths(binary_name, search_roots):
        if candidate.is_file():
            return _build_resolution(
                candidate.resolve(), f"auto:{candidate.parents[3].name}"
            )

    if required:
        raise RuntimeError(
            f"{binary_name} not found. Set an explicit path or install UE 5.5+ in an Epic Games directory."
        )
    return _missing_resolution(
        binary_name, "auto-discovery did not find a matching UE install"
    )


def resolve_unrealinsights_exe(
    explicit_path: str | None = None,
    engine_root: str | None = None,
    search_roots: Iterable[Path] | None = None,
    required: bool = True,
) -> dict[str, object]:
    if engine_root:
        return resolve_binary_from_engine_root(
            INSIGHTS_BINARY_NAME, engine_root, required=required
        )
    return resolve_windows_binary(
        INSIGHTS_BINARY_NAME,
        explicit_path=explicit_path,
        env_var_name="UNREALINSIGHTS_EXE",
        search_roots=search_roots,
        required=required,
    )


def resolve_trace_server_exe(
    explicit_path: str | None = None,
    engine_root: str | None = None,
    search_roots: Iterable[Path] | None = None,
    required: bool = False,
) -> dict[str, object]:
    if engine_root:
        return resolve_binary_from_engine_root(
            TRACE_SERVER_BINARY_NAME, engine_root, required=required
        )
    return resolve_windows_binary(
        TRACE_SERVER_BINARY_NAME,
        explicit_path=explicit_path,
        env_var_name="UNREAL_TRACE_SERVER_EXE",
        search_roots=search_roots,
        required=required,
    )


def ensure_parent_dir(path: str | Path):
    Path(path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


def build_engine_program(
    engine_root: str | Path,
    target_name: str,
    *,
    platform: str = "Win64",
    configuration: str = "Development",
    timeout: float | None = None,
    log_path: str | None = None,
) -> dict[str, object]:
    """Build a UE program target using the engine's Build.bat."""
    root = resolve_engine_root(engine_root)
    build_bat = root / "Engine" / "Build" / "BatchFiles" / "Build.bat"
    if not build_bat.is_file():
        raise RuntimeError(f"Build.bat not found under engine root: {root}")

    if log_path is None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_path = str(
            root
            / "Engine"
            / "Programs"
            / target_name
            / "Saved"
            / "Logs"
            / f"build-{target_name}-{timestamp}.log"
        )
    ensure_parent_dir(log_path)

    command = [str(build_bat), target_name, platform, configuration, "-WaitMutex"]
    try:
        result = subprocess.run(
            command,
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        exit_code = None
        timed_out = True

    Path(log_path).write_text(
        "\n".join(
            [
                f"# Command: {' '.join(command)}",
                "",
                stdout or "",
                stderr or "",
            ]
        ),
        encoding="utf-8",
        errors="replace",
    )

    return {
        "command": command,
        "cwd": str(root),
        "log_path": str(Path(log_path).resolve()),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "stdout": stdout,
        "stderr": stderr,
        "succeeded": (not timed_out and exit_code == 0),
    }
