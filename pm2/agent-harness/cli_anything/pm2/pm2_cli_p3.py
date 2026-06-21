# ruff: noqa: F403, F405, E501
from .pm2_cli_base import *  # noqa: F403

# fmt: off
from .pm2_cli_p1 import _output, lifecycle_mod  # noqa: E402,E501
from .pm2_cli_p2 import _run_repl, lifecycle  # noqa: E402,E501
# fmt: on


@lifecycle.command("start")
@click.argument("script")
@click.option("--name", default=None, help="Process name.")
@click.pass_context
def lifecycle_start(ctx, script, name):
    """Start a new PM2 process."""
    as_json = ctx.obj["json"]
    data = lifecycle_mod.start_process(script, name=name, as_json=as_json)
    _output(data, as_json)


@lifecycle.command("delete")
@click.argument("name")
@click.pass_context
def lifecycle_delete(ctx, name):
    """Delete a PM2 process."""
    as_json = ctx.obj["json"]
    data = lifecycle_mod.delete_process(name, as_json=as_json)
    _output(data, as_json)


def _init_lifecycle_mod():
    """Lazy-init the lifecycle module reference."""
    global lifecycle_mod
    if lifecycle_mod is None:
        from .core import lifecycle as _lc

        lifecycle_mod = _lc


_init_lifecycle_mod()


@main.group("logs")
@click.pass_context
def logs_group(ctx):
    """Log commands: view, flush."""
    pass


@logs_group.command("view")
@click.argument("name")
@click.option("--lines", default=20, help="Number of log lines.")
@click.pass_context
def logs_view(ctx, name, lines):
    """View recent logs for a PM2 process."""
    as_json = ctx.obj["json"]
    data = logs.view_logs(name, lines=lines, as_json=as_json)
    _output(data, as_json)


@logs_group.command("flush")
@click.argument("name", required=False, default=None)
@click.pass_context
def logs_flush(ctx, name):
    """Flush logs for a process (or all if no name given)."""
    as_json = ctx.obj["json"]
    data = logs.flush_logs(name=name, as_json=as_json)
    _output(data, as_json)


@main.group("system")
@click.pass_context
def system_group(ctx):
    """System commands: save, startup, version."""
    pass


@system_group.command("save")
@click.pass_context
def system_save(ctx):
    """Save current PM2 process list."""
    as_json = ctx.obj["json"]
    data = system.save(as_json=as_json)
    _output(data, as_json)


@system_group.command("startup")
@click.pass_context
def system_startup(ctx):
    """Generate PM2 startup script."""
    as_json = ctx.obj["json"]
    data = system.startup(as_json=as_json)
    _output(data, as_json)


@system_group.command("version")
@click.pass_context
def system_version(ctx):
    """Show PM2 version."""
    as_json = ctx.obj["json"]
    data = system.version(as_json=as_json)
    _output(data, as_json)


@click.group(invoke_without_command=True)
@click.option(
    "--json", "as_json", is_flag=True, default=False, help="Output in JSON format."
)
@click.pass_context
def main(ctx, as_json):
    """CLI-Anything PM2 — Process management harness for PM2."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = as_json

    if ctx.invoked_subcommand is None:
        # Launch REPL mode
        _run_repl()
