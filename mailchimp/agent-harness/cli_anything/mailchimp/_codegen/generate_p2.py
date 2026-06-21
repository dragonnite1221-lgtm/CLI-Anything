# ruff: noqa: F403, F405, E501
from .generate_base import *  # noqa: F403

# fmt: off
from .generate_p1 import _click_help_text, _param_type_to_click, _safe_name, _slugify, _tag_to_module  # noqa: E402,E501
# fmt: on


def _generate_command_func(
    cmd_name: str,
    method: str,
    path: str,
    operation: dict,
    path_params: list,
    query_params: list,
    body_param: dict | None,
) -> str:
    summary = operation.get("summary", "").replace('"', '\\"')
    # C1: prefix with _cmd_ so no builtin shadowing (list, get, delete, etc.)
    func_name = "_cmd_" + _safe_name(cmd_name.replace("-", "_"))

    lines: list[str] = []

    group_var = f"{_tag_to_module(operation['tags'][0])}_group"
    decorators = [f'@{group_var}.command("{cmd_name}")']

    # Path params as Click arguments (positional)
    for p in path_params:
        py_arg = _safe_name(p["name"]).upper()
        decorators.append(f'@click.argument("{py_arg}")')

    # Body option
    if body_param is not None:
        decorators.append(
            '@click.option("--data", default=None, help="Request body as JSON string.")'
        )

    # I3: All query params (no arbitrary cap); --extra-params escape hatch
    for p in query_params:
        flag = _slugify(p["name"])
        py_name = _safe_name(p["name"]).lower()
        ptype = _param_type_to_click(p)
        desc = _click_help_text(p.get("description", ""))
        if ptype == "int":
            type_clause = "type=int, "
        elif ptype == "bool":
            type_clause = "type=bool, "
        else:
            type_clause = ""
        decorators.append(
            f'@click.option("--{flag}", "{py_name}", default=None, {type_clause}help="{desc}")'
        )

    # Escape hatch for extra/future query params
    decorators.append(
        '@click.option("--extra-params", default=None, '
        'help="Extra query params as JSON object, e.g. \'{\\"key\\":\\"val\\"}\'")'
    )

    decorators.append("@click.pass_context")

    for d in decorators:
        lines.append(d)

    # Function signature — M4: no module-level USE_JSON import needed
    sig_parts = ["ctx"]
    for p in path_params:
        sig_parts.append(_safe_name(p["name"]).lower())
    if body_param is not None:
        sig_parts.append("data")
    for p in query_params:
        sig_parts.append(_safe_name(p["name"]).lower())
    sig_parts.append("extra_params")

    lines.append(f"def {func_name}({', '.join(sig_parts)}):")
    lines.append(f'    """{summary}"""')

    lines.append(
        "    from cli_anything.mailchimp.core.client import get_client, MailchimpError"
    )
    lines.append(
        "    from cli_anything.mailchimp.utils.output import _out, _out_ok, _out_err"
    )

    # Build path with lowercased path params
    url_parts = re.sub(
        r"\{([^}]+)\}",
        lambda m: "{" + _safe_name(m.group(1)).lower() + "}",
        path,
    )
    lines.append(f'    path = f"{url_parts}"')

    # Build query params dict
    if query_params:
        lines.append("    params = {k: v for k, v in {")
        for p in query_params:
            py_name = _safe_name(p["name"]).lower()
            lines.append(f'        "{p["name"]}": {py_name},')
        lines.append("    }.items() if v is not None}")
    else:
        lines.append("    params = {}")

    # Merge --extra-params
    lines.append("    if extra_params:")
    lines.append(
        '        params.update(_parse_json_option(extra_params, "--extra-params", require_object=True))'
    )

    # Parse body
    if body_param is not None:
        lines.append('    body = _parse_json_option(data, "--data") if data else None')

    # Make the request
    lines.append("    client = get_client()")
    lines.append("    try:")
    if method == "get":
        lines.append("        result = client.get(path, params=params or None)")
    elif method == "post":
        body_arg = "body" if body_param else "None"
        lines.append(
            f"        result = client.post(path, json={body_arg}, params=params or None)"
        )
    elif method == "patch":
        body_arg = "body" if body_param else "None"
        lines.append(
            f"        result = client.patch(path, json={body_arg}, params=params or None)"
        )
    elif method == "put":
        body_arg = "body" if body_param else "None"
        lines.append(
            f"        result = client.put(path, json={body_arg}, params=params or None)"
        )
    elif method == "delete":
        lines.append("        result = client.delete(path, params=params or None)")
    else:
        lines.append("        result = client.get(path, params=params or None)")

    lines.append("    except MailchimpError as e:")
    lines.append("        _out_err(e.status, e.title, e.detail, e.raw)")
    lines.append("        return")

    if method == "delete":
        lines.append('    _out_ok("Deleted.")')
    else:
        lines.append("    _out(result)")

    lines.append("")
    return "\n".join(lines)
