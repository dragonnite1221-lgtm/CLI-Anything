# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers_base import *  # noqa: F403

# fmt: off
from .test_full_e2e_helpers_p1 import _subprocess_json  # noqa: E402,E501
# fmt: on


def _build_subprocess_point_project(
    command: list[str], tmp_path: Path, stem: str, env: dict[str, str]
) -> dict[str, str]:
    project_path = tmp_path / f"{stem}.qgz"

    _subprocess_json(
        command, ["project", "new", "-o", str(project_path), "--title", stem], env
    )
    layer = _subprocess_json(
        command,
        [
            "--project",
            str(project_path),
            "layer",
            "create-vector",
            "--name",
            "places",
            "--geometry",
            "point",
            "--field",
            "name:string",
            "--field",
            "score:int",
        ],
        env,
    )
    _subprocess_json(
        command,
        [
            "--project",
            str(project_path),
            "feature",
            "add",
            "--layer",
            "places",
            "--wkt",
            "POINT(116.397 39.907)",
            "--attr",
            "name=Beijing",
            "--attr",
            "score=5",
        ],
        env,
    )
    _subprocess_json(
        command,
        ["--project", str(project_path), "layout", "create", "--name", "Main"],
        env,
    )

    return {
        "project_path": str(project_path),
        "layer_source": layer["source"],
    }


__all__ = [
    "CliRunner",
    "PNG_SIGNATURE",
    "Path",
    "_PACKAGE_NAMESPACE_ROOT",
    "_build_cli_project",
    "_build_subprocess_point_project",
    "_build_subprocess_project",
    "_invoke_json",
    "_parse_json_output",
    "_resolve_cli",
    "_subprocess_json",
    "annotations",
    "backend",
    "clean_qgis_state",
    "cli",
    "json",
    "os",
    "project_mod",
    "pytest",
    "qgis_cli",
    "runner",
    "shutil",
    "subprocess",
    "sys",
]  # noqa: E501
