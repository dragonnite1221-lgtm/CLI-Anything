# ruff: noqa: F403, F405, E501
from .cc_backend_base import *  # noqa: F403


def find_cloudcompare() -> list[str]:
    """Locate the CloudCompare executable.

    Returns a command prefix list (e.g., ['CloudCompare'] or
    ['flatpak', 'run', 'org.cloudcompare.CloudCompare']).

    Raises RuntimeError with install instructions if not found.
    """
    # 1. Try native binary first
    native = shutil.which("CloudCompare") or shutil.which("cloudcompare")
    if native:
        return [native]

    # 2. Try Flatpak
    flatpak = shutil.which("flatpak")
    if flatpak:
        result = subprocess.run(
            ["flatpak", "list", "--app", "--columns=application"],
            capture_output=True,
            text=True,
        )
        if "org.cloudcompare.CloudCompare" in result.stdout:
            return ["flatpak", "run", "org.cloudcompare.CloudCompare"]

    # 3. Try snap
    snap_path = "/snap/bin/cloudcompare"
    if os.path.exists(snap_path):
        return [snap_path]

    raise RuntimeError(
        "CloudCompare is not installed or not found.\n"
        "Install it with one of:\n"
        "  flatpak install flathub org.cloudcompare.CloudCompare  # Flatpak\n"
        "  sudo apt install cloudcompare                          # Debian/Ubuntu\n"
        "  brew install --cask cloudcompare                       # macOS\n"
        "  https://cloudcompare.org/release/index.html            # Windows installer"
    )


def run_cloudcompare(args: list[str], cwd: Optional[str] = None) -> dict:
    """Run CloudCompare with the given arguments in silent mode.

    Args:
        args: List of CC arguments (without the executable itself).
              The -SILENT flag is prepended automatically.
        cwd: Working directory for the subprocess.

    Returns:
        dict with keys: returncode, stdout, stderr, command
    """
    cmd_prefix = find_cloudcompare()
    full_cmd = cmd_prefix + ["-SILENT"] + args

    result = subprocess.run(
        full_cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
    )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "command": " ".join(full_cmd),
    }


def open_and_save(
    input_path: str,
    output_path: str,
    extra_args: Optional[list[str]] = None,
) -> dict:
    """Load a point cloud, optionally process it, and save.

    Args:
        input_path: Path to input file.
        output_path: Path to output file.
        extra_args: Additional CC command-line arguments between load and save.

    Returns:
        dict with result info.
    """
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)
    out_dir = os.path.dirname(output_path)
    out_name = os.path.splitext(os.path.basename(output_path))[0]
    out_ext = os.path.splitext(output_path)[1].lstrip(".")

    fmt = CLOUD_FORMATS.get(out_ext.lower(), "ASC")

    args = ["-O", input_path]
    if extra_args:
        args.extend(extra_args)

    args += [
        "-C_EXPORT_FMT",
        fmt,
        "-NO_TIMESTAMP",
        "-SAVE_CLOUDS",
        "FILE",
        output_path,
    ]

    result = run_cloudcompare(args, cwd=out_dir)
    result["output"] = output_path
    result["exists"] = os.path.exists(output_path)
    if result["exists"]:
        result["file_size"] = os.path.getsize(output_path)
    return result
