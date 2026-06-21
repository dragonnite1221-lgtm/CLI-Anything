# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers_base import *  # noqa: F403


def _find_compiler() -> str | None:
    for name in ("clang", "gcc", "cc"):
        path = shutil.which(name)
        if path:
            return path
    return None


@pytest.fixture(scope="session")
def lldb_test_exe(tmp_path_factory) -> str:
    compiler = _find_compiler()
    if not compiler:
        pytest.skip("No C compiler found for LLDB E2E helper build")

    build_dir = tmp_path_factory.mktemp("lldb-e2e")
    src = build_dir / "lldb_helper.c"
    src.write_text(HELPER_SOURCE, encoding="utf-8")

    exe_name = "lldb_helper.exe" if os.name == "nt" else "lldb_helper"
    exe_path = build_dir / exe_name

    cmd = [compiler, "-g", "-O0", str(src), "-o", str(exe_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        pytest.skip(f"Failed to build LLDB E2E helper: {result.stderr.strip()}")

    return str(exe_path)


@pytest.fixture()
def session_file(tmp_path) -> Path:
    return tmp_path / "lldb-session.json"


@pytest.fixture()
def core_file(tmp_path) -> str:
    if TEST_CORE and os.path.isfile(TEST_CORE):
        return TEST_CORE

    placeholder = tmp_path / "placeholder.core"
    placeholder.write_bytes(b"lldb-core-placeholder")
    return str(placeholder)


def _run_cli(
    *args, session_file: Path, input_text: str | None = None, timeout: int = 90
) -> dict:
    cmd = [
        sys.executable,
        "-m",
        "cli_anything.lldb.lldb_cli",
        "--json",
        "--session-file",
        str(session_file),
    ]
    cmd.extend(args)
    result = subprocess.run(
        cmd,
        input=input_text,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=HARNESS_ROOT,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"CLI failed ({' '.join(args)}): {result.stderr}\n{result.stdout}"
        )
    return json.loads(result.stdout)


def _close_session(session_file: Path):
    cmd = [
        sys.executable,
        "-m",
        "cli_anything.lldb.lldb_cli",
        "--json",
        "--session-file",
        str(session_file),
        "session",
        "close",
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=HARNESS_ROOT)


def _extract_address(payload: dict) -> str:
    for key in ("value", "summary"):
        value = payload.get(key)
        if isinstance(value, str):
            match = re.search(r"0x[0-9a-fA-F]+", value)
            if match:
                return match.group(0)
    raise AssertionError(f"Could not extract address from payload: {payload}")
