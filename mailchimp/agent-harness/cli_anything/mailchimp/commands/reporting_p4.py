# ruff: noqa: F403, F405, E501
from .reporting_base import *  # noqa: F403
# fmt: off
from .reporting_p1 import _parse_json_option, reporting_group  # noqa: E402,E501
# fmt: on


@reporting_group.command("get-reporting-surveys-id-responses-id")
@click.argument("SURVEY_ID")
@click.argument("RESPONSE_ID")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_get_reporting_surveys_id_responses_id(ctx, survey_id, response_id, extra_params):
    """Get survey response"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/reporting/surveys/{survey_id}/responses/{response_id}"
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
