# ruff: noqa: F403, F405, E501
from .ollama_cli_base import *  # noqa: F403

# fmt: off
from .ollama_cli_p1 import cli, handle_error, output  # noqa: E402,E501
from .ollama_cli_p2 import _format_size, model  # noqa: E402,E501
# fmt: on


@model.command("pull")
@click.argument("name")
@click.option("--no-stream", is_flag=True, help="Wait for completion without progress")
@handle_error
def model_pull(name, no_stream):
    """Download a model from the Ollama library."""
    if no_stream or _json_output:
        result = models_mod.pull_model(_host, name, stream=False)
        output(result, f"Pulled: {name}")
    else:
        click.echo(f"Pulling {name}...")
        last_status = ""
        for chunk in models_mod.pull_model(_host, name, stream=True):
            if "error" in chunk:
                raise RuntimeError(chunk["error"])
            status = chunk.get("status", "")
            if status != last_status:
                click.echo(f"  {status}")
                last_status = status
            completed = chunk.get("completed", 0)
            total = chunk.get("total", 0)
            if total > 0:
                pct = int(completed / total * 100)
                bar_w = 30
                filled = int(bar_w * completed / total)
                bar = "█" * filled + "░" * (bar_w - filled)
                click.echo(
                    f"\r  {bar} {pct:3d}% ({_format_size(completed)}/{_format_size(total)})",
                    nl=False,
                )
        click.echo(f"\nDone: {name}")


@model.command("rm")
@click.argument("name")
@handle_error
def model_rm(name):
    """Delete a model from local storage."""
    result = models_mod.delete_model(_host, name)
    output(result, f"Deleted: {name}")


@model.command("copy")
@click.argument("source")
@click.argument("destination")
@handle_error
def model_copy(source, destination):
    """Copy a model to a new name."""
    result = models_mod.copy_model(_host, source, destination)
    output(result, f"Copied {source} → {destination}")


@model.command("ps")
@handle_error
def model_ps():
    """List models currently loaded in memory."""
    result = models_mod.running_models(_host)
    models = result.get("models", [])
    if _json_output:
        output(result)
    else:
        if not models:
            click.echo("No models currently loaded.")
            return
        click.echo(f"{'NAME':<40} {'SIZE':<12} {'PROCESSOR':<15} {'UNTIL'}")
        click.echo("─" * 80)
        for m in models:
            name = m.get("name", "")
            size = m.get("size", 0)
            proc = m.get("size_vram", 0)
            until = m.get("expires_at", "")[:19]
            click.echo(
                f"{name:<40} {_format_size(size):<12} {_format_size(proc):<15} {until}"
            )


@cli.group()
def generate():
    """Text generation and chat commands."""
    pass


@generate.command("text")
@click.option("--model", "-m", "model_name", required=True, help="Model name")
@click.option("--prompt", "-p", required=True, help="Input prompt")
@click.option("--system", "-s", default=None, help="System message")
@click.option(
    "--no-stream", is_flag=True, help="Return complete response instead of streaming"
)
@click.option("--temperature", type=float, default=None, help="Sampling temperature")
@click.option("--top-p", type=float, default=None, help="Top-p sampling")
@click.option("--num-predict", type=int, default=None, help="Max tokens to generate")
@handle_error
def generate_text(
    model_name, prompt, system, no_stream, temperature, top_p, num_predict
):
    """Generate text from a prompt."""
    global _last_model
    _last_model = model_name

    options = {}
    if temperature is not None:
        options["temperature"] = temperature
    if top_p is not None:
        options["top_p"] = top_p
    if num_predict is not None:
        options["num_predict"] = num_predict

    if no_stream or _json_output:
        result = gen_mod.generate(
            _host,
            model_name,
            prompt,
            system=system,
            options=options or None,
            stream=False,
        )
        output(result)
    else:
        chunks = gen_mod.generate(
            _host,
            model_name,
            prompt,
            system=system,
            options=options or None,
            stream=True,
        )
        final = gen_mod.stream_to_stdout(chunks)
