# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _conn, _json_flag  # noqa: E402,E501
from .n8n_cli_p9 import template_  # noqa: E402,E501
# fmt: on


@template_.command("deploy")
@click.argument("template_id", type=int)
@click.option("--name", default=None, help="Override workflow name")
@click.pass_context
def template_deploy(ctx: click.Context, template_id: int, name: str | None) -> None:
    """Deploy a template from n8n.io directly to your n8n instance."""
    conn = _conn(ctx)
    click.echo(f"  Fetching template #{template_id} from n8n.io...")
    data = templates.get_template(template_id)
    # n8n.io API nests workflow data under "workflow" key
    wf_wrapper = data.get("workflow", {})
    wf_data = (
        wf_wrapper.get("workflow", wf_wrapper) if isinstance(wf_wrapper, dict) else {}
    )

    # Clean for import — never auto-activate
    for field in ("id", "createdAt", "updatedAt", "versionId", "shared"):
        wf_data.pop(field, None)
    wf_data["active"] = False
    if name:
        wf_data["name"] = name
    elif not wf_data.get("name"):
        wf_data["name"] = f"Template #{template_id}"

    result = workflows.create_workflow(wf_data, **conn)
    success(f"Deployed as workflow {result.get('id', '?')} — {result.get('name', '?')}")
    output(result, _json_flag(ctx))
