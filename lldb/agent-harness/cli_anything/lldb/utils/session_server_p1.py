# ruff: noqa: F403, F405, E501
from .session_server_base import *  # noqa: F403


def _encode_token(token: bytes) -> str:
    return base64.b64encode(token).decode("ascii")


def _best_effort_chmod(path: Path, mode: int):
    try:
        os.chmod(path, mode)
    except OSError:
        pass


def _best_effort_restrict_windows_acl(path: Path):
    if os.name != "nt":
        return
    user = getpass.getuser()
    try:
        subprocess.run(
            ["icacls", str(path), "/inheritance:r", "/grant:r", f"{user}:F"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        pass


def _prepare_state_dir(state_dir: Path):
    state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    _best_effort_chmod(state_dir, 0o700)
    _best_effort_restrict_windows_acl(state_dir)


def _write_owner_only_json(path: Path, payload: dict[str, Any]):
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_BINARY", 0)
    fd = os.open(tmp_path, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
            handle.flush()
            os.fsync(handle.fileno())
        _best_effort_chmod(tmp_path, 0o600)
        _best_effort_restrict_windows_acl(tmp_path)
        os.replace(tmp_path, path)
        _best_effort_chmod(path, 0o600)
        _best_effort_restrict_windows_acl(path)
    finally:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass


def _write_state_file(state_file: Path, address: tuple[str, int], token: bytes):
    _prepare_state_dir(state_file.parent)
    payload = {
        "host": address[0],
        "port": address[1],
        "token": _encode_token(token),
        "pid": os.getpid(),
    }
    _write_owner_only_json(state_file, payload)


def _remove_state_file(state_file: Path):
    try:
        state_file.unlink()
    except FileNotFoundError:
        pass


def _recv_exact(conn: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = conn.recv(size - len(chunks))
        if not chunk:
            raise ConnectionError("Unexpected EOF while reading request")
        chunks.extend(chunk)
    return bytes(chunks)


def _recv_message(conn: socket.socket) -> dict[str, Any]:
    header = _recv_exact(conn, 4)
    message_size = struct.unpack("!I", header)[0]
    if message_size <= 0 or message_size > MAX_MESSAGE_BYTES:
        raise ValueError(f"Invalid message size: {message_size}")
    payload = _recv_exact(conn, message_size)
    message = json.loads(payload.decode("utf-8"))
    if not isinstance(message, dict):
        raise ValueError("Request payload must be a JSON object")
    return message


def _send_message(conn: socket.socket, payload: dict[str, Any]):
    raw = json.dumps(payload).encode("utf-8")
    if len(raw) > MAX_MESSAGE_BYTES:
        raise ValueError("Response payload is too large")
    conn.sendall(struct.pack("!I", len(raw)))
    conn.sendall(raw)


def _validate_request(request: dict[str, Any]):
    method = request.get("method")
    args = request.get("args", [])
    kwargs = request.get("kwargs", {})
    if not isinstance(method, str) or not method:
        raise ValueError("Request is missing a valid method name")
    if not isinstance(args, list):
        raise ValueError("Request args must be a list")
    if not isinstance(kwargs, dict):
        raise ValueError("Request kwargs must be an object")
