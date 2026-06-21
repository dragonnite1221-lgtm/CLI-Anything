# ruff: noqa: F403, F405, E501
from .lists_base import *  # noqa: F403
# fmt: off
from .lists_p1 import _parse_json_option, lists_group  # noqa: E402,E501
# fmt: on


@lists_group.command("list-lists-id-members")
@click.argument("LIST_ID")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--count", "count", default=None, type=int, help="The number of records to return. Default value is 10. Maximum value is 1000")
@click.option("--offset", "offset", default=None, type=int, help="Used for [pagination](https://mailchimp.com/developer/marketing/docs/methods-parameters/#pagination), this is the number of records from a collection to skip. Default value is 0.")
@click.option("--email-type", "email_type", default=None, help="The email type.")
@click.option("--status", "status", default=None, help="The subscriber's status.")
@click.option("--since-timestamp-opt", "since_timestamp_opt", default=None, help="Restrict results to subscribers who opted-in after the set timeframe. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--before-timestamp-opt", "before_timestamp_opt", default=None, help="Restrict results to subscribers who opted-in before the set timeframe. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--since-last-changed", "since_last_changed", default=None, help="Restrict results to subscribers whose information changed after the set timeframe. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--before-last-changed", "before_last_changed", default=None, help="Restrict results to subscribers whose information changed before the set timeframe. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--unique-email-id", "unique_email_id", default=None, help="A unique identifier for the email address across all Mailchimp lists.")
@click.option("--vip-only", "vip_only", default=None, type=bool, help="A filter to return only the list's VIP members. Passing `true` will restrict results to VIP list members, passing `false` will return all list members.")
@click.option("--interest-category-id", "interest_category_id", default=None, help="The unique id for the interest category.")
@click.option("--interest-ids", "interest_ids", default=None, help="Used to filter list members by interests. Must be accompanied by interest_category_id and interest_match. The value must be a comma separated list of interest ids present for any supplied interest categories.")
@click.option("--interest-match", "interest_match", default=None, help="Used to filter list members by interests. Must be accompanied by interest_category_id and interest_ids. \"any\" will match a member with any of the interest supplied, \"all\" will only match members with every interest supplied, and \"none\" will match members without any of the interest supplied.")
@click.option("--sort-field", "sort_field", default=None, help="Returns files sorted by the specified field.")
@click.option("--sort-dir", "sort_dir", default=None, help="Determines the order direction for sorted results.")
@click.option("--since-last-campaign", "since_last_campaign", default=None, type=bool, help="Filter subscribers by those subscribed/unsubscribed/pending/cleaned since last email campaign send. Member status is required to use this filter.")
@click.option("--unsubscribed-since", "unsubscribed_since", default=None, help="Filter subscribers by those unsubscribed since a specific date. Using any status other than unsubscribed with this filter will result in an error.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_lists_id_members(ctx, list_id, fields, exclude_fields, count, offset, email_type, status, since_timestamp_opt, before_timestamp_opt, since_last_changed, before_last_changed, unique_email_id, vip_only, interest_category_id, interest_ids, interest_match, sort_field, sort_dir, since_last_campaign, unsubscribed_since, extra_params):
    """List members info"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members"
    params = {k: v for k, v in {
        "fields": fields,
        "exclude_fields": exclude_fields,
        "count": count,
        "offset": offset,
        "email_type": email_type,
        "status": status,
        "since_timestamp_opt": since_timestamp_opt,
        "before_timestamp_opt": before_timestamp_opt,
        "since_last_changed": since_last_changed,
        "before_last_changed": before_last_changed,
        "unique_email_id": unique_email_id,
        "vip_only": vip_only,
        "interest_category_id": interest_category_id,
        "interest_ids": interest_ids,
        "interest_match": interest_match,
        "sort_field": sort_field,
        "sort_dir": sort_dir,
        "since_last_campaign": since_last_campaign,
        "unsubscribed_since": unsubscribed_since,
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
@lists_group.command("create-lists-id-members")
@click.argument("LIST_ID")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--skip-merge-validation", "skip_merge_validation", default=None, type=bool, help="If skip_merge_validation is true, member data will be accepted without merge field values, even if the merge field is usually required. This defaults to false.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_create_lists_id_members(ctx, list_id, data, skip_merge_validation, extra_params):
    """Add member to list"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members"
    params = {k: v for k, v in {
        "skip_merge_validation": skip_merge_validation,
    }.items() if v is not None}
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
lists_group.add_command(_cmd_create_lists_id_members, "create-members")
@lists_group.command("delete-lists-id-members-id")
@click.argument("LIST_ID")
@click.argument("SUBSCRIBER_HASH")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_delete_lists_id_members_id(ctx, list_id, subscriber_hash, extra_params):
    """Archive list member"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members/{subscriber_hash}"
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
