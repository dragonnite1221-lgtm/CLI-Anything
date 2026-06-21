# ruff: noqa: F403, F405, E402, F401, E501
from .anygen_backend_base import *

from . import anygen_backend_base as _coupbase  # noqa: E402


def load_config() -> dict:
    """Load configuration from ~/.config/anygen/config.json."""
    if not _coupbase._COUP_GLOBALS["CONFIG_FILE"].exists():
        return {}
    try:
        with open(_coupbase._COUP_GLOBALS["CONFIG_FILE"], "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(config: dict):
    """Save configuration to ~/.config/anygen/config.json (mode 600)."""
    _coupbase._COUP_GLOBALS["CONFIG_DIR"].mkdir(parents=True, exist_ok=True)
    with open(_coupbase._COUP_GLOBALS["CONFIG_FILE"], "w") as f:
        json.dump(config, f, indent=2)
    _coupbase._COUP_GLOBALS["CONFIG_FILE"].chmod(384)


def get_api_key(cli_key: str | None = None) -> str | None:
    """Resolve API key: CLI arg → env var → config file."""
    if cli_key:
        return cli_key
    env_key = os.environ.get(ENV_API_KEY)
    if env_key:
        return env_key
    return load_config().get("api_key")


def _make_auth_token(api_key: str) -> str:
    return api_key if api_key.startswith("Bearer ") else f"Bearer {api_key}"


def _require_api_key(api_key: str | None) -> str:
    if not api_key:
        raise RuntimeError(
            f"AnyGen API key not found. Provide one via:\n  1. --api-key sk-xxx\n  2. export {ENV_API_KEY}=sk-xxx\n  3. cli-anything-anygen config set api_key sk-xxx\nGet a key at https://www.anygen.io/home → Setting → Integration"
        )
    return api_key


def upload_file(
    api_key: str, file_path: str, extra_headers: dict | None = None
) -> dict:
    """Upload a file and return {"file_token": ..., "filename": ..., "file_size": ...}."""
    api_key = _require_api_key(api_key)
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    headers = {"Authorization": _make_auth_token(api_key)}
    if extra_headers:
        headers.update(extra_headers)
    with open(path, "rb") as f:
        files = {"file": (path.name, f)}
        data = {"filename": path.name}
        resp = requests.post(
            f"{API_BASE}/v1/openapi/files/upload",
            files=files,
            data=data,
            headers=headers,
            timeout=60,
        )
    if resp.status_code != 200:
        raise RuntimeError(
            f"Upload failed (HTTP {resp.status_code}): {resp.text[:300]}"
        )
    result = resp.json()
    if not result.get("success"):
        raise RuntimeError(f"Upload failed: {result.get('error', 'Unknown error')}")
    return {
        "file_token": result.get("file_token"),
        "filename": result.get("filename"),
        "file_size": result.get("file_size"),
    }


def encode_file(file_path: str) -> dict:
    """Encode a file to base64 for legacy attachment in create_task."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(path, "rb") as f:
        content = f.read()
    mime_types = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".txt": "text/plain",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".ppt": "application/vnd.ms-powerpoint",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
    mime_type = mime_types.get(path.suffix.lower(), "application/octet-stream")
    return {
        "file_name": path.name,
        "file_type": mime_type,
        "file_data": base64.b64encode(content).decode("utf-8"),
    }
