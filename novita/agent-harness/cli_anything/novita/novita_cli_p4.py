# ruff: noqa: F403, F405, E501
from .novita_cli_base import *  # noqa: F403

# fmt: off
from .novita_cli_p1 import cli, handle_error, output  # noqa: E402,E501
from .novita_cli_p3 import config  # noqa: E402,E501
# fmt: on


@config.command("delete")
@click.argument("key")
def config_delete(key):
    """Delete a configuration value."""
    cfg = load_config()
    if key in cfg:
        del cfg[key]
        save_config(cfg)
        output({"deleted": key}, f"✓ Deleted {key}")
    else:
        output({"error": f"{key} not found"}, f"{key} not found in config")


@config.command("path")
def config_path():
    """Show the config file path."""
    from cli_anything.novita.utils.novita_backend import CONFIG_FILE

    output({"path": str(CONFIG_FILE)}, f"Config file: {CONFIG_FILE}")


@cli.command()
@click.option(
    "--model",
    "model_opt",
    type=str,
    default=None,
    help="Model ID to test (default: deepseek/deepseek-v3.2)",
)
@handle_error
def test(model_opt=None):
    """Test Novita API connectivity."""
    api_key = get_api_key()
    model = model_opt or "deepseek/deepseek-v3.2"

    result = chat_completion(
        api_key=api_key,
        model=model,
        messages=[{"role": "user", "content": "Say 'ok'"}],
        max_tokens=5,
    )

    choices = result.get("choices", [])
    content = ""
    if choices:
        content = choices[0].get("message", {}).get("content", "")

    output(
        {"status": "ok", "model": model, "response": content},
        "✓ Novita API test passed",
    )


@cli.command()
@handle_error
def models():
    """List available models."""
    api_key = get_api_key()
    models_list = list_models(api_key)

    for m in models_list:
        click.echo(m.get("id", m.get("name", "unknown")))


def main():
    cli()
