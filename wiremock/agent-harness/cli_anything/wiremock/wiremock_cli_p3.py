# ruff: noqa: F403, F405, E501
from .wiremock_cli_base import *  # noqa: F403

# fmt: off
from .wiremock_cli_p1 import cli  # noqa: E402,E501
from .wiremock_cli_p2 import request  # noqa: E402,E501
# fmt: on


@request.command("find")
@click.argument("pattern_json")
@click.pass_context
def request_find(ctx, pattern_json):
    """Find requests matching a pattern JSON."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        pattern = json.loads(pattern_json)
        data = RequestsLog(client).find(pattern)
        if json_mode:
            print_json(data)
        else:
            requests_list = data.get("requests", [])
            rows = [
                (
                    r.get("request", {}).get("method", ""),
                    r.get("request", {}).get("url", ""),
                    r.get("responseDefinition", {}).get("status", ""),
                )
                for r in requests_list
            ]
            print_table(
                ["Method", "URL", "Status"],
                rows,
                title=f"Matching requests ({len(requests_list)})",
            )
    except Exception as e:
        error(str(e), json_mode)


@request.command("count")
@click.argument("pattern_json")
@click.pass_context
def request_count(ctx, pattern_json):
    """Count requests matching a pattern JSON."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        pattern = json.loads(pattern_json)
        data = RequestsLog(client).count(pattern)
        if json_mode:
            print_json(data)
        else:
            click.echo(f"Count: {data.get('count', 0)}")
    except Exception as e:
        error(str(e), json_mode)


@request.command("unmatched")
@click.pass_context
def request_unmatched(ctx):
    """List unmatched requests."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        data = RequestsLog(client).unmatched()
        if json_mode:
            print_json(data)
        else:
            requests_list = data.get("requests", [])
            rows = [
                (
                    r.get("request", {}).get("method", ""),
                    r.get("request", {}).get("url", ""),
                )
                for r in requests_list
            ]
            print_table(
                ["Method", "URL"],
                rows,
                title=f"Unmatched requests ({len(requests_list)})",
            )
    except Exception as e:
        error(str(e), json_mode)


@request.command("reset")
@click.pass_context
def request_reset(ctx):
    """Clear the request journal."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        RequestsLog(client).reset()
        if json_mode:
            print_json({"status": "ok"})
        else:
            success("Request journal cleared")
    except Exception as e:
        error(str(e), json_mode)


@cli.group()
def scenario():
    """Manage state machine scenarios."""


@scenario.command("list")
@click.pass_context
def scenario_list(ctx):
    """List all scenarios."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        data = ScenariosManager(client).list()
        if json_mode:
            print_json(data)
        else:
            scenarios = data.get("scenarios", [])
            rows = [
                (
                    s.get("name", ""),
                    s.get("state", ""),
                    s.get("possibleStates", ""),
                )
                for s in scenarios
            ]
            print_table(
                ["Name", "Current State", "Possible States"],
                rows,
                title="Scenarios",
            )
    except Exception as e:
        error(str(e), json_mode)


@scenario.command("set")
@click.argument("name")
@click.argument("state")
@click.pass_context
def scenario_set(ctx, name, state):
    """Set a scenario state."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        ScenariosManager(client).set_state(name, state)
        if json_mode:
            print_json({"status": "ok"})
        else:
            success(f"Scenario '{name}' set to state '{state}'")
    except Exception as e:
        error(str(e), json_mode)


@scenario.command("reset")
@click.pass_context
def scenario_reset(ctx):
    """Reset all scenarios."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        ScenariosManager(client).reset_all()
        if json_mode:
            print_json({"status": "ok"})
        else:
            success("All scenarios reset")
    except Exception as e:
        error(str(e), json_mode)


@cli.group()
def record():
    """Record traffic from a real backend."""
