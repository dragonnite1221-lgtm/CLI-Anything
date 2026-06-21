# ruff: noqa: F403, F405, E501
from .unrealinsights_cli_base import *  # noqa: F403


_repl_mode = False
def _get_session(ctx: click.Context) -> UnrealInsightsSession:
    ctx.ensure_object(dict)
    session = ctx.obj.get("session")
    if session is None:
        session = UnrealInsightsSession.load()
        ctx.obj["session"] = session
    return session
def _output(ctx: click.Context, data, human_fn=None):
    if ctx.obj.get("json_mode"):
        output_json(data)
    elif human_fn:
        human_fn(data)
    else:
        output_json(data)
def _handle_exc(ctx: click.Context, exc: Exception):
    err = handle_error(exc, debug=ctx.obj.get("debug", False))
    if ctx.obj.get("json_mode"):
        output_json(err)
        ctx.exit(1)
    raise click.ClickException(err["error"])
def _resolve_insights(ctx: click.Context) -> dict[str, object]:
    session = _get_session(ctx)
    info = resolve_unrealinsights_exe(session.insights_exe, required=True)
    session.set_insights_exe(info["path"])
    return info
def _resolve_trace_server(ctx: click.Context) -> dict[str, object]:
    session = _get_session(ctx)
    info = resolve_trace_server_exe(session.trace_server_exe, required=False)
    if info["available"]:
        session.set_trace_server_exe(info["path"])
    return info
def _require_trace(ctx: click.Context) -> str:
    session = _get_session(ctx)
    if not session.trace_path:
        raise click.ClickException("No trace selected. Use --trace <path> or `trace set <path>` first.")
    trace_path = Path(session.trace_path).expanduser().resolve()
    if not trace_path.is_file():
        raise click.ClickException(f"Trace file not found: {trace_path}")
    return str(trace_path)
def _human_backend(data: dict[str, object]):
    insights = data["insights"]
    trace_server = data["trace_server"]
    click.echo("Resolved Backends:")
    click.echo(f"  UnrealInsights.exe : {insights['path']} ({insights['source']})")
    click.echo(f"  Version            : {insights.get('version') or 'unknown'}")
    if trace_server["available"]:
        click.echo(f"  UnrealTraceServer  : {trace_server['path']} ({trace_server['source']})")
        click.echo(f"  Version            : {trace_server.get('version') or 'unknown'}")
    else:
        click.echo(f"  UnrealTraceServer  : unavailable ({trace_server.get('error', 'not found')})")
def _human_ensure_insights(data: dict[str, object]):
    insights = data["insights"]
    click.echo(f"Engine root:       {data['engine_root']}")
    click.echo(f"UnrealInsights.exe {insights['path']} ({insights['source']})")
    click.echo(f"Version:           {insights.get('version') or 'unknown'}")
    trace_server = data.get("trace_server")
    if trace_server and trace_server.get("available"):
        click.echo(f"TraceServer:       {trace_server['path']}")
    build = data.get("build")
    if build:
        click.echo(f"Built:             {'yes' if build['succeeded'] else 'no'}")
        click.echo(f"Build log:         {build['log_path']}")
def _human_trace_info(data: dict[str, object]):
    trace_path = data.get("trace_path")
    if not trace_path:
        click.echo("No active trace selected.")
        return
    click.echo(f"Trace:   {trace_path}")
    click.echo(f"Exists:  {'yes' if data.get('exists') else 'no'}")
    if data.get("exists"):
        click.echo(f"Size:    {format_size(data.get('file_size'))}")
def _human_export_result(data: dict[str, object]):
    click.echo(f"Trace:     {data['trace_path']}")
    click.echo(f"Command:   {data['exec_command']}")
    click.echo(f"Log:       {data['log_path']}")
    click.echo(f"Exit code: {data['exit_code']}")
    click.echo(f"Status:    {data.get('output_status', 'unknown')}")
    click.echo(f"Success:   {'yes' if data['succeeded'] else 'no'}")
    if data.get("status_message"):
        click.echo(f"Message:   {data['status_message']}")
    if data["output_files"]:
        click.echo("Outputs:")
        for output_path in data["output_files"]:
            click.echo(f"  {output_path}")
    if data["errors"]:
        click.echo("Errors:")
        for line in data["errors"]:
            click.echo(f"  {line}")
def _human_capture_result(data: dict[str, object]):
    click.echo(f"Target exe:   {data['target_exe']}")
    if data.get("project_path"):
        click.echo(f"Project:      {data['project_path']}")
    if data.get("engine_root"):
        click.echo(f"Engine root:  {data['engine_root']}")
    click.echo(f"Trace output: {data['trace_path']}")
    click.echo(f"Channels:     {data['channels']}")
    click.echo(f"Command:      {' '.join(map(str, data['command']))}")
    if data["waited"]:
        click.echo(f"Exit code:    {data['exit_code']}")
        click.echo(f"Trace exists: {'yes' if data['trace_exists'] else 'no'}")
        if data["trace_exists"]:
            click.echo(f"Trace size:   {format_size(data['trace_size'])}")
    else:
        click.echo(f"PID:          {data['pid']}")
