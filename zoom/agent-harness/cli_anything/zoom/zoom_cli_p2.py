# ruff: noqa: F403, F405, E501
from .zoom_cli_base import *  # noqa: F403

# fmt: off
from .zoom_cli_p1 import cli, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.zoom.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("zoom", version="1.0.1")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "auth": "setup|login|status|logout",
        "meeting": "create|list|info|update|delete|join|start",
        "participant": "add|add-batch|list|remove|attended",
        "recording": "list|files|download|delete",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    # Check auth status on start
    try:
        status = auth_mod.get_auth_status()
        if status.get("authenticated"):
            skin.success(f"Authenticated as: {status.get('user', 'unknown')}")
        elif status.get("configured"):
            skin.warning("OAuth configured but not logged in. Run: auth login")
        else:
            skin.info(
                "Not configured. Run: auth setup --client-id <ID> --client-secret <SECRET>"
            )
    except Exception:
        skin.info("Run 'auth setup' to configure OAuth credentials.")

    while True:
        try:
            # Determine context for prompt
            try:
                status = auth_mod.get_auth_status()
                context = status.get("user", "") if status.get("authenticated") else ""
            except Exception:
                context = ""

            line = skin.get_input(pt_session, context=context)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_repl_commands)
                continue

            # Parse and execute command (shlex handles quoted strings with spaces)
            try:
                args = shlex.split(line)
            except ValueError:
                args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


@cli.group()
def auth():
    """Authentication and OAuth2 setup."""
    pass


@auth.command("setup")
@click.option("--client-id", required=True, help="Zoom OAuth app Client ID")
@click.option("--client-secret", required=True, help="Zoom OAuth app Client Secret")
@click.option(
    "--redirect-uri",
    default="http://localhost:4199/callback",
    help="OAuth redirect URI",
)
@handle_error
def auth_setup(client_id, client_secret, redirect_uri):
    """Configure OAuth app credentials."""
    result = auth_mod.setup_oauth(client_id, client_secret, redirect_uri)
    output(result, "OAuth app configured successfully.")


@auth.command("login")
@click.option("--code", default=None, help="Authorization code (for manual flow)")
@handle_error
def auth_login(code):
    """Login via OAuth2 browser flow.

    Opens a browser for Zoom authorization. After approving,
    tokens are saved locally for subsequent API calls.

    Use --code if you need to manually paste the authorization code.
    """
    if code:
        result = auth_mod.login_with_code(code)
    else:
        result = auth_mod.login()
    output(result, "Login successful.")


@auth.command("status")
@handle_error
def auth_status():
    """Check authentication status."""
    result = auth_mod.get_auth_status()
    output(result)
