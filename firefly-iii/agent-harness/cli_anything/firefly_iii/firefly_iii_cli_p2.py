# ruff: noqa: F403, F405, E501
from .firefly_iii_cli_base import *  # noqa: F403

# fmt: off
from .firefly_iii_cli_p1 import cli  # noqa: E402,E501
# fmt: on


@cli.command()
def repl():
    """Start interactive REPL mode"""
    global _json_output

    if _repl_skin is None:
        click.echo(
            "Error: REPL requires backend connection to be initialized first", err=True
        )
        return

    _repl_skin.print_banner()
    _repl_skin.info("Type 'help' for available commands, 'exit' to quit")

    while True:
        try:
            user_input = _repl_skin.prompt("firefly-iii")

            if not user_input.strip():
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                _repl_skin.print_goodbye()
                break

            if user_input.lower() == "help":
                _repl_skin.help(cli.commands)
                continue

            # Parse command through shell-like rules so quoted arguments survive.
            try:
                parts = shlex.split(user_input)
            except ValueError as e:
                _repl_skin.error(f"Parse error: {e}")
                continue

            command_name = parts[0]
            args = parts[1:]

            if command_name in cli.commands:
                try:
                    cli.commands[command_name].main(
                        args=args,
                        prog_name=command_name,
                        standalone_mode=False,
                    )
                except click.ClickException as e:
                    _repl_skin.error(e.format_message())
                except click.Abort:
                    _repl_skin.error("Command aborted")
                except click.exceptions.Exit as e:
                    if e.exit_code:
                        _repl_skin.error(f"Command exited with status {e.exit_code}")
            else:
                _repl_skin.error(f"Unknown command: {command_name}")

        except KeyboardInterrupt:
            _repl_skin.print_goodbye()
            break
        except Exception as e:
            _repl_skin.error(f"Error: {e}")


cli.add_command(accounts)
cli.add_command(transactions)
cli.add_command(budgets)
cli.add_command(categories)
cli.add_command(tags)
cli.add_command(bills)
cli.add_command(piggy_banks)
cli.add_command(insights)
cli.add_command(search)
cli.add_command(export)
cli.add_command(info)
cli.add_command(autocomplete)
cli.add_command(currencies)
cli.add_command(recurrences)
cli.add_command(rules)
cli.add_command(rule_groups)
cli.add_command(summary)
cli.add_command(webhooks)


def main():
    """Entry point"""
    cli()
