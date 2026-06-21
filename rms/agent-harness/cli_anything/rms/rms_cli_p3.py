# ruff: noqa: F403, F405, E501
from .rms_cli_base import *  # noqa: F403

# fmt: off
from .rms_cli_p1 import _get_token, cli, handle_error, output  # noqa: E402,E501
from .rms_cli_p2 import companies  # noqa: E402,E501
# fmt: on


@companies.command("get")
@click.argument("company_id")
@handle_error
def companies_get(company_id):
    """Get company details."""
    from cli_anything.rms.core.companies import get_company

    result = get_company(_get_token(), company_id)
    output(result, f"Company {company_id}")


@companies.command("create")
@click.option("--name", required=True)
@handle_error
def companies_create(name):
    """Create company."""
    from cli_anything.rms.core.companies import create_company

    result = create_company(_get_token(), {"name": name})
    output(result, f"Created company: {name}")


@companies.command("update")
@click.argument("company_id")
@click.option("--name", type=str, default=None)
@handle_error
def companies_update(company_id, name):
    """Update company."""
    from cli_anything.rms.core.companies import update_company

    data = {}
    if name:
        data["name"] = name
    if not data:
        raise click.UsageError("No fields to update")
    result = update_company(_get_token(), company_id, data)
    output(result, f"Updated company {company_id}")


@companies.command("delete")
@click.argument("company_id")
@handle_error
def companies_delete(company_id):
    """Delete company."""
    from cli_anything.rms.core.companies import delete_company

    result = delete_company(_get_token(), company_id)
    output(result, f"Deleted company {company_id}")


@cli.group()
def users():
    """User management."""


@users.command("list")
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def users_list(limit, offset):
    """List users."""
    from cli_anything.rms.core.users import list_users

    result = list_users(_get_token(), limit=limit, offset=offset)
    output(result, "Users")


@users.command("get")
@click.argument("user_id")
@handle_error
def users_get(user_id):
    """Get user details."""
    from cli_anything.rms.core.users import get_user

    result = get_user(_get_token(), user_id)
    output(result, f"User {user_id}")


@users.command("invite")
@click.option("--email", required=True)
@click.option("--role", type=str, default=None)
@handle_error
def users_invite(email, role):
    """Invite user."""
    from cli_anything.rms.core.users import invite_user

    data = {"email": email}
    if role:
        data["role"] = role
    result = invite_user(_get_token(), data)
    output(result, f"Invited {email}")


@users.command("update")
@click.argument("user_id")
@click.option("--role", type=str, default=None)
@handle_error
def users_update(user_id, role):
    """Update user."""
    from cli_anything.rms.core.users import update_user

    data = {}
    if role:
        data["role"] = role
    if not data:
        raise click.UsageError("No fields to update")
    result = update_user(_get_token(), user_id, data)
    output(result, f"Updated user {user_id}")


@users.command("delete")
@click.argument("user_id")
@handle_error
def users_delete(user_id):
    """Delete user."""
    from cli_anything.rms.core.users import delete_user

    result = delete_user(_get_token(), user_id)
    output(result, f"Deleted user {user_id}")


@cli.group()
def tags():
    """Tag management."""


@tags.command("list")
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def tags_list(limit, offset):
    """List tags."""
    from cli_anything.rms.core.tags import list_tags

    result = list_tags(_get_token(), limit=limit, offset=offset)
    output(result, "Tags")


@tags.command("get")
@click.argument("tag_id")
@handle_error
def tags_get(tag_id):
    """Get tag details."""
    from cli_anything.rms.core.tags import get_tag

    result = get_tag(_get_token(), tag_id)
    output(result, f"Tag {tag_id}")


@tags.command("create")
@click.option("--name", required=True)
@handle_error
def tags_create(name):
    """Create tag."""
    from cli_anything.rms.core.tags import create_tag

    result = create_tag(_get_token(), {"name": name})
    output(result, f"Created tag: {name}")
