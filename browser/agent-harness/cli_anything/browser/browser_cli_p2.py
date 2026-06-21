# ruff: noqa: F403, F405, E501
from .browser_cli_base import *  # noqa: F403

# fmt: off
from .browser_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.browser.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("browser", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "page": "open|reload|back|forward|info",
        "fs": "ls|cd|cat|grep|pwd",
        "act": "click|type",
        "session": "status|daemon-start|daemon-stop",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    while True:
        try:
            sess = get_session()
            # Show URL and working dir in prompt
            context = sess.working_dir if sess.working_dir != "/" else "/"
            if sess.current_url:
                # Truncate long URLs for prompt
                url_display = (
                    sess.current_url[:40] + "..."
                    if len(sess.current_url) > 40
                    else sess.current_url
                )
                context = f"{url_display} {context}"

            line = skin.get_input(pt_session, context=context)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_repl_commands)
                continue

            # Parse and execute command (preserve quoted arguments)
            try:
                args = shlex.split(line)
            except ValueError:
                args = line.split()  # Fallback for unbalanced quotes
            # Propagate --json from top-level to subcommands in REPL
            if (
                _json_output
                and "--json" not in args
                and not any(a.startswith("--json") for a in args)
            ):
                args = ["--json"] + args
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
def page():
    """Page navigation commands."""
    pass


@page.command("open")
@click.argument("url")
@handle_error
def page_open(url):
    """Open a URL in Chrome."""
    sess = get_session()
    result = page_mod.open_page(sess, url)
    output(result, f"Opened: {url}")


@page.command("reload")
@handle_error
def page_reload():
    """Reload the current page."""
    sess = get_session()
    result = page_mod.reload_page(sess)
    output(result, "Page reloaded")


@page.command("back")
@handle_error
def page_back():
    """Navigate back in history."""
    sess = get_session()
    result = page_mod.go_back(sess)
    if "error" in result:
        output(result, result["error"])
    else:
        output(result, "Navigated back")


@page.command("forward")
@handle_error
def page_forward():
    """Navigate forward in history."""
    sess = get_session()
    result = page_mod.go_forward(sess)
    if "error" in result:
        output(result, result["error"])
    else:
        output(result, "Navigated forward")


@page.command("info")
@handle_error
def page_info():
    """Show current page information."""
    sess = get_session()
    result = page_mod.get_page_info(sess)
    output(result)


@cli.group()
def fs():
    """Filesystem navigation commands (Accessibility Tree)."""
    pass
