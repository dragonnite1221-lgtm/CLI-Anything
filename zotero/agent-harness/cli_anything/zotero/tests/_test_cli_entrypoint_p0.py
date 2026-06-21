# ruff: noqa: F403, F405, E501
from ._test_cli_entrypoint_base import *  # noqa: F403


def resolve_cli() -> list[str]:
    force_installed = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    installed = shutil.which("cli-anything-zotero")
    if installed:
        return [installed]
    scripts_dir = Path(sysconfig.get_path("scripts"))
    for candidate in (scripts_dir / "cli-anything-zotero.exe", scripts_dir / "cli-anything-zotero"):
        if candidate.exists():
            return [str(candidate)]
    if force_installed:
        raise RuntimeError("cli-anything-zotero not found in PATH. Install it with: py -m pip install -e .")
    return [sys.executable, "-m", "cli_anything.zotero"]


def uses_module_fallback(cli_base: list[str]) -> bool:
    return len(cli_base) >= 3 and cli_base[1] == "-m"
