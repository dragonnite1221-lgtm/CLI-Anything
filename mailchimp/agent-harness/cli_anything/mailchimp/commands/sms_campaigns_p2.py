# ruff: noqa: F403, F405, E501
from .sms_campaigns_base import *  # noqa: F403

# fmt: off
from .sms_campaigns_p1 import _parse_json_option, sms_campaigns_group  # noqa: E402,E501
# fmt: on


@sms_campaigns_group.command("update")
@click.argument("SMS_CAMPAIGN_ID")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option(
    "--extra-params",
    default=None,
    help='Extra query params as JSON object, e.g. \'{"key":"val"}\'',
)
@click.pass_context
def _cmd_update(ctx, sms_campaign_id, data, extra_params):
    """Update SMS campaign settings"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err

    path = f"/sms-campaigns/{sms_campaign_id}"
    params = {}
    if extra_params:
        params.update(
            _parse_json_option(extra_params, "--extra-params", require_object=True)
        )
    body = _parse_json_option(data, "--data") if data else None
    client = get_client()
    try:
        result = client.patch(path, json=body, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)


@sms_campaigns_group.command("cancel-send")
@click.argument("SMS_CAMPAIGN_ID")
@click.option(
    "--extra-params",
    default=None,
    help='Extra query params as JSON object, e.g. \'{"key":"val"}\'',
)
@click.pass_context
def _cmd_cancel_send(ctx, sms_campaign_id, extra_params):
    """Cancel SMS campaign send"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err

    path = f"/sms-campaigns/{sms_campaign_id}/actions/cancel-send"
    params = {}
    if extra_params:
        params.update(
            _parse_json_option(extra_params, "--extra-params", require_object=True)
        )
    client = get_client()
    try:
        result = client.post(path, json=None, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)


@sms_campaigns_group.command("schedule")
@click.argument("SMS_CAMPAIGN_ID")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option(
    "--extra-params",
    default=None,
    help='Extra query params as JSON object, e.g. \'{"key":"val"}\'',
)
@click.pass_context
def _cmd_schedule(ctx, sms_campaign_id, data, extra_params):
    """Schedule SMS campaign"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err

    path = f"/sms-campaigns/{sms_campaign_id}/actions/schedule"
    params = {}
    if extra_params:
        params.update(
            _parse_json_option(extra_params, "--extra-params", require_object=True)
        )
    body = _parse_json_option(data, "--data") if data else None
    client = get_client()
    try:
        result = client.post(path, json=body, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)


@sms_campaigns_group.command("send")
@click.argument("SMS_CAMPAIGN_ID")
@click.option(
    "--extra-params",
    default=None,
    help='Extra query params as JSON object, e.g. \'{"key":"val"}\'',
)
@click.pass_context
def _cmd_send(ctx, sms_campaign_id, extra_params):
    """Send SMS campaign"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err

    path = f"/sms-campaigns/{sms_campaign_id}/actions/send"
    params = {}
    if extra_params:
        params.update(
            _parse_json_option(extra_params, "--extra-params", require_object=True)
        )
    client = get_client()
    try:
        result = client.post(path, json=None, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)


@sms_campaigns_group.command("list-sms-campaigns-id-content")
@click.argument("SMS_CAMPAIGN_ID")
@click.option(
    "--fields",
    "fields",
    default=None,
    help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.",
)
@click.option(
    "--exclude-fields",
    "exclude_fields",
    default=None,
    help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.",
)
@click.option(
    "--extra-params",
    default=None,
    help='Extra query params as JSON object, e.g. \'{"key":"val"}\'',
)
@click.pass_context
def _cmd_list_sms_campaigns_id_content(
    ctx, sms_campaign_id, fields, exclude_fields, extra_params
):
    """Get SMS campaign content"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err

    path = f"/sms-campaigns/{sms_campaign_id}/content"
    params = {
        k: v
        for k, v in {
            "fields": fields,
            "exclude_fields": exclude_fields,
        }.items()
        if v is not None
    }
    if extra_params:
        params.update(
            _parse_json_option(extra_params, "--extra-params", require_object=True)
        )
    client = get_client()
    try:
        result = client.get(path, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)
