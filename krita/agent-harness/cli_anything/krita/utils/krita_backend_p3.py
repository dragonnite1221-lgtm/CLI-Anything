# ruff: noqa: F403, F405, E501
from .krita_backend_base import *  # noqa: F403

# fmt: off
from .krita_backend_p1 import _run, _write_temp_script, find_krita  # noqa: E402,E501
# fmt: on


def run_script(
    script_content: str,
    *,
    input_path: Optional[str | Path] = None,
    timeout: int = 300,
) -> Dict[str, Any]:
    """Execute a Python script inside Krita's embedded interpreter.

    This writes *script_content* to a temporary file and invokes Krita with
    ``--script <path>``.

    Parameters:
        script_content: Python source code to run.
        input_path: Optional document to open before the script runs.
        timeout: Maximum seconds to wait.

    Returns:
        Result dict.
    """
    krita = find_krita()
    script_path = _write_temp_script(script_content)

    try:
        args = [krita, "--script", script_path]
        if input_path is not None:
            args.append(str(Path(input_path).resolve()))
        result = _run(args, timeout=timeout)
        result["script_path"] = script_path
        return result
    finally:
        # Best-effort cleanup; leave the file if removal fails so the
        # caller can inspect it.
        try:
            os.unlink(script_path)
        except OSError:
            pass
