# ruff: noqa: F403, F405, E501
from .novita_cli_base import *  # noqa: F403

# fmt: off
from .novita_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command("repl", hidden=True)
@handle_error
def repl():
    """Enter interactive REPL mode."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.novita.utils.repl_skin import ReplSkin

    skin = ReplSkin("novita", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    commands = {
        "chat <prompt>": "Chat with the Novita API",
        "stream <prompt>": "Stream chat completion",
        "session status": "Show session status",
        "session clear": "Clear session history",
        "session history": "Show command history",
        "config set <key> <val>": "Set configuration",
        "config get [key]": "Show configuration",
        "test [model]": "Test API connectivity",
        "models": "List available models",
        "help": "Show this help",
        "quit / exit": "Exit REPL",
    }

    while True:
        try:
            line = skin.get_input(pt_session, context="novita")
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            skin.print_goodbye()
            break
        if line == "help":
            skin.help(commands)
            continue

        parts = line.split()
        try:
            cli.main(parts, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


@cli.group()
def session():
    """Session management commands."""
    pass


@cli.command()
@click.option("--prompt", "-p", required=True, help="User prompt")
@click.option(
    "--model",
    "model_opt",
    type=str,
    default=None,
    help="Model ID (default: deepseek/deepseek-v3.2)",
)
@click.option("--temperature", type=float, default=None, help="Temperature (0.0-1.0)")
@click.option("--max-tokens", type=int, default=None, help="Maximum tokens to generate")
@click.pass_context
@handle_error
def chat(ctx, prompt, model_opt=None, temperature=None, max_tokens=None):
    """Chat with the Novita API."""
    parent_key = ctx.obj.get("api_key") if ctx.obj else None
    api_key = get_api_key(parent_key)
    model = (
        model_opt
        or (ctx.obj.get("model") if ctx.obj else None)
        or "deepseek/deepseek-v3.2"
    )

    # Build messages
    messages = []

    # Check for existing session
    session = get_session()
    messages.extend(session.get_messages())
    messages.append({"role": "user", "content": prompt})

    result = chat_completion(
        api_key=api_key,
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Extract content
    choices = result.get("choices", [])
    if choices:
        content = choices[0].get("message", {}).get("content", "")
    else:
        content = ""

    # Update session
    session.add_user_message(prompt)
    session.add_assistant_message(content)

    # Add usage info if available
    output_data = {"content": content}
    usage = result.get("usage", {})
    if usage:
        output_data["usage"] = usage

    output(output_data, f"✓ Response from {model}")
