# ruff: noqa: F403, F405, E501
from .ecommerce_base import *  # noqa: F403
# fmt: off
from .ecommerce_p1 import _parse_json_option, ecommerce_group  # noqa: E402,E501
# fmt: on


@ecommerce_group.command("get-ecommerce-stores-id-carts-id-lines-id")
@click.argument("STORE_ID")
@click.argument("CART_ID")
@click.argument("LINE_ID")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_get_ecommerce_stores_id_carts_id_lines_id(ctx, store_id, cart_id, line_id, fields, exclude_fields, extra_params):
    """Get cart line item"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/ecommerce/stores/{store_id}/carts/{cart_id}/lines/{line_id}"
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
@ecommerce_group.command("update-ecommerce-stores-id-carts-id-lines-id")
@click.argument("STORE_ID")
@click.argument("CART_ID")
@click.argument("LINE_ID")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_update_ecommerce_stores_id_carts_id_lines_id(ctx, store_id, cart_id, line_id, data, extra_params):
    """Update cart line item"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/ecommerce/stores/{store_id}/carts/{cart_id}/lines/{line_id}"
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
@ecommerce_group.command("list-ecommerce-stores-id-customers")
@click.argument("STORE_ID")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--count", "count", default=None, type=int, help="The number of records to return. Default value is 10. Maximum value is 1000")
@click.option("--offset", "offset", default=None, type=int, help="Used for [pagination](https://mailchimp.com/developer/marketing/docs/methods-parameters/#pagination), this is the number of records from a collection to skip. Default value is 0.")
@click.option("--email-address", "email_address", default=None, help="Restrict the response to customers with the email address.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_ecommerce_stores_id_customers(ctx, store_id, fields, exclude_fields, count, offset, email_address, extra_params):
    """List customers"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/ecommerce/stores/{store_id}/customers"
    params = {k: v for k, v in {
        "fields": fields,
        "exclude_fields": exclude_fields,
        "count": count,
        "offset": offset,
        "email_address": email_address,
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
@ecommerce_group.command("create-ecommerce-stores-id-customers")
@click.argument("STORE_ID")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_create_ecommerce_stores_id_customers(ctx, store_id, data, extra_params):
    """Add customer"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/ecommerce/stores/{store_id}/customers"
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
@ecommerce_group.command("delete-ecommerce-stores-id-customers-id")
@click.argument("STORE_ID")
@click.argument("CUSTOMER_ID")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_delete_ecommerce_stores_id_customers_id(ctx, store_id, customer_id, extra_params):
    """Delete customer"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/ecommerce/stores/{store_id}/customers/{customer_id}"
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
