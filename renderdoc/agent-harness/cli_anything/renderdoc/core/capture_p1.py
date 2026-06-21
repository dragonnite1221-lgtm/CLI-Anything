# ruff: noqa: F403, F405, E501
from .capture_base import *  # noqa: F403


def _require_rd():
    if not HAS_RD:
        raise RuntimeError(
            "renderdoc Python module not available. "
            "Ensure RenderDoc is installed and its Python bindings are on PYTHONPATH."
        )


def _api_properties_summary(props: Any) -> Dict[str, Any]:
    """JSON-friendly subset of CaptureFile.APIProperties / GetAPIProperties."""
    out: Dict[str, Any] = {"api": str(props.pipelineType)}
    if hasattr(props, "degraded"):
        out["degraded"] = bool(props.degraded)
    driver = None
    for attr in ("localRenderer", "vendor"):
        if hasattr(props, attr):
            val = getattr(props, attr)
            if val is not None and str(val):
                driver = str(val)
                break
    out["driver"] = driver if driver is not None else str(props.pipelineType)
    return out


_replay_refcount = 0


def _ensure_replay_api():
    """Initialise RenderDoc replay once; pair with ``_release_replay_api`` per handle."""
    global _replay_refcount
    _require_rd()
    if _replay_refcount == 0:
        rd.InitialiseReplay(rd.GlobalEnvironment(), [])
    _replay_refcount += 1


def _release_replay_api():
    """Shut down replay when the last CaptureHandle in the process closes."""
    global _replay_refcount
    if not HAS_RD or _replay_refcount <= 0:
        return
    _replay_refcount -= 1
    if _replay_refcount == 0:
        rd.ShutdownReplay()
