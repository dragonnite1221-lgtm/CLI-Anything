# ruff: noqa: F403, F405, E501
from .lists_base import *  # noqa: F403


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
@click.group("lists")
@click.pass_context
def lists_group(ctx):
    """lists resource commands."""
@lists_group.command("list")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--count", "count", default=None, type=int, help="The number of records to return. Default value is 10. Maximum value is 1000")
@click.option("--offset", "offset", default=None, type=int, help="Used for [pagination](https://mailchimp.com/developer/marketing/docs/methods-parameters/#pagination), this is the number of records from a collection to skip. Default value is 0.")
@click.option("--before-date-created", "before_date_created", default=None, help="Restrict response to lists created before the set date. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--since-date-created", "since_date_created", default=None, help="Restrict results to lists created after the set date. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--before-campaign-last-sent", "before_campaign_last_sent", default=None, help="Restrict results to lists created before the last campaign send date. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--since-campaign-last-sent", "since_campaign_last_sent", default=None, help="Restrict results to lists created after the last campaign send date. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--email", "email", default=None, help="Restrict results to lists that include a specific subscriber's email address.")
@click.option("--sort-field", "sort_field", default=None, help="Returns files sorted by the specified field.")
@click.option("--sort-dir", "sort_dir", default=None, help="Determines the order direction for sorted results.")
@click.option("--has-ecommerce-store", "has_ecommerce_store", default=None, type=bool, help="Restrict results to lists that contain an active, connected, undeleted ecommerce store.")
@click.option("--include-total-contacts", "include_total_contacts", default=None, type=bool, help="Return the total_contacts field in the stats response, which contains an approximate count of all contacts in any state.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_(ctx, fields, exclude_fields, count, offset, before_date_created, since_date_created, before_campaign_last_sent, since_campaign_last_sent, email, sort_field, sort_dir, has_ecommerce_store, include_total_contacts, extra_params):
    """Get lists info"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists"
    params = {k: v for k, v in {
        "fields": fields,
        "exclude_fields": exclude_fields,
        "count": count,
        "offset": offset,
        "before_date_created": before_date_created,
        "since_date_created": since_date_created,
        "before_campaign_last_sent": before_campaign_last_sent,
        "since_campaign_last_sent": since_campaign_last_sent,
        "email": email,
        "sort_field": sort_field,
        "sort_dir": sort_dir,
        "has_ecommerce_store": has_ecommerce_store,
        "include_total_contacts": include_total_contacts,
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
@lists_group.command("create")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_create(ctx, data, extra_params):
    """Add list"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists"
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
@lists_group.command("delete")
@click.argument("LIST_ID")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_delete(ctx, list_id, extra_params):
    """Delete list"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}"
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
