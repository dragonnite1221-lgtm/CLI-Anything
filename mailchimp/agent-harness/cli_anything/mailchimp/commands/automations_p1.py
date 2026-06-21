# ruff: noqa: F403, F405, E501
from .automations_base import *  # noqa: F403


def _parse_json_option(value, option_name, require_object=False):
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise click.BadParameter(
            f"must be valid JSON ({exc.msg})",
            param_hint=option_name,
        ) from exc
    if require_object and not isinstance(parsed, dict):
        raise click.BadParameter("must be a JSON object", param_hint=option_name)
    return parsed
@click.group("automations")
@click.pass_context
def automations_group(ctx):
    """automations resource commands."""
@automations_group.command("list")
@click.option("--count", "count", default=None, type=int, help="The number of records to return. Default value is 10. Maximum value is 1000")
@click.option("--offset", "offset", default=None, type=int, help="Used for [pagination](https://mailchimp.com/developer/marketing/docs/methods-parameters/#pagination), this is the number of records from a collection to skip. Default value is 0.")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--before-create-time", "before_create_time", default=None, help="Restrict the response to automations created before this time. Uses the ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--since-create-time", "since_create_time", default=None, help="Restrict the response to automations created after this time. Uses the ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--before-start-time", "before_start_time", default=None, help="Restrict the response to automations started before this time. Uses the ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--since-start-time", "since_start_time", default=None, help="Restrict the response to automations started after this time. Uses the ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--status", "status", default=None, help="Restrict the results to automations with the specified status.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_(ctx, count, offset, fields, exclude_fields, before_create_time, since_create_time, before_start_time, since_start_time, status, extra_params):
    """List automations"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/automations"
    params = {k: v for k, v in {
        "count": count,
        "offset": offset,
        "fields": fields,
        "exclude_fields": exclude_fields,
        "before_create_time": before_create_time,
        "since_create_time": since_create_time,
        "before_start_time": before_start_time,
        "since_start_time": since_start_time,
        "status": status,
    }.items() if v is not None}
    if extra_params:
        params.update(_parse_json_option(extra_params, "--extra-params", require_object=True))
    client = get_client()
    try:
        result = client.get(path, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)
@automations_group.command("create")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_create(ctx, data, extra_params):
    """Add automation"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/automations"
    params = {}
    if extra_params:
        params.update(_parse_json_option(extra_params, "--extra-params", require_object=True))
    body = _parse_json_option(data, "--data") if data else None
    client = get_client()
    try:
        result = client.post(path, json=body, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)
@automations_group.command("get")
@click.argument("WORKFLOW_ID")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_get(ctx, workflow_id, fields, exclude_fields, extra_params):
    """Get automation info"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/automations/{workflow_id}"
    params = {k: v for k, v in {
        "fields": fields,
        "exclude_fields": exclude_fields,
    }.items() if v is not None}
    if extra_params:
        params.update(_parse_json_option(extra_params, "--extra-params", require_object=True))
    client = get_client()
    try:
        result = client.get(path, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)
@automations_group.command("archive")
@click.argument("WORKFLOW_ID")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_archive(ctx, workflow_id, extra_params):
    """Archive automation"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/automations/{workflow_id}/actions/archive"
    params = {}
    if extra_params:
        params.update(_parse_json_option(extra_params, "--extra-params", require_object=True))
    client = get_client()
    try:
        result = client.post(path, json=None, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)
