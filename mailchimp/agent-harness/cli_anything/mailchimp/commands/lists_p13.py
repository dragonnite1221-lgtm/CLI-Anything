# ruff: noqa: F403, F405, E501
from .lists_base import *  # noqa: F403
# fmt: off
from .lists_p1 import _parse_json_option, lists_group  # noqa: E402,E501
# fmt: on


@lists_group.command("list-preview-a-segment")
@click.argument("LIST_ID")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--count", "count", default=None, type=int, help="The number of records to return. Default value is 10. Maximum value is 1000")
@click.option("--offset", "offset", default=None, type=int, help="Used for [pagination](https://mailchimp.com/developer/marketing/docs/methods-parameters/#pagination), this is the number of records from a collection to skip. Default value is 0.")
@click.option("--type", "type_", default=None, help="Limit results based on segment type.")
@click.option("--since-created-at", "since_created_at", default=None, help="Restrict results to segments created after the set time. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--before-created-at", "before_created_at", default=None, help="Restrict results to segments created before the set time. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--include-cleaned", "include_cleaned", default=None, type=bool, help="Include cleaned members in response")
@click.option("--include-transactional", "include_transactional", default=None, type=bool, help="Include transactional members in response")
@click.option("--include-unsubscribed", "include_unsubscribed", default=None, type=bool, help="Include unsubscribed members in response")
@click.option("--since-updated-at", "since_updated_at", default=None, help="Restrict results to segments update after the set time. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--before-updated-at", "before_updated_at", default=None, help="Restrict results to segments update before the set time. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--exclude-type", "exclude_type", default=None, help="Exclude results based on segment type. For example, use `exclude_type=static` to exclude tags from the response.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_preview_a_segment(ctx, list_id, fields, exclude_fields, count, offset, type_, since_created_at, before_created_at, include_cleaned, include_transactional, include_unsubscribed, since_updated_at, before_updated_at, exclude_type, extra_params):
    """List segments"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/segments"
    params = {k: v for k, v in {
        "fields": fields,
        "exclude_fields": exclude_fields,
        "count": count,
        "offset": offset,
        "type": type_,
        "since_created_at": since_created_at,
        "before_created_at": before_created_at,
        "include_cleaned": include_cleaned,
        "include_transactional": include_transactional,
        "include_unsubscribed": include_unsubscribed,
        "since_updated_at": since_updated_at,
        "before_updated_at": before_updated_at,
        "exclude_type": exclude_type,
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
lists_group.add_command(_cmd_list_preview_a_segment, "list-lists-id-segments")
@lists_group.command("create-lists-id-segments")
@click.argument("LIST_ID")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_create_lists_id_segments(ctx, list_id, data, extra_params):
    """Add segment"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/segments"
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
@lists_group.command("delete-lists-id-segments-id")
@click.argument("LIST_ID")
@click.argument("SEGMENT_ID")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_delete_lists_id_segments_id(ctx, list_id, segment_id, extra_params):
    """Delete segment"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/segments/{segment_id}"
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
@lists_group.command("get-lists-id-segments-id")
@click.argument("LIST_ID")
@click.argument("SEGMENT_ID")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--include-cleaned", "include_cleaned", default=None, type=bool, help="Include cleaned members in response")
@click.option("--include-transactional", "include_transactional", default=None, type=bool, help="Include transactional members in response")
@click.option("--include-unsubscribed", "include_unsubscribed", default=None, type=bool, help="Include unsubscribed members in response")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_get_lists_id_segments_id(ctx, list_id, segment_id, fields, exclude_fields, include_cleaned, include_transactional, include_unsubscribed, extra_params):
    """Get segment info"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/segments/{segment_id}"
    params = {k: v for k, v in {
        "fields": fields,
        "exclude_fields": exclude_fields,
        "include_cleaned": include_cleaned,
        "include_transactional": include_transactional,
        "include_unsubscribed": include_unsubscribed,
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
