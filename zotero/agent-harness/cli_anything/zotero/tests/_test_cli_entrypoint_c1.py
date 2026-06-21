# ruff: noqa: F403, F405, E501
from ._test_cli_entrypoint_base import *  # noqa: F403


class _CliEntrypointTestsMixin1:
    def test_json_repl_builtin_status_emits_structured_json(self):
        config = RootCliConfig(json_output=True)
        state = {"current_library": 1, "current_collection": "COLLAAAA", "current_item": "REG12345", "command_history": []}
        with mock.patch("cli_anything.zotero.zotero_cli.current_session", return_value=state):
            with mock.patch("click.echo") as echo:
                handled, control = _handle_repl_builtin(["status"], mock.Mock(), config)

        self.assertTrue(handled)
        self.assertEqual(control, 0)
        payload = json.loads(echo.call_args.args[0])
        self.assertEqual(payload["current_library"], 1)
        self.assertEqual(payload["current_item"], "REG12345")
    def test_run_repl_dispatches_commands_with_root_flags(self):
        config = RootCliConfig(
            backend="api",
            data_dir="D:/zotero-data",
            profile_dir="D:/zotero-profile",
            executable="D:/Program Files/Zotero/zotero.exe",
            json_output=True,
        )
        with mock.patch("cli_anything.zotero.zotero_cli.ReplSkin.create_prompt_session", return_value=None):
            with mock.patch("cli_anything.zotero.zotero_cli._safe_print_banner"), mock.patch(
                "cli_anything.zotero.zotero_cli._safe_print_goodbye"
            ):
                with mock.patch("builtins.input", side_effect=["item get REG12345", "exit"]):
                    with mock.patch("cli_anything.zotero.zotero_cli.current_session", return_value=session_mod.default_session_state()):
                        with mock.patch(
                            "cli_anything.zotero.zotero_cli.session_mod.expand_repl_aliases_with_state",
                            return_value=["item", "get", "REG12345"],
                        ):
                            with mock.patch("cli_anything.zotero.zotero_cli.dispatch", return_value=0) as dispatch_mock:
                                result = run_repl(config)

        self.assertEqual(result, 0)
        dispatch_mock.assert_called_once_with(
            [
                "--backend",
                "api",
                "--json",
                "--data-dir",
                "D:/zotero-data",
                "--profile-dir",
                "D:/zotero-profile",
                "--executable",
                "D:/Program Files/Zotero/zotero.exe",
                "item",
                "get",
                "REG12345",
            ]
        )
    def test_app_status_json(self):
        result = self.run_cli(["--json", "app", "status"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"sqlite_exists": true', result.stdout)
    def test_app_enable_local_api_json(self):
        result = self.run_cli(["--json", "app", "enable-local-api"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"enabled": true', result.stdout)
        self.assertIn('"already_enabled": false', result.stdout)
    def test_collection_list_json(self):
        result = self.run_cli(["--json", "collection", "list"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Sample Collection", result.stdout)
    def test_collection_find_json(self):
        result = self.run_cli(["--json", "collection", "find", "sample"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("COLLAAAA", result.stdout)
    def test_item_get_json(self):
        result = self.run_cli(["--json", "item", "get", "REG12345"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Sample Title", result.stdout)
    def test_item_find_and_notes_json(self):
        with fake_zotero_http_server() as server:
            result = self.run_cli(
                ["--json", "item", "find", "Sample", "--collection", "COLLAAAA"],
                extra_env={"ZOTERO_HTTP_PORT": str(server["port"])},
            )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("REG12345", result.stdout)

        notes_result = self.run_cli(["--json", "item", "notes", "REG12345"])
        self.assertEqual(notes_result.returncode, 0, msg=notes_result.stderr)
        self.assertIn("Example note", notes_result.stdout)
    def test_note_get_and_add(self):
        result = self.run_cli(["--json", "note", "get", "NOTEKEY"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Example note", result.stdout)

        with fake_zotero_http_server() as server:
            add_result = self.run_cli(
                ["--json", "note", "add", "REG12345", "--text", "A new note", "--format", "text"],
                extra_env={"ZOTERO_HTTP_PORT": str(server["port"])},
            )
        self.assertEqual(add_result.returncode, 0, msg=add_result.stderr)
        self.assertIn('"action": "note_add"', add_result.stdout)
