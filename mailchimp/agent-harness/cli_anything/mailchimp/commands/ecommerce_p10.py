# ruff: noqa: F403, F405, E501
from .ecommerce_base import *  # noqa: F403
# fmt: off
from .ecommerce_p1 import _parse_json_option, ecommerce_group  # noqa: E402,E501
# fmt: on


@ecommerce_group.command("get-ecommerce-stores-id-products-id-images-id")
@click.argument("STORE_ID")
@click.argument("PRODUCT_ID")
@click.argument("IMAGE_ID")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_get_ecommerce_stores_id_products_id_images_id(ctx, store_id, product_id, image_id, fields, exclude_fields, extra_params):
    """Get product image info"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/ecommerce/stores/{store_id}/products/{product_id}/images/{image_id}"
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
@ecommerce_group.command("update-ecommerce-stores-id-products-id-images-id")
@click.argument("STORE_ID")
@click.argument("PRODUCT_ID")
@click.argument("IMAGE_ID")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_update_ecommerce_stores_id_products_id_images_id(ctx, store_id, product_id, image_id, data, extra_params):
    """Update product image"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/ecommerce/stores/{store_id}/products/{product_id}/images/{image_id}"
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
@ecommerce_group.command("list-ecommerce-stores-id-products-id-variants")
@click.argument("STORE_ID")
@click.argument("PRODUCT_ID")
@click.option("--fields", "fields", default=None, help="A comma-separated list of fields to return. Reference parameters of sub-objects with dot notation.")
@click.option("--exclude-fields", "exclude_fields", default=None, help="A comma-separated list of fields to exclude. Reference parameters of sub-objects with dot notation.")
@click.option("--count", "count", default=None, type=int, help="The number of records to return. Default value is 10. Maximum value is 1000")
@click.option("--offset", "offset", default=None, type=int, help="Used for [pagination](https://mailchimp.com/developer/marketing/docs/methods-parameters/#pagination), this is the number of records from a collection to skip. Default value is 0.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_list_ecommerce_stores_id_products_id_variants(ctx, store_id, product_id, fields, exclude_fields, count, offset, extra_params):
    """List product variants"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/ecommerce/stores/{store_id}/products/{product_id}/variants"
    params = {k: v for k, v in {
        "fields": fields,
        "exclude_fields": exclude_fields,
        "count": count,
        "offset": offset,
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
@ecommerce_group.command("create-ecommerce-stores-id-products-id-variants")
@click.argument("STORE_ID")
@click.argument("PRODUCT_ID")
@click.option("--data", default=None, help="Request body as JSON string.")
@click.option("--extra-params", default=None, help="Extra query params as JSON object, e.g. '{\"key\":\"val\"}'")
@click.pass_context
def _cmd_create_ecommerce_stores_id_products_id_variants(ctx, store_id, product_id, data, extra_params):
    """Add product variant"""
    from cli_anything.mailchimp.core.client import get_client, MailchimpError
    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err
    path = f"/ecommerce/stores/{store_id}/products/{product_id}/variants"
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
