# ruff: noqa: F403, F405, E501
from .file_manager_base import *  # noqa: F403
# fmt: off
from .file_manager_p1 import _parse_json_option, file_manager_group  # noqa: E402,E501
# fmt: on


@file_manager_group.command("update-file-manager-folders-id")
@click.argument("FOLDER_ID")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_update_file_manager_folders_id(ctx, folder_id, data, extra_params):
    """Update folder"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/file-manager/folders/{folder_id}"
    params = {}
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
@file_manager_group.command("list-file-manager-folders-files")
@click.argument("FOLDER_ID")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--count", "count", default=None, type=int, help="The number of records to return. Default value is 10. Maximum value is 1000")
@click.option("--offset", "offset", default=None, type=int, help="Used for [pagination](https://mailchimp.com/developer/marketing/docs/methods-parameters/#pagination), this is the number of records from a collection to skip. Default value is 0.")
@click.option("--type", "type_", default=None, help="The file type for the File Manager file.")
@click.option("--created-by", "created_by", default=None, help="The Mailchimp account user who created the File Manager file.")
@click.option("--before-created-at", "before_created_at", default=None, help="Restrict the response to files created before the set date. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--since-created-at", "since_created_at", default=None, help="Restrict the response to files created after the set date. Uses ISO 8601 time format: 2015-10-21T15:41:36+00:00.")
@click.option("--sort-field", "sort_field", default=None, help="Returns files sorted by the specified field.")
@click.option("--sort-dir", "sort_dir", default=None, help="Determines the order direction for sorted results.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_file_manager_folders_files(ctx, folder_id, fields, exclude_fields, count, offset, type_, created_by, before_created_at, since_created_at, sort_field, sort_dir, extra_params):
    """List stored files"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/file-manager/folders/{folder_id}/files"
    params = {k: v for k, v in {
        "fields": fields,
        "exclude_fields": exclude_fields,
        "count": count,
        "offset": offset,
        "type": type_,
        "created_by": created_by,
        "before_created_at": before_created_at,
        "since_created_at": since_created_at,
        "sort_field": sort_field,
        "sort_dir": sort_dir,
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
