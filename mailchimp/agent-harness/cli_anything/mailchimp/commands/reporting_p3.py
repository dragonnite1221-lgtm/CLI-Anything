# ruff: noqa: F403, F405, E501
from .reporting_base import *  # noqa: F403
# fmt: off
from .reporting_p1 import _parse_json_option, reporting_group  # noqa: E402,E501
# fmt: on


@reporting_group.command("list-reporting-surveys-id-questions")
@click.argument("SURVEY_ID")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_reporting_surveys_id_questions(ctx, survey_id, fields, exclude_fields, extra_params):
    """List survey question reports"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/reporting/surveys/{survey_id}/questions"
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
@reporting_group.command("get-reporting-surveys-id-questions-id")
@click.argument("SURVEY_ID")
@click.argument("QUESTION_ID")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_get_reporting_surveys_id_questions_id(ctx, survey_id, question_id, fields, exclude_fields, extra_params):
    """Get survey question report"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/reporting/surveys/{survey_id}/questions/{question_id}"
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
@reporting_group.command("list-reporting-surveys-id-questions-id-answers")
@click.argument("SURVEY_ID")
@click.argument("QUESTION_ID")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--respondent-familiarity-is", "respondent_familiarity_is", default=None, help="Filter survey responses by familiarity of the respondents.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_reporting_surveys_id_questions_id_answers(ctx, survey_id, question_id, fields, exclude_fields, respondent_familiarity_is, extra_params):
    """List answers for question"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/reporting/surveys/{survey_id}/questions/{question_id}/answers"
    params = {k: v for k, v in {
        "fields": fields,
        "exclude_fields": exclude_fields,
        "respondent_familiarity_is": respondent_familiarity_is,
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
@reporting_group.command("list-reporting-surveys-id-responses")
@click.argument("SURVEY_ID")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--answered-question", "answered_question", default=None, type=int, help="The ID of the question that was answered.")
@click.option("--chose-answer", "chose_answer", default=None, help="The ID of the option chosen to filter responses on.")
@click.option("--respondent-familiarity-is", "respondent_familiarity_is", default=None, help="Filter survey responses by familiarity of the respondents.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_reporting_surveys_id_responses(ctx, survey_id, fields, exclude_fields, answered_question, chose_answer, respondent_familiarity_is, extra_params):
    """List survey responses"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/reporting/surveys/{survey_id}/responses"
    params = {k: v for k, v in {
        "fields": fields,
        "exclude_fields": exclude_fields,
        "answered_question": answered_question,
        "chose_answer": chose_answer,
        "respondent_familiarity_is": respondent_familiarity_is,
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
