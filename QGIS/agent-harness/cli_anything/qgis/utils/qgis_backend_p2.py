# ruff: noqa: F403, F405, E501
from .qgis_backend_base import *  # noqa: F403

# fmt: off
from .qgis_backend_p1 import QgisProcessError, _extract_payload_message, find_qgis_process, project_path_argument  # noqa: E402,E501
# fmt: on


def run_process_json(
    arguments: list[str],
    *,
    project_path: str | None = None,
    parameters: list[str] | None = None,
) -> dict[str, Any]:
    """Run qgis_process in JSON mode and return parsed output."""
    command = [find_qgis_process(), "--json", *arguments]
    project_arg = project_path_argument(project_path)
    if project_arg:
        command.append(project_arg)
    if parameters:
        command.append("--")
        command.extend(parameters)

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    payload: dict[str, Any] | None = None

    if stdout:
        try:
            parsed = json.loads(stdout)
            if isinstance(parsed, dict):
                payload = parsed
            else:
                payload = {"data": parsed}
        except json.JSONDecodeError:
            payload = None

    if completed.returncode != 0:
        message = (
            _extract_payload_message(payload)
            or stderr
            or stdout
            or (f"qgis_process exited with status {completed.returncode}")
        )
        raise QgisProcessError(
            message,
            command=command,
            returncode=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            payload=payload,
        )

    if payload is None:
        raise QgisProcessError(
            "qgis_process returned non-JSON output in --json mode",
            command=command,
            returncode=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            payload=None,
        )

    return payload


def list_algorithms() -> dict[str, Any]:
    """Return the raw qgis_process list payload."""
    return run_process_json(["list"])


def help_algorithm(algorithm_id: str) -> dict[str, Any]:
    """Return the raw qgis_process help payload for an algorithm."""
    return run_process_json(["help", algorithm_id])


def run_algorithm(
    algorithm_id: str,
    *,
    parameters: list[str] | None = None,
    project_path: str | None = None,
) -> dict[str, Any]:
    """Run a qgis_process algorithm and return the raw JSON payload."""
    return run_process_json(
        ["run", algorithm_id],
        project_path=project_path,
        parameters=parameters,
    )
