# ruff: noqa: F403, F405, E501
from .pm2_cli_base import *  # noqa: F403


def _output(data, as_json: bool):
    """Print data as JSON or formatted text."""
    if as_json:
        if isinstance(data, str):
            click.echo(json.dumps({"result": data}, indent=2))
        else:
            click.echo(json.dumps(data, indent=2, default=str))
    else:
        if isinstance(data, str):
            click.echo(data)
        elif isinstance(data, dict):
            if "message" in data:
                prefix = "OK" if data.get("success", True) else "ERROR"
                click.echo(f"[{prefix}] {data['message']}")
                if data.get("content"):
                    click.echo(data["content"])
                if data.get("instructions"):
                    click.echo(data["instructions"])
            else:
                for k, v in data.items():
                    click.echo(f"  {k}: {v}")
        elif isinstance(data, list):
            if data and isinstance(data[0], dict):
                # Print as table
                if not data:
                    return
                keys = list(data[0].keys())
                # Header
                header = "  ".join(f"{k:<15}" for k in keys)
                click.echo(header)
                click.echo("-" * len(header))
                for row in data:
                    line = "  ".join(f"{str(row.get(k, '')):<15}" for k in keys)
                    click.echo(line)
            else:
                for item in data:
                    click.echo(str(item))


lifecycle_mod = lifecycle_module = None


def _repl_start(args, as_json):
    """Handle 'lifecycle start' in REPL with --name parsing."""
    if not args:
        click.echo("Usage: lifecycle start <script> [--name <name>]")
        return
    script = args[0]
    name = None
    if "--name" in args:
        idx = args.index("--name")
        if idx + 1 < len(args):
            name = args[idx + 1]
    _output(lifecycle_mod.start_process(script, name=name, as_json=as_json), as_json)


def _repl_logs_view(args, as_json):
    """Handle 'logs view' in REPL with --lines parsing."""
    if not args:
        click.echo("Usage: logs view <name> [--lines N]")
        return
    name = args[0]
    lines = 20
    if "--lines" in args:
        idx = args.index("--lines")
        if idx + 1 < len(args):
            try:
                lines = int(args[idx + 1])
            except ValueError:
                pass
    _output(logs.view_logs(name, lines=lines, as_json=as_json), as_json)
