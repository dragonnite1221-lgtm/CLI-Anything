# ruff: noqa: F403, F405, E501
from .novita_cli_base import *  # noqa: F403

# fmt: off
from .novita_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .novita_cli_p2 import session  # noqa: E402,E501
# fmt: on


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
def stream(ctx, prompt, model_opt=None, temperature=None, max_tokens=None):
    """Stream chat completion."""
    parent_key = ctx.obj.get("api_key") if ctx.obj else None
    api_key = get_api_key(parent_key)
    model = (
        model_opt
        or (ctx.obj.get("model") if ctx.obj else None)
        or "deepseek/deepseek-v3.2"
    )

    # Build messages
    messages = []
    session = get_session()
    messages.extend(session.get_messages())
    messages.append({"role": "user", "content": prompt})

    full_response = ""

    def on_chunk(chunk_content):
        if chunk_content:
            nonlocal full_response
            full_response += chunk_content
            if not _json_output:
                click.echo(chunk_content, nl=False)

    result = chat_completion_stream(
        api_key=api_key,
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        on_chunk=on_chunk,
    )

    if not _json_output:
        click.echo()  # Add newline after stream

    # Update session
    session.add_user_message(prompt)
    session.add_assistant_message(full_response)

    output({"content": full_response}, "✓ Stream completed")


@session.command("status")
@handle_error
def session_status():
    """Show session status."""
    s = get_session()
    output(s.status(), "Session status")


@session.command("clear")
@handle_error
def session_clear():
    """Clear session history."""
    s = get_session()
    s.clear()
    output({"cleared": True}, "Session cleared")


@session.command("history")
@click.option("--limit", "-n", type=int, default=20, help="Maximum entries to show")
@handle_error
def session_history(limit):
    """Show command history."""
    s = get_session()
    history = s.history[-limit:]
    output(history, f"History ({len(history)} entries)")


@cli.group()
def config():
    """Configuration management."""
    pass


@config.command("set")
@click.argument("key", type=click.Choice(["api_key", "default_model"]))
@click.argument("value")
def config_set(key, value):
    """Set a configuration value."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    display = value[:10] + "..." if key == "api_key" and len(value) > 10 else value
    output({"key": key, "value": display}, f"✓ Set {key} = {display}")


@config.command("get")
@click.argument("key", required=False)
def config_get(key):
    """Get a configuration value (or show all)."""
    cfg = load_config()
    if key:
        val = cfg.get(key)
        if val:
            if key == "api_key" and len(val) > 10:
                val = val[:10] + "..."
            output({"key": key, "value": val}, f"{key} = {val}")
        else:
            output({"key": key, "value": None}, f"{key} is not set")
    else:
        if cfg:
            masked = {}
            for k, v in cfg.items():
                masked[k] = v[:10] + "..." if k == "api_key" and len(v) > 10 else v
            output(masked)
        else:
            output({}, "No configuration set")
