# ruff: noqa: F403, F405, E501
from .rms_cli_base import *  # noqa: F403

# fmt: off
from .rms_cli_p1 import _get_token, cli, handle_error, output  # noqa: E402,E501
from .rms_cli_p5 import files  # noqa: E402,E501
# fmt: on


@files.command("list")
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def files_list(limit, offset):
    """List files."""
    from cli_anything.rms.core.files import list_files

    result = list_files(_get_token(), limit=limit, offset=offset)
    output(result, "Files")


@files.command("get")
@click.argument("file_id")
@handle_error
def files_get(file_id):
    """Get file details."""
    from cli_anything.rms.core.files import get_file

    result = get_file(_get_token(), file_id)
    output(result, f"File {file_id}")


@files.command("upload")
@click.argument("file_path", type=click.Path(exists=True))
@handle_error
def files_upload(file_path):
    """Upload a file."""
    from cli_anything.rms.core.files import upload_file

    result = upload_file(_get_token(), file_path)
    output(result, f"Uploaded {file_path}")


@files.command("delete")
@click.argument("file_id")
@handle_error
def files_delete(file_id):
    """Delete file."""
    from cli_anything.rms.core.files import delete_file

    result = delete_file(_get_token(), file_id)
    output(result, f"Deleted file {file_id}")


@cli.group()
def reports():
    """Report management."""


@reports.command("list")
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def reports_list(limit, offset):
    """List reports."""
    from cli_anything.rms.core.reports import list_reports

    result = list_reports(_get_token(), limit=limit, offset=offset)
    output(result, "Reports")


@reports.command("get")
@click.argument("report_id")
@handle_error
def reports_get(report_id):
    """Get report."""
    from cli_anything.rms.core.reports import get_report

    result = get_report(_get_token(), report_id)
    output(result, f"Report {report_id}")


@reports.command("create")
@click.option("--template", "template_id", required=True, help="Report template ID")
@click.option("--name", type=str, default=None)
@handle_error
def reports_create(template_id, name):
    """Create report."""
    from cli_anything.rms.core.reports import create_report

    data = {"template_id": template_id}
    if name:
        data["name"] = name
    result = create_report(_get_token(), data)
    output(result, "Created report")


@reports.command("delete")
@click.argument("report_id")
@handle_error
def reports_delete(report_id):
    """Delete report."""
    from cli_anything.rms.core.reports import delete_report

    result = delete_report(_get_token(), report_id)
    output(result, f"Deleted report {report_id}")


@reports.group("templates")
def report_templates():
    """Report template management."""


@report_templates.command("list")
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def report_templates_list(limit, offset):
    """List report templates."""
    from cli_anything.rms.core.reports import list_templates

    result = list_templates(_get_token(), limit=limit, offset=offset)
    output(result, "Report templates")


@report_templates.command("get")
@click.argument("template_id")
@handle_error
def report_templates_get(template_id):
    """Get report template."""
    from cli_anything.rms.core.reports import get_template

    result = get_template(_get_token(), template_id)
    output(result, f"Template {template_id}")


@report_templates.command("create")
@click.option("--data", "data_json", required=True, help="JSON template data")
@handle_error
def report_templates_create(data_json):
    """Create report template."""
    from cli_anything.rms.core.reports import create_template

    data = json.loads(data_json)
    result = create_template(_get_token(), data)
    output(result, "Created report template")


@report_templates.command("update")
@click.argument("template_id")
@click.option("--data", "data_json", required=True, help="JSON template data")
@handle_error
def report_templates_update(template_id, data_json):
    """Update report template."""
    from cli_anything.rms.core.reports import update_template

    data = json.loads(data_json)
    result = update_template(_get_token(), template_id, data)
    output(result, f"Updated template {template_id}")


@report_templates.command("delete")
@click.argument("template_id")
@handle_error
def report_templates_delete(template_id):
    """Delete report template."""
    from cli_anything.rms.core.reports import delete_template

    result = delete_template(_get_token(), template_id)
    output(result, f"Deleted template {template_id}")


@cli.group()
def hotspots():
    """Device hotspot management."""
