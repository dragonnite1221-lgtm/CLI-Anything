# ruff: noqa: F403, F405, E501
from .automations_base import *  # noqa: F403
# fmt: off
from .automations_p1 import _parse_json_option, automations_group  # noqa: E402,E501
# fmt: on


@automations_group.command("pause")
@click.argument("WORKFLOW_ID")
@click.argument("WORKFLOW_EMAIL_ID")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_pause(ctx, workflow_id, workflow_email_id, extra_params):
    """Pause automated email"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/automations/{workflow_id}/emails/{workflow_email_id}/actions/pause"
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
@automations_group.command("start")
@click.argument("WORKFLOW_ID")
@click.argument("WORKFLOW_EMAIL_ID")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_start(ctx, workflow_id, workflow_email_id, extra_params):
    """Start automated email"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/automations/{workflow_id}/emails/{workflow_email_id}/actions/start"
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
@automations_group.command("list-automations-id-emails-id-queue")
@click.argument("WORKFLOW_ID")
@click.argument("WORKFLOW_EMAIL_ID")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_automations_id_emails_id_queue(ctx, workflow_id, workflow_email_id, extra_params):
    """List automated email subscribers"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/automations/{workflow_id}/emails/{workflow_email_id}/queue"
    params = {}
    if extra_params:
        params.update(_parse_json_option(extra_params, "--extra-params", require_object=True))
    client = get_client()
    try:
        result = client.get(path, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)
@automations_group.command("create-automations-id-emails-id-queue")
@click.argument("WORKFLOW_ID")
@click.argument("WORKFLOW_EMAIL_ID")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_create_automations_id_emails_id_queue(ctx, workflow_id, workflow_email_id, data, extra_params):
    """Add subscriber to workflow email"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/automations/{workflow_id}/emails/{workflow_email_id}/queue"
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
@automations_group.command("get-automations-id-emails-id-queue-id")
@click.argument("WORKFLOW_ID")
@click.argument("WORKFLOW_EMAIL_ID")
@click.argument("SUBSCRIBER_HASH")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_get_automations_id_emails_id_queue_id(ctx, workflow_id, workflow_email_id, subscriber_hash, extra_params):
    """Get automated email subscriber"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/automations/{workflow_id}/emails/{workflow_email_id}/queue/{subscriber_hash}"
    params = {}
    if extra_params:
        params.update(_parse_json_option(extra_params, "--extra-params", require_object=True))
    client = get_client()
    try:
        result = client.get(path, params=params or None)
    except MailchimpError as e:
        _out_err(e.status, e.title, e.detail, e.raw)
        return
    _out(result)
