# ruff: noqa: F403, F405, E501
from .landing_pages_base import *  # noqa: F403

# fmt: off
from .landing_pages_p1 import _parse_json_option, landing_pages_group  # noqa: E402,E501
# fmt: on


@landing_pages_group.command("list-landing-page-id-content")
@click.argument("PAGE_ID")
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
def _cmd_list_landing_page_id_content(
    ctx, page_id, fields, exclude_fields, extra_params
):
    """Get landing page content"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err

    path = f"/landing-pages/{page_id}/content"
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
