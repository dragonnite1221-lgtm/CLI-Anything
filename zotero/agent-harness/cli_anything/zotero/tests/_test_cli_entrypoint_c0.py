# ruff: noqa: F403, F405, E501
from ._test_cli_entrypoint_base import *  # noqa: F403
from ._test_cli_entrypoint_p0 import resolve_cli, uses_module_fallback  # noqa: F401,E501


class _CliEntrypointTestsMixin0:
    CLI_BASE = resolve_cli()
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.env_paths = create_sample_environment(Path(self.tmpdir.name))
    def run_cli(self, args, input_text=None, extra_env=None):
        env = os.environ.copy()
        if uses_module_fallback(self.CLI_BASE):
            env["PYTHONPATH"] = str(REPO_ROOT / "zotero" / "agent-harness") + os.pathsep + env.get("PYTHONPATH", "")
        env["ZOTERO_PROFILE_DIR"] = str(self.env_paths["profile_dir"])
        env["ZOTERO_DATA_DIR"] = str(self.env_paths["data_dir"])
        env["ZOTERO_EXECUTABLE"] = str(self.env_paths["executable"])
        env["ZOTERO_HTTP_PORT"] = "23191"
        env["CLI_ANYTHING_ZOTERO_STATE_DIR"] = str(Path(self.tmpdir.name) / "state")
        if extra_env:
            env.update(extra_env)
        return subprocess.run(self.CLI_BASE + args, input=input_text, capture_output=True, text=True, env=env)
    def test_help_renders_groups(self):
        result = self.run_cli(["--help"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("collection", result.stdout)
        self.assertIn("item", result.stdout)
        self.assertIn("import", result.stdout)
        self.assertIn("note", result.stdout)
        self.assertIn("session", result.stdout)
    def test_dispatch_uses_requested_prog_name(self):
        result = dispatch(["--help"], prog_name="cli-anything-zotero")
        self.assertEqual(result, 0)
    def test_force_installed_mode_requires_real_command(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict("os.environ", {"CLI_ANYTHING_FORCE_INSTALLED": "1"}, clear=False):
                with mock.patch("shutil.which", return_value=None):
                    with mock.patch("sysconfig.get_path", return_value=tmpdir):
                        with self.assertRaises(RuntimeError):
                            resolve_cli()
    def test_repl_help_text_mentions_builtins(self):
        self.assertIn("use-selected", repl_help_text())
        self.assertIn("current-item", repl_help_text())
    def test_default_entrypoint_starts_repl(self):
        result = self.run_cli([], input_text="exit\n")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("cli-anything-zotero", result.stdout)
    def test_repl_builtin_use_library_uses_root_runtime_config(self):
        config = RootCliConfig(
            backend="api",
            data_dir="D:/zotero-data",
            profile_dir="D:/zotero-profile",
            executable="D:/Program Files/Zotero/zotero.exe",
            json_output=True,
        )
        skin = mock.Mock()
        state = {"current_library": None, "current_collection": None, "current_item": None, "command_history": []}

        with mock.patch("cli_anything.zotero.zotero_cli.current_session", return_value=state):
            with mock.patch("cli_anything.zotero.zotero_cli.session_mod.save_session_state"):
                with mock.patch("cli_anything.zotero.zotero_cli.session_mod.append_command_history"):
                    with mock.patch("cli_anything.zotero.zotero_cli.discovery.build_runtime_context", return_value=object()) as build_runtime:
                        with mock.patch("cli_anything.zotero.zotero_cli._normalize_session_library", return_value=2):
                            with mock.patch("click.echo") as echo:
                                handled, control = _handle_repl_builtin(["use-library", "L2"], skin, config)

        self.assertTrue(handled)
        self.assertEqual(control, 0)
        build_runtime.assert_called_once_with(
            backend="api",
            data_dir="D:/zotero-data",
            profile_dir="D:/zotero-profile",
            executable="D:/Program Files/Zotero/zotero.exe",
        )
        emitted = json.loads(echo.call_args.args[0])
        self.assertEqual(emitted["current_library"], 2)
    def test_repl_builtin_use_selected_uses_root_runtime_config(self):
        config = RootCliConfig(
            backend="sqlite",
            data_dir="D:/zotero-data",
            profile_dir="D:/zotero-profile",
            executable="D:/Program Files/Zotero/zotero.exe",
            json_output=False,
        )
        runtime = object()
        selected = {"collectionID": 1, "collectionName": "Selected"}
        state = {"current_library": 1, "current_collection": "COLLAAAA", "current_item": None, "command_history": []}

        with mock.patch("cli_anything.zotero.zotero_cli.current_session", return_value=state):
            with mock.patch("cli_anything.zotero.zotero_cli.discovery.build_runtime_context", return_value=runtime) as build_runtime:
                with mock.patch("cli_anything.zotero.zotero_cli.catalog.use_selected_collection", return_value=selected) as use_selected:
                    with mock.patch("cli_anything.zotero.zotero_cli._persist_selected_collection", return_value=state):
                        with mock.patch("cli_anything.zotero.zotero_cli.session_mod.append_command_history"):
                            with mock.patch("click.echo"):
                                handled, control = _handle_repl_builtin(["use-selected"], mock.Mock(), config)

        self.assertTrue(handled)
        self.assertEqual(control, 0)
        build_runtime.assert_called_once_with(
            backend="sqlite",
            data_dir="D:/zotero-data",
            profile_dir="D:/zotero-profile",
            executable="D:/Program Files/Zotero/zotero.exe",
        )
        use_selected.assert_called_once_with(runtime)
