# ruff: noqa: F403, F405, E501
from .qgis_backend_base import *  # noqa: F403


class QgisBackendError(RuntimeError):
    """Base error raised by the QGIS backend wrapper."""


class QgisProcessError(QgisBackendError):
    """Raised when qgis_process fails."""

    def __init__(
        self,
        message: str,
        *,
        command: list[str],
        returncode: int,
        stdout: str,
        stderr: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.payload = payload


def _normalize_path(path: str | os.PathLike[str]) -> str:
    return str(Path(path).expanduser().resolve())


def _detect_qgis_prefix() -> str:
    prefix = os.environ.get("QGIS_PREFIX_PATH")
    if prefix:
        return prefix

    for binary in ("qgis_process", "qgis"):
        found = shutil.which(binary)
        if found:
            return str(Path(found).resolve().parent.parent)

    return "/usr"


def find_qgis_process() -> str:
    """Return the qgis_process executable path or raise a clear error."""
    path = shutil.which("qgis_process")
    if path:
        return path
    raise QgisBackendError(
        "qgis_process is not installed or not available in PATH. Install QGIS and ensure "
        "the qgis_process command is available. Example: apt install qgis"
    )


def _is_shadow_qgis_module(module: Any) -> bool:
    shadow_package = Path(__file__).resolve().parents[1]

    module_file = getattr(module, "__file__", "") or ""
    if module_file:
        try:
            if Path(module_file).resolve().is_relative_to(shadow_package):
                return True
        except OSError:
            pass

    module_paths = getattr(module, "__path__", None) or []
    for item in module_paths:
        try:
            if Path(item).resolve().is_relative_to(shadow_package):
                return True
        except OSError:
            continue

    return False


def _import_qgs_application():
    shadow_root = str(Path(__file__).resolve().parents[2])

    for name, module in list(sys.modules.items()):
        if (name == "qgis" or name.startswith("qgis.")) and _is_shadow_qgis_module(
            module
        ):
            sys.modules.pop(name, None)

    removed_shadow_root = False
    if shadow_root in sys.path:
        sys.path.remove(shadow_root)
        removed_shadow_root = True

    try:
        from qgis.core import QgsApplication
    except ImportError as exc:
        raise QgisBackendError(
            "PyQGIS is not importable in this Python environment. Install QGIS with Python "
            "bindings and use a Python interpreter that can import qgis.core."
        ) from exc
    finally:
        if removed_shadow_root:
            sys.path.insert(0, shadow_root)

    return QgsApplication


def ensure_qgis_app():
    """Initialize PyQGIS once for this Python process."""
    global _QGIS_APP

    if _QGIS_APP is not None:
        return _QGIS_APP

    QgsApplication = _import_qgs_application()
    QgsApplication.setPrefixPath(_detect_qgis_prefix(), True)
    _QGIS_APP = QgsApplication([], False)
    _QGIS_APP.initQgis()
    return _QGIS_APP


def project_path_argument(project_path: str | None) -> str | None:
    """Normalize project paths for qgis_process invocations."""
    if not project_path:
        return None
    return f"--PROJECT_PATH={_normalize_path(project_path)}"


def _extract_payload_message(payload: dict[str, Any] | None) -> str | None:
    if not payload:
        return None

    log_entries = payload.get("log")
    if isinstance(log_entries, list):
        parts: list[str] = []
        for entry in log_entries:
            if isinstance(entry, dict):
                message = entry.get("message") or entry.get("text")
                if message:
                    parts.append(str(message))
            elif entry:
                parts.append(str(entry))
        if parts:
            return " | ".join(parts[-3:])

    results = payload.get("results")
    if isinstance(results, dict) and "error" in results:
        return str(results["error"])

    return None
