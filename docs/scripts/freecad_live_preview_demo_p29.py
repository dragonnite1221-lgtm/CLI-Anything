# ruff: noqa: F403, F405, E501
from .freecad_live_preview_demo_base import *  # noqa: F403
# fmt: off
from .freecad_live_preview_demo_p1 import FREECAD_CLI, FREECAD_WORKDIR  # noqa: E402,E501
from .freecad_live_preview_demo_p2 import _taipei_101_steps  # noqa: E402,E501
from .freecad_live_preview_demo_p24 import _mod_cg0_0  # noqa: E402,E501
from .freecad_live_preview_demo_p26 import _mod_cg0_1, _mod_cg1_0  # noqa: E402,E501
from .freecad_live_preview_demo_p27 import _mod_cg2_0  # noqa: E402,E501
from .freecad_live_preview_demo_p28 import _mod_cg2_1  # noqa: E402,E501
# fmt: on


def _mod_cg2_2():
    return [
        {
                "id": "mast-upper",
                "label": "Add upper antenna mast",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "cylinder",
                    "--name",
                    "MastUpper",
                    "-P",
                    "radius=1.3",
                    "-P",
                    "height=12",
                    "-pos",
                    "0,0,140",
                ],
                "wait_preview": True,
            },
        {
                "id": "spire-tip",
                "label": "Add spire tip",
                "argv": [
                    "-p",
                    "{project_path}",
                    "part",
                    "add",
                    "cone",
                    "--name",
                    "SpireTip",
                    "-P",
                    "radius1=2.0",
                    "-P",
                    "radius2=0.2",
                    "-P",
                    "height=10",
                    "-pos",
                    "0,0,152",
                ],
                "wait_preview": True,
            },
    ]
def _mod_cg1_1():
    return {
        "steps": (_mod_cg2_0() + _mod_cg2_1() + _mod_cg2_2()),
    }
def _mod_cg0_2():
    return {
        "empire-state-building": {**_mod_cg1_0(), **_mod_cg1_1()},
    }
def _mod_cg0_3():
    return {
        "taipei-101": {
        "title": "Taipei 101",
        "subtitle": "tiny stacked-shoulder skyscraper model built with cli-anything-freecad",
        "project_name": "Taipei101",
        "project_file": "taipei_101.json",
        "steps": _taipei_101_steps(),
    },
    }
SCENARIOS: Dict[str, Dict[str, Any]] = {**_mod_cg0_0(), **_mod_cg0_1(), **_mod_cg0_2(), **_mod_cg0_3()}
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
def get_scenario(name: str) -> Dict[str, Any]:
    try:
        return SCENARIOS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown scenario: {name!r}. Available: {', '.join(sorted(SCENARIOS))}") from exc
def ensure_clean_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)
def write_json(path: Path, payload: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return path
def shlex_quote(value: str) -> str:
    if not value or any(c in value for c in " \t\n\"'`$&|;()[]{}<>"):
        return "'" + value.replace("'", "'\"'\"'") + "'"
    return value
def format_cmd(argv: List[str]) -> str:
    return " ".join(shlex_quote(arg) for arg in argv)
def run_cli(argv: List[str], *, timeout: int = 300) -> Dict[str, Any]:
    cmd = [FREECAD_CLI, "--json"] + argv
    started = time.time()
    proc = subprocess.run(
        cmd,
        cwd=FREECAD_WORKDIR,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    finished = time.time()
    payload: Dict[str, Any] = {
        "argv": cmd,
        "display_cmd": format_cmd(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "started_at": started,
        "finished_at": finished,
        "duration_s": round(finished - started, 3),
    }
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed: {payload['display_cmd']}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    try:
        payload["json"] = json.loads(proc.stdout) if proc.stdout.strip() else None
    except json.JSONDecodeError:
        payload["json"] = None
    return payload
def _load_motion_module():
    if str(FREECAD_WORKDIR) not in sys.path:
        sys.path.insert(0, str(FREECAD_WORKDIR))
    from cli_anything.freecad.core import motion as motion_mod

    return motion_mod
def _is_noop_alignment(result: Dict[str, Any]) -> bool:
    """Return True when a part-align command produced no placement delta."""
    payload = result.get("json") or {}
    delta = payload.get("delta")
    if not isinstance(delta, dict):
        return False
    try:
        return all(abs(float(delta.get(axis, 0.0))) <= 1e-9 for axis in ("x", "y", "z"))
    except (TypeError, ValueError):
        return False
