# ruff: noqa: F403, F405, E501
from .listener_base_base import *  # noqa: F403


def _get_local_ip() -> str:
    """Return the primary local IPv4 address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _make_ssl_context() -> tuple[ssl.SSLContext, str]:
    """Generate a temporary self-signed cert and return (SSLContext, tmp_dir)."""
    tmp_dir = tempfile.mkdtemp(prefix="nslogger_cli_")
    cert = os.path.join(tmp_dir, "server.crt")
    key = os.path.join(tmp_dir, "server.key")
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-keyout",
            key,
            "-out",
            cert,
            "-days",
            "1",
            "-nodes",
            "-subj",
            "/CN=nslogger-cli",
        ],
        check=True,
        capture_output=True,
    )
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    if hasattr(ssl, "TLSVersion"):
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    try:
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
    except ssl.SSLError:
        pass
    ctx.load_cert_chain(cert, key)
    return ctx, tmp_dir


def _make_pkcs12_identity() -> tuple[str, str, str]:
    """Generate a temporary self-signed PKCS#12 identity for CFStream server SSL."""
    tmp_dir = tempfile.mkdtemp(prefix="nslogger_cli_")
    cert = os.path.join(tmp_dir, "server.crt")
    key = os.path.join(tmp_dir, "server.key")
    p12 = os.path.join(tmp_dir, "server.p12")
    password = "nslogger-cli"
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-keyout",
            key,
            "-out",
            cert,
            "-days",
            "1",
            "-nodes",
            "-subj",
            "/CN=nslogger-cli",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "openssl",
            "pkcs12",
            "-export",
            "-inkey",
            key,
            "-in",
            cert,
            "-out",
            p12,
            "-passout",
            f"pass:{password}",
        ],
        check=True,
        capture_output=True,
    )
    return p12, password, tmp_dir


def _swift_helper_env() -> dict[str, str]:
    env = os.environ.copy()
    cache_root = tempfile.gettempdir()
    env.setdefault(
        "SWIFT_MODULE_CACHE_PATH",
        os.path.join(cache_root, "nslogger_cli_swift_module_cache"),
    )
    env.setdefault(
        "CLANG_MODULE_CACHE_PATH",
        os.path.join(cache_root, "nslogger_cli_clang_module_cache"),
    )
    return env
