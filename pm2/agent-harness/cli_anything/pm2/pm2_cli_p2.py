# ruff: noqa: F403, F405, E501
from .pm2_cli_base import *  # noqa: F403

# fmt: off
from .pm2_cli_p1 import _output, _repl_logs_view, _repl_start, lifecycle_mod  # noqa: E402,E501
from .pm2_cli_p3 import main  # noqa: E402,E501
# fmt: on


def _run_repl():
    """Launch the interactive REPL."""
    from .utils.repl_skin import ReplSkin

    skin = ReplSkin("pm2", version="1.0.0")
    skin.print_banner()

    session = skin.create_prompt_session()

    # REPL command mapping
    repl_commands = {
        "process list": lambda args, j: _output(processes.list_processes(as_json=j), j),
        "process describe": lambda args, j: _output(
            processes.describe_process(args[0], as_json=j)
            if args
            else "Usage: process describe <name>",
            j,
        ),
        "process metrics": lambda args, j: _output(processes.get_metrics(as_json=j), j),
        "lifecycle restart": lambda args, j: _output(
            lifecycle_mod.restart_process(args[0], as_json=j)
            if args
            else "Usage: lifecycle restart <name>",
            j,
        ),
        "lifecycle stop": lambda args, j: _output(
            lifecycle_mod.stop_process(args[0], as_json=j)
            if args
            else "Usage: lifecycle stop <name>",
            j,
        ),
        "lifecycle start": lambda args, j: _repl_start(args, j),
        "lifecycle delete": lambda args, j: _output(
            lifecycle_mod.delete_process(args[0], as_json=j)
            if args
            else "Usage: lifecycle delete <name>",
            j,
        ),
        "logs view": lambda args, j: _repl_logs_view(args, j),
        "logs flush": lambda args, j: _output(
            logs.flush_logs(name=args[0] if args else None, as_json=j), j
        ),
        "system save": lambda args, j: _output(system.save(as_json=j), j),
        "system startup": lambda args, j: _output(system.startup(as_json=j), j),
        "system version": lambda args, j: _output(system.version(as_json=j), j),
    }

    help_commands = {
        "process list": "List all PM2 processes",
        "process describe N": "Detailed info for process N",
        "process metrics": "CPU/memory metrics for all processes",
        "lifecycle start S": "Start script S [--name N]",
        "lifecycle stop N": "Stop process N",
        "lifecycle restart N": "Restart process N",
        "lifecycle delete N": "Delete process N",
        "logs view N": "View logs for process N [--lines 50]",
        "logs flush [N]": "Flush logs (optionally for process N)",
        "system save": "Save PM2 process list",
        "system startup": "Generate startup script",
        "system version": "Show PM2 version",
        "help": "Show this help",
        "quit / exit": "Exit the REPL",
    }

    while True:
        try:
            user_input = skin.get_input(session)
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not user_input:
            continue

        raw = user_input.strip()

        if raw in ("quit", "exit", "q"):
            skin.print_goodbye()
            break

        if raw == "help":
            skin.help(help_commands)
            continue

        # Check for --json flag in input
        as_json = False
        if "--json" in raw:
            as_json = True
            raw = raw.replace("--json", "").strip()

        # Match command
        matched = False
        for cmd_key, handler in repl_commands.items():
            if raw.startswith(cmd_key):
                remainder = raw[len(cmd_key) :].strip()
                args = remainder.split() if remainder else []
                try:
                    handler(args, as_json)
                except Exception as e:
                    skin.error(str(e))
                matched = True
                break

        if not matched:
            skin.warning(f"Unknown command: {raw}")
            skin.hint("Type 'help' for available commands.")


@main.group()
@click.pass_context
def process(ctx):
    """Process info commands: list, describe, metrics."""
    pass


@process.command("list")
@click.pass_context
def process_list(ctx):
    """List all PM2 processes."""
    as_json = ctx.obj["json"]
    data = processes.list_processes(as_json=as_json)
    _output(data, as_json)


@process.command("describe")
@click.argument("name")
@click.pass_context
def process_describe(ctx, name):
    """Show detailed info for a PM2 process."""
    as_json = ctx.obj["json"]
    data = processes.describe_process(name, as_json=as_json)
    if data is None:
        click.echo(f"Process '{name}' not found.", err=True)
        sys.exit(1)
    _output(data, as_json)


@process.command("metrics")
@click.pass_context
def process_metrics(ctx):
    """Show CPU/memory metrics for all processes."""
    as_json = ctx.obj["json"]
    data = processes.get_metrics(as_json=as_json)
    _output(data, as_json)


@main.group()
@click.pass_context
def lifecycle(ctx):
    """Lifecycle commands: start, stop, restart, delete."""
    pass


@lifecycle.command("restart")
@click.argument("name")
@click.pass_context
def lifecycle_restart(ctx, name):
    """Restart a PM2 process."""
    as_json = ctx.obj["json"]
    data = lifecycle_mod.restart_process(name, as_json=as_json)
    _output(data, as_json)


@lifecycle.command("stop")
@click.argument("name")
@click.pass_context
def lifecycle_stop(ctx, name):
    """Stop a PM2 process."""
    as_json = ctx.obj["json"]
    data = lifecycle_mod.stop_process(name, as_json=as_json)
    _output(data, as_json)
