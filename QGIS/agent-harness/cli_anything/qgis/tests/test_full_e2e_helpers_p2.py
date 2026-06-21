# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers_base import *  # noqa: F403

# fmt: off
from .test_full_e2e_helpers_p1 import _invoke_json, runner  # noqa: E402,E501
# fmt: on


def _build_cli_project(runner: CliRunner, tmp_path: Path, stem: str) -> dict[str, str]:
    project_path = tmp_path / f"{stem}.qgz"

    _invoke_json(runner, ["project", "new", "-o", str(project_path), "--title", stem])
    layer = _invoke_json(
        runner,
        [
            "--project",
            str(project_path),
            "layer",
            "create-vector",
            "--name",
            "areas",
            "--geometry",
            "polygon",
            "--field",
            "name:string",
            "--field",
            "score:int",
        ],
    )
    _invoke_json(
        runner,
        [
            "--project",
            str(project_path),
            "feature",
            "add",
            "--layer",
            "areas",
            "--wkt",
            "POLYGON((0 0,0 5,5 5,5 0,0 0))",
            "--attr",
            "name=ZoneA",
            "--attr",
            "score=5",
        ],
    )
    _invoke_json(
        runner, ["--project", str(project_path), "layout", "create", "--name", "Main"]
    )
    _invoke_json(
        runner,
        [
            "--project",
            str(project_path),
            "layout",
            "add-map",
            "--layout",
            "Main",
            "--x",
            "10",
            "--y",
            "20",
            "--width",
            "180",
            "--height",
            "120",
        ],
    )
    _invoke_json(
        runner,
        [
            "--project",
            str(project_path),
            "layout",
            "add-label",
            "--layout",
            "Main",
            "--text",
            "Demo map",
            "--x",
            "10",
            "--y",
            "8",
            "--width",
            "100",
            "--height",
            "10",
        ],
    )

    return {
        "project_path": str(project_path),
        "layer_source": layer["source"],
    }
