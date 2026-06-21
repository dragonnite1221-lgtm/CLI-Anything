# ruff: noqa: F403, F405, E501
from .ollama_cli_base import *  # noqa: F403

# fmt: off
from .ollama_cli_p1 import cli, handle_error, output  # noqa: E402,E501
from .ollama_cli_p3 import generate  # noqa: E402,E501
# fmt: on


@generate.command("chat")
@click.option("--model", "-m", "model_name", required=True, help="Model name")
@click.option(
    "--message",
    "messages_input",
    multiple=True,
    help="Messages as role:content (repeatable)",
)
@click.option(
    "--file",
    "messages_file",
    type=click.Path(exists=True),
    default=None,
    help="JSON file with messages array",
)
@click.option(
    "--no-stream", is_flag=True, help="Return complete response instead of streaming"
)
@click.option("--temperature", type=float, default=None, help="Sampling temperature")
@click.option("--continue-chat", is_flag=True, help="Continue previous chat session")
@handle_error
def generate_chat(
    model_name, messages_input, messages_file, no_stream, temperature, continue_chat
):
    """Send a chat completion request."""
    global _last_model, _chat_history
    _last_model = model_name

    options = {}
    if temperature is not None:
        options["temperature"] = temperature

    # Build messages list
    if messages_file:
        with open(messages_file, "r") as f:
            messages = json.load(f)
    elif messages_input:
        messages = []
        for msg in messages_input:
            if ":" not in msg:
                raise ValueError(f"Invalid message format: '{msg}'. Use role:content")
            role, content = msg.split(":", 1)
            messages.append({"role": role.strip(), "content": content.strip()})
    else:
        raise ValueError("Provide messages via --message or --file")

    if continue_chat:
        messages = _chat_history + messages

    if no_stream or _json_output:
        result = gen_mod.chat(
            _host,
            model_name,
            messages,
            options=options or None,
            stream=False,
        )
        if not _json_output and "message" in result:
            _chat_history = messages + [result["message"]]
        output(result)
    else:
        chunks = gen_mod.chat(
            _host,
            model_name,
            messages,
            options=options or None,
            stream=True,
        )
        # Collect streamed content for history
        collected = []
        for chunk in chunks:
            if "error" in chunk:
                raise RuntimeError(chunk["error"])
            if "message" in chunk and "content" in chunk["message"]:
                token = chunk["message"]["content"]
                collected.append(token)
                sys.stdout.write(token)
                sys.stdout.flush()
        sys.stdout.write("\n")
        sys.stdout.flush()
        full_response = "".join(collected)
        _chat_history = messages + [{"role": "assistant", "content": full_response}]


@cli.group()
def embed():
    """Embedding generation commands."""
    pass


@embed.command("text")
@click.option("--model", "-m", "model_name", required=True, help="Model name")
@click.option(
    "--input",
    "-i",
    "input_texts",
    multiple=True,
    required=True,
    help="Text to embed. Repeat for batch embeddings.",
)
@handle_error
def embed_text(model_name, input_texts):
    """Generate embeddings for text."""
    payload = list(input_texts)
    result = embed_mod.embed(
        _host, model_name, payload[0] if len(payload) == 1 else payload
    )
    if _json_output:
        output(result)
    else:
        embeddings = result.get("embeddings", [])
        if embeddings:
            dims = len(embeddings[0]) if embeddings else 0
            click.echo(f"Model: {model_name}")
            click.echo(f"Dimensions: {dims}")
            click.echo(f"Vectors: {len(embeddings)}")
            # Show first few values
            if embeddings:
                preview = embeddings[0][:5]
                click.echo(f"Preview: [{', '.join(f'{v:.6f}' for v in preview)}, ...]")
        else:
            output(result)


@cli.group()
def server():
    """Server status and info commands."""
    pass


@server.command("status")
@handle_error
def server_status():
    """Check if Ollama server is running."""
    result = server_mod.server_status(_host)
    output(result, f"Ollama server at {_host}: running")


@server.command("version")
@handle_error
def server_version():
    """Show Ollama server version."""
    result = server_mod.version(_host)
    output(result)
