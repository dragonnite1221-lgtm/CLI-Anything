# ruff: noqa: F403, F405, E501
from .dify_workflow_cli_base import *  # noqa: F403

# fmt: off
from .dify_workflow_cli_p1 import _forward, cli, edit  # noqa: E402,E501
# fmt: on


@edit.command("remove-edge", context_settings=PASS_ARGS)
def edit_remove_edge() -> None:
    _forward("edit", "remove-edge")


@edit.command("set-title", context_settings=PASS_ARGS)
def edit_set_title() -> None:
    _forward("edit", "set-title")


@cli.group(context_settings=PASS_ARGS)
def config() -> None:
    """Chat/agent/completion config commands."""


@config.command("set-model", context_settings=PASS_ARGS)
def config_set_model() -> None:
    _forward("config", "set-model")


@config.command("set-prompt", context_settings=PASS_ARGS)
def config_set_prompt() -> None:
    _forward("config", "set-prompt")


@config.command("add-variable", context_settings=PASS_ARGS)
def config_add_variable() -> None:
    _forward("config", "add-variable")


@config.command("set-opening", context_settings=PASS_ARGS)
def config_set_opening() -> None:
    _forward("config", "set-opening")


@config.command("add-question", context_settings=PASS_ARGS)
def config_add_question() -> None:
    _forward("config", "add-question")


@config.command("add-tool", context_settings=PASS_ARGS)
def config_add_tool() -> None:
    _forward("config", "add-tool")


@config.command("remove-tool", context_settings=PASS_ARGS)
def config_remove_tool() -> None:
    _forward("config", "remove-tool")


def main() -> None:
    cli()
