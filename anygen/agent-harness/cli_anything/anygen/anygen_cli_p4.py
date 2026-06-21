# ruff: noqa: F403, F405, E501
from .anygen_cli_base import *  # noqa: F403

# fmt: off
from .anygen_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .anygen_cli_p2 import task  # noqa: E402,E501
# fmt: on


@task.command("prepare")
@click.option("--message", "-m", required=True, help="User message")
@click.option("--file-token", multiple=True, help="File token (repeatable)")
@click.option("--input", "input_file", default=None, help="Load conversation from JSON")
@click.option("--save", "save_file", default=None, help="Save conversation to JSON")
@handle_error
def task_prepare(message, file_token, input_file, save_file):
    """Multi-turn requirement analysis before creating a task."""
    messages = []
    loaded_file_tokens = set()

    if input_file:
        with open(input_file) as f:
            data = json.load(f)
        messages = data.get("messages", [])
        loaded_file_tokens = set(data.get("file_tokens", []))

    ft_list = list(file_token) if file_token else []
    all_tokens = ft_list + list(loaded_file_tokens)

    content = [{"type": "text", "text": message}]
    for ft in ft_list:
        if ft not in loaded_file_tokens:
            content.append({"type": "file", "file_token": ft})
    messages.append({"role": "user", "content": content})

    result = task_mod.prepare_task(
        _api_key,
        messages,
        file_tokens=all_tokens if all_tokens else None,
    )

    if save_file:
        save_data = {
            "messages": result.get("messages", messages),
            "file_tokens": all_tokens,
            "status": result.get("status"),
            "suggested_task_params": result.get("suggested_task_params"),
        }
        with open(save_file, "w") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

    reply = result.get("reply", "")
    status = result.get("status", "collecting")
    suggested = result.get("suggested_task_params")

    out = {"reply": reply, "status": status}
    if suggested:
        out["suggested_task_params"] = suggested

    msg = f"AnyGen: {reply}\nStatus: {status}"
    if suggested:
        msg += f"\nSuggested operation: {suggested.get('operation', 'N/A')}"
    output(out, msg)


@cli.group()
def file():
    """File operations — upload reference files."""
    pass


@file.command("upload")
@click.argument("path", type=click.Path(exists=True))
@handle_error
def file_upload(path):
    """Upload a reference file to get a file_token."""
    result = task_mod.upload_file(_api_key, path)
    sess = get_session()
    sess.record("file upload", {"path": path}, result)
    output(result, f"✓ Uploaded: {result['filename']} → token: {result['file_token']}")


@cli.group()
def config():
    """Configuration management — API key and settings."""
    pass


@config.command("set")
@click.argument("key", type=click.Choice(["api_key", "default_language"]))
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
