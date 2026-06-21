# ruff: noqa: F403, F405, E501
from .lists_base import *  # noqa: F403
# fmt: off
from .lists_p1 import _parse_json_option, lists_group  # noqa: E402,E501
# fmt: on


@lists_group.command("get-lists-id-members-id")
@click.argument("LIST_ID")
@click.argument("SUBSCRIBER_HASH")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_get_lists_id_members_id(ctx, list_id, subscriber_hash, fields, exclude_fields, extra_params):
    """Get member info"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members/{subscriber_hash}"
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
@lists_group.command("update-lists-id-members-id")
@click.argument("LIST_ID")
@click.argument("SUBSCRIBER_HASH")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--skip-merge-validation", "skip_merge_validation", default=None, type=bool, help="If skip_merge_validation is true, member data will be accepted without merge field values, even if the merge field is usually required. This defaults to false.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_update_lists_id_members_id(ctx, list_id, subscriber_hash, data, skip_merge_validation, extra_params):
    """Update list member"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members/{subscriber_hash}"
    params = {k: v for k, v in {
        "skip_merge_validation": skip_merge_validation,
    }.items() if v is not None}
    if extra_params:
        params.update(_parse_json_option(extra_params, "--extra-params", require_object=True))
    body = _parse_json_option(data, "--data") if data else None
    client = get_client()
    try:
        result = client.patch(path, json=body, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)
@lists_group.command("update-3")
@click.argument("LIST_ID")
@click.argument("SUBSCRIBER_HASH")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--skip-merge-validation", "skip_merge_validation", default=None, type=bool, help="If skip_merge_validation is true, member data will be accepted without merge field values, even if the merge field is usually required. This defaults to false.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_update_3(ctx, list_id, subscriber_hash, data, skip_merge_validation, extra_params):
    """Add or update list member"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members/{subscriber_hash}"
    params = {k: v for k, v in {
        "skip_merge_validation": skip_merge_validation,
    }.items() if v is not None}
    if extra_params:
        params.update(_parse_json_option(extra_params, "--extra-params", require_object=True))
    body = _parse_json_option(data, "--data") if data else None
    client = get_client()
    try:
        result = client.put(path, json=body, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)
@lists_group.command("delete-permanent")
@click.argument("LIST_ID")
@click.argument("SUBSCRIBER_HASH")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_delete_permanent(ctx, list_id, subscriber_hash, extra_params):
    """Delete list member"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/members/{subscriber_hash}/actions/delete-permanent"
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
