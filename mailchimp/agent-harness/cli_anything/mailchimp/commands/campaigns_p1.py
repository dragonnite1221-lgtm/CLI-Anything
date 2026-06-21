# ruff: noqa: F403, F405, E501
from .campaigns_base import *  # noqa: F403


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
@click.group("campaigns")
@click.pass_context
def campaigns_group(ctx):
    """campaigns resource commands."""
@campaigns_group.command("list")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--count", "count", default=None, type=int, help="The number of records to return. Default value is 10. Maximum value is 1000")
@click.option("--offset", "offset", default=None, type=int, help="Used for [pagination](https://mailchimp.com/developer/marketing/docs/methods-parameters/#pagination), this is the number of records from a collection to skip. Default value is 0.")
@click.option("--type", "type_", default=None, help="The campaign type.")
@click.option("--status", "status", default=None, help="The status of the campaign.")
@click.option("--before-send-time", "before_send_time", default=None, help="Restrict the response to campaigns sent before the set time. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--since-send-time", "since_send_time", default=None, help="Restrict the response to campaigns sent after the set time. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--before-create-time", "before_create_time", default=None, help="Restrict the response to campaigns created before the set time. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--since-create-time", "since_create_time", default=None, help="Restrict the response to campaigns created after the set time. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--list-id", "list_id", default=None, help="The unique id for the list.")
@click.option("--folder-id", "folder_id", default=None, help="The unique folder id.")
@click.option("--member-id", "member_id", default=None, help="Retrieve campaigns sent to a particular list member. Member ID is The MD5 hash of the lowercase version of the list member’s email address.")
@click.option("--sort-field", "sort_field", default=None, help="Returns files sorted by the specified field.")
@click.option("--sort-dir", "sort_dir", default=None, help="Determines the order direction for sorted results.")
@click.option("--include-resend-shortcut-eligibility", "include_resend_shortcut_eligibility", default=None, type=bool, help="Return the `resend_shortcut_eligibility` field in the response, which tells you if the campaign is eligible for the various Campaign Resend Shortcuts offered.")
@click.option("--include-resend-shortcut-usage", "include_resend_shortcut_usage", default=None, type=bool, help="Return the `resend_shortcut_usage` field in the response. This includes information about campaigns related by a shortcut.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_(ctx, fields, exclude_fields, count, offset, type_, status, before_send_time, since_send_time, before_create_time, since_create_time, list_id, folder_id, member_id, sort_field, sort_dir, include_resend_shortcut_eligibility, include_resend_shortcut_usage, extra_params):
    """List campaigns"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/campaigns"
    params = {k: v for k, v in {
        "fields": fields,
        "exclude_fields": exclude_fields,
        "count": count,
        "offset": offset,
        "type": type_,
        "status": status,
        "before_send_time": before_send_time,
        "since_send_time": since_send_time,
        "before_create_time": before_create_time,
        "since_create_time": since_create_time,
        "list_id": list_id,
        "folder_id": folder_id,
        "member_id": member_id,
        "sort_field": sort_field,
        "sort_dir": sort_dir,
        "include_resend_shortcut_eligibility": include_resend_shortcut_eligibility,
        "include_resend_shortcut_usage": include_resend_shortcut_usage,
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
@campaigns_group.command("create")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_create(ctx, data, extra_params):
    """Add campaign"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/campaigns"
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
@campaigns_group.command("delete")
@click.argument("CAMPAIGN_ID")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_delete(ctx, campaign_id, extra_params):
    """Delete campaign"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/campaigns/{campaign_id}"
    params = {}
    if extra_params:
        params.update(_parse_json_option(extra_params, "--extra-params", require_object=True))
    client = get_client()
    try:
        result = client.delete(path, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out_ok("Deleted.")
