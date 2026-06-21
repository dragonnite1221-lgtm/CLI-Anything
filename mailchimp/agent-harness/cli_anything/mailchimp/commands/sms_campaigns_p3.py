# ruff: noqa: F403, F405, E501
from .sms_campaigns_base import *  # noqa: F403

# fmt: off
from .sms_campaigns_p1 import _parse_json_option, sms_campaigns_group  # noqa: E402,E501
# fmt: on


@sms_campaigns_group.command("update-sms-campaigns-id-content")
@click.argument("SMS_CAMPAIGN_ID")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option(
    "--extra-params",
    default=None,
    help='Extra query params as JSON object, e.g. \'{"key":"val"}\'',
)
@click.pass_context
def _cmd_update_sms_campaigns_id_content(ctx, sms_campaign_id, data, extra_params):
    """Set SMS campaign content"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err

    path = f"/sms-campaigns/{sms_campaign_id}/content"
    params = {}
    if extra_params:
        params.update(
            _parse_json_option(extra_params, "--extra-params", require_object=True)
        )
    body = _parse_json_option(data, "--data") if data else None
    client = get_client()
    try:
        result = client.put(path, json=body, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)
