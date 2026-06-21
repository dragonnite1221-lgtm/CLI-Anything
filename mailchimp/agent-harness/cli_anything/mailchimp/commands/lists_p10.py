# ruff: noqa: F403, F405, E501
from .lists_base import *  # noqa: F403
# fmt: off
from .lists_p1 import _parse_json_option, lists_group  # noqa: E402,E501
# fmt: on


@lists_group.command("list-lists-id-members-id-goals")
@click.argument("LIST_ID")
@click.argument("SUBSCRIBER_HASH")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_lists_id_members_id_goals(ctx, list_id, subscriber_hash, fields, exclude_fields, extra_params):
    """List member goal events"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members/{subscriber_hash}/goals"
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
@lists_group.command("list-lists-id-members-id-notes")
@click.argument("LIST_ID")
@click.argument("SUBSCRIBER_HASH")
@click.option("--sort-field", "sort_field", default=None, help="Returns notes sorted by the specified field.")
@click.option("--sort-dir", "sort_dir", default=None, help="Determines the order direction for sorted results.")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--count", "count", default=None, type=int, help="The number of records to return. Default value is 10. Maximum value is 1000")
@click.option("--offset", "offset", default=None, type=int, help="Used for [pagination](https://mailchimp.com/developer/marketing/docs/methods-parameters/#pagination), this is the number of records from a collection to skip. Default value is 0.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_lists_id_members_id_notes(ctx, list_id, subscriber_hash, sort_field, sort_dir, fields, exclude_fields, count, offset, extra_params):
    """List recent member notes"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members/{subscriber_hash}/notes"
    params = {k: v for k, v in {
        "sort_field": sort_field,
        "sort_dir": sort_dir,
        "fields": fields,
        "exclude_fields": exclude_fields,
        "count": count,
        "offset": offset,
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
@lists_group.command("create-lists-id-members-id-notes")
@click.argument("LIST_ID")
@click.argument("SUBSCRIBER_HASH")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_create_lists_id_members_id_notes(ctx, list_id, subscriber_hash, data, extra_params):
    """Add member note"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members/{subscriber_hash}/notes"
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
@lists_group.command("delete-lists-id-members-id-notes-id")
@click.argument("LIST_ID")
@click.argument("SUBSCRIBER_HASH")
@click.argument("NOTE_ID")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_delete_lists_id_members_id_notes_id(ctx, list_id, subscriber_hash, note_id, extra_params):
    """Delete note"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members/{subscriber_hash}/notes/{note_id}"
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
