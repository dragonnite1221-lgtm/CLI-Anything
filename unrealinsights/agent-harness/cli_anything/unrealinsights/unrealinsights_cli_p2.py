# ruff: noqa: F403, F405, E501
from .unrealinsights_cli_base import *  # noqa: F403


def _human_capture_status(data: dict[str, object]):
    if not data.get("active"):
        click.echo("No tracked capture session.")
        return
    click.echo(f"PID:          {data.get('pid')}")
    click.echo(f"Running:      {'yes' if data.get('running') else 'no'}")
    click.echo(f"Target exe:   {data.get('target_exe')}")
    if data.get("project_path"):
        click.echo(f"Project:      {data['project_path']}")
    if data.get("engine_root"):
        click.echo(f"Engine root:  {data['engine_root']}")
    click.echo(f"Trace:        {data.get('trace_path')}")
    click.echo(f"Trace exists: {'yes' if data.get('trace_exists') else 'no'}")
    if data.get("trace_exists"):
        click.echo(f"Trace size:   {format_size(data.get('trace_size'))}")
    if data.get("started_at"):
        click.echo(f"Started at:   {data['started_at']}")
def _human_snapshot_result(data: dict[str, object]):
    click.echo(f"Source trace:   {data['source_trace']}")
    click.echo(f"Snapshot trace: {data['snapshot_trace']}")
    click.echo(f"Exists:         {'yes' if data['snapshot_exists'] else 'no'}")
    if data.get("snapshot_exists"):
        click.echo(f"Size:           {format_size(data.get('snapshot_size'))}")
    click.echo(f"Capture running:{' yes' if data.get('capture_running') else ' no'}")
def _human_stop_result(data: dict[str, object]):
    termination = data["termination"]
    click.echo(f"Requested PID: {termination['requested_pid']}")
    click.echo(f"Stopped:       {'yes' if termination['stopped'] else 'no'}")
    click.echo(f"Exit code:     {termination.get('exit_code')}")
def _human_store_info(data: dict[str, object]):
    click.echo(f"Trace root:    {data['trace_root']}")
    click.echo(f"Store:         {data['store_dir']}")
    click.echo(f"Store exists:  {'yes' if data['store_exists'] else 'no'}")
    click.echo(f"Trace files:   {data['trace_file_count']}")
    trace_server = data["trace_server"]
    if trace_server.get("available"):
        click.echo(f"TraceServer:   {trace_server['path']}")
    else:
        click.echo(f"TraceServer:   unavailable ({trace_server.get('error', 'not found')})")
def _human_store_list(data: dict[str, object]):
    click.echo(f"Store:       {data['store_dir']}")
    click.echo(f"Trace count: {data['trace_count']}")
    for trace in data["traces"][:20]:
        live = " live?" if trace.get("is_live_candidate") else ""
        click.echo(f"  {trace['path']} ({format_size(trace.get('file_size'))}){live}")
def _human_store_latest(data: dict[str, object]):
    latest = data.get("latest")
    if not latest:
        click.echo("No trace file found.")
        return
    click.echo(f"Latest trace: {latest['path']}")
    click.echo(f"Size:         {format_size(latest.get('file_size'))}")
    click.echo(f"Live guess:   {'yes' if latest.get('is_live_candidate') else 'no'}")
    if data.get("set_current"):
        click.echo("Current session trace updated.")
def _human_processes(data: dict[str, object]):
    click.echo(f"Processes: {data['process_count']}")
    for process in data["processes"]:
        click.echo(f"  {process['pid']}  {process['role']}  {process['name']}  {process.get('path') or ''}")
def _human_live_result(data: dict[str, object]):
    click.echo(f"PID:      {data['pid']}")
    click.echo(f"Command:  {data['live_command']}")
    click.echo(f"Backend:  {data['backend']}")
    click.echo(f"Exit:     {data['exit_code']}")
    click.echo(f"Success:  {'yes' if data['succeeded'] else 'no'}")
    if data.get("stdout"):
        click.echo(data["stdout"])
    if data.get("stderr"):
        click.echo(data["stderr"])
def _human_gui_status(data: dict[str, object]):
    click.echo(f"Unreal Insights GUI running: {'yes' if data['running'] else 'no'}")
    for process in data["processes"]:
        click.echo(f"  {process['pid']}  {process.get('path') or process['name']}")
def _human_gui_open(data: dict[str, object]):
    click.echo(f"UnrealInsights.exe: {data['insights_exe']}")
    if data.get("trace_path"):
        click.echo(f"Trace:              {data['trace_path']}")
    click.echo(f"PID:                {data['pid']}")
    click.echo("Mode:               GUI kept running")
def _human_analyze_summary(data: dict[str, object]):
    click.echo(f"Trace:   {data.get('trace_path') or 'not supplied'}")
    click.echo(f"Out dir: {data['out_dir']}")
    click.echo(f"Success: {'yes' if data['succeeded'] else 'no'}")
    top_timers = data["summary"].get("top_timers", [])
    if top_timers:
        click.echo("Top timers:")
        for entry in top_timers[:10]:
            click.echo(f"  {entry['name']}  score={entry.get('score')}")
    if data.get("warnings"):
        click.echo("Warnings:")
        for warning in data["warnings"]:
            click.echo(f"  {warning}")
