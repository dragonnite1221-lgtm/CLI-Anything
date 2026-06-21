# ruff: noqa: F403, F405, E501
from .quietshrink_cli_base import *  # noqa: F403

# fmt: off
from .quietshrink_cli_p1 import cli, find_bash_cli  # noqa: E402,E501
# fmt: on


@cli.command()
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
def presets(json_mode: bool) -> None:
    """List available quality presets with their characteristics."""
    presets_data = [
        {
            "name": "tiny",
            "q_value": 50,
            "typical_reduction": "~90%",
            "ssim": "~0.95",
            "use_case": "chat / email",
        },
        {
            "name": "balanced",
            "q_value": 55,
            "typical_reduction": "~88%",
            "ssim": "~0.99",
            "use_case": "docs / sharing",
        },
        {
            "name": "transparent",
            "q_value": 60,
            "typical_reduction": "~87%",
            "ssim": "~0.99+",
            "use_case": "default — visually lossless",
        },
        {
            "name": "pristine",
            "q_value": 70,
            "typical_reduction": "~84%",
            "ssim": "~0.997",
            "use_case": "archival / editing",
        },
    ]
    if json_mode:
        click.echo(json.dumps({"presets": presets_data}, indent=2))
    else:
        for p in presets_data:
            click.echo(
                f"  {p['name']:<13} q={p['q_value']:<3} {p['typical_reduction']:<6} ssim={p['ssim']:<8} — {p['use_case']}"
            )


@cli.command()
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
def doctor(json_mode: bool) -> None:
    """Verify environment is set up correctly."""
    checks = []

    # Check ffmpeg
    ffmpeg = shutil.which("ffmpeg")
    checks.append(
        {"check": "ffmpeg installed", "ok": bool(ffmpeg), "path": ffmpeg or "not found"}
    )

    # Check hevc_videotoolbox
    if ffmpeg:
        try:
            result = subprocess.run(
                [ffmpeg, "-hide_banner", "-encoders"],
                capture_output=True,
                text=True,
                check=True,
            )
            has_vt = "hevc_videotoolbox" in result.stdout
            checks.append({"check": "hevc_videotoolbox available", "ok": has_vt})
        except subprocess.CalledProcessError:
            checks.append({"check": "hevc_videotoolbox available", "ok": False})

    # Check bash CLI
    try:
        find_bash_cli()
        checks.append({"check": "quietshrink bash CLI", "ok": True})
    except click.ClickException:
        checks.append({"check": "quietshrink bash CLI", "ok": False})

    # Platform check
    import platform

    is_arm_mac = platform.system() == "Darwin" and platform.machine() == "arm64"
    checks.append({"check": "Apple Silicon Mac", "ok": is_arm_mac})

    all_ok = all(c["ok"] for c in checks)

    if json_mode:
        click.echo(json.dumps({"checks": checks, "ready": all_ok}, indent=2))
    else:
        for c in checks:
            mark = "✓" if c["ok"] else "✗"
            click.echo(f"  {mark} {c['check']}")
        click.echo()
        click.echo("Ready" if all_ok else "Setup incomplete")
    sys.exit(0 if all_ok else 1)
