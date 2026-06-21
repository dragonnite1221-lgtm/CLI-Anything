# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers_base import *  # noqa: F403


def _resolve_cli(name: str) -> list[str]:
    """Resolve the CLI entry-point for subprocess tests.

    Prefers an installed command on PATH and falls back to ``python -m``
    unless ``CLI_ANYTHING_FORCE_INSTALLED=1`` is set.
    """
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    sibling = Path(sys.executable).parent / name
    if sibling.exists():
        print(f"[_resolve_cli] Using sibling command: {sibling}")
        return [str(sibling)]
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(
            f"{name} not found in PATH. Install with: python3 -m pip install -e ."
        )
    module = "cli_anything.qgis.qgis_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


@pytest.fixture(autouse=True)
def clean_qgis_state(monkeypatch, tmp_path):
    home_dir = tmp_path / "home"
    home_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(home_dir))
    monkeypatch.setenv(
        "QT_QPA_PLATFORM", os.environ.get("QT_QPA_PLATFORM", "offscreen")
    )

    backend.ensure_qgis_app()
    project = project_mod.current_project()
    project.clear()
    project.setFileName("")
    qgis_cli._session = None
    qgis_cli._json_output = False
    qgis_cli._repl_mode = False

    yield

    project.clear()
    project.setFileName("")
    qgis_cli._session = None
    qgis_cli._json_output = False
    qgis_cli._repl_mode = False


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def _parse_json_output(raw: str) -> dict:
    return json.loads(raw)


def _invoke_json(runner: CliRunner, args: list[str]) -> dict:
    result = runner.invoke(cli, ["--json", *args])
    assert result.exit_code == 0, result.output
    return _parse_json_output(result.output)


def _subprocess_json(command: list[str], args: list[str], env: dict[str, str]) -> dict:
    completed = subprocess.run(
        [*command, "--json", *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    return json.loads(completed.stdout)
