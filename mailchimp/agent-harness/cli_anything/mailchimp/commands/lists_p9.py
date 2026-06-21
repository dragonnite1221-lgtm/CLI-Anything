# ruff: noqa: F403, F405, E501
from .lists_base import *  # noqa: F403
# fmt: off
from .lists_p1 import _parse_json_option, lists_group  # noqa: E402,E501
# fmt: on


@lists_group.command("list-lists-id-members-id-activity")
@click.argument("LIST_ID")
@click.argument("SUBSCRIBER_HASH")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--action", "action", default=None, help="A comma seperated list of actions to return.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_lists_id_members_id_activity(ctx, list_id, subscriber_hash, fields, exclude_fields, action, extra_params):
    """View recent activity 50"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members/{subscriber_hash}/activity"
    params = {k: v for k, v in {
        "fields": fields,
        "exclude_fields": exclude_fields,
        "action": action,
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
@lists_group.command("list-lists-id-members-id-activity-feed")
@click.argument("LIST_ID")
@click.argument("SUBSCRIBER_HASH")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--count", "count", default=None, type=int, help="The number of records to return. Default value is 10. Maximum value is 1000")
@click.option("--offset", "offset", default=None, type=int, help="Used for [pagination](https://mailchimp.com/developer/marketing/docs/methods-parameters/#pagination), this is the number of records from a collection to skip. Default value is 0.")
@click.option("--activity-filters", "activity_filters", default=None, help="A comma-separated list of activity filters that correspond to a set of activity types, e.g \"?activity_filters=open,bounce,click\".")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_lists_id_members_id_activity_feed(ctx, list_id, subscriber_hash, fields, exclude_fields, count, offset, activity_filters, extra_params):
    """View recent activity"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members/{subscriber_hash}/activity-feed"
    params = {k: v for k, v in {
        "fields": fields,
        "exclude_fields": exclude_fields,
        "count": count,
        "offset": offset,
        "activity_filters": activity_filters,
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
@lists_group.command("list-lists-id-members-id-events")
@click.argument("LIST_ID")
@click.argument("SUBSCRIBER_HASH")
@click.option("--count", "count", default=None, type=int, help="The number of records to return. Default value is 10. Maximum value is 1000")
@click.option("--offset", "offset", default=None, type=int, help="Used for [pagination](https://mailchimp.com/developer/marketing/docs/methods-parameters/#pagination), this is the number of records from a collection to skip. Default value is 0.")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_lists_id_members_id_events(ctx, list_id, subscriber_hash, count, offset, fields, exclude_fields, extra_params):
    """List member events"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members/{subscriber_hash}/events"
    params = {k: v for k, v in {
        "count": count,
        "offset": offset,
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
@lists_group.command("create-list-member-events")
@click.argument("LIST_ID")
@click.argument("SUBSCRIBER_HASH")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_create_list_member_events(ctx, list_id, subscriber_hash, data, extra_params):
    """Add event"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members/{subscriber_hash}/events"
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
