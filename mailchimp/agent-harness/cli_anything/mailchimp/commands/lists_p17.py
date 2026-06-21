# ruff: noqa: F403, F405, E501
from .lists_base import *  # noqa: F403
# fmt: off
from .lists_p1 import _parse_json_option, lists_group  # noqa: E402,E501
# fmt: on


@lists_group.command("update-lists-id-webhooks-id")
@click.argument("LIST_ID")
@click.argument("WEBHOOK_ID")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_update_lists_id_webhooks_id(ctx, list_id, webhook_id, data, extra_params):
    """Update webhook"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/lists/{list_id}/webhooks/{webhook_id}"
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
