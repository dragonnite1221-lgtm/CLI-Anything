# ruff: noqa: F403, F405, E501
from ._test_cli_entrypoint_base import *  # noqa: F403
from ._test_cli_entrypoint_p0 import resolve_cli  # noqa: F401,E501


class _CliEntrypointTestsMixin0:
    CLI_BASE = resolve_cli()
    def run_cli(self, args, input_text=None, extra_env=None):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            self.CLI_BASE + args,
            input=input_text,
            capture_output=True,
            text=True,
            env=env,
        )
    def test_help_renders_root_commands(self):
        result = self.run_cli(["--help"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("discover", result.stdout)
        self.assertIn("inspect", result.stdout)
        self.assertIn("mutate", result.stdout)
        self.assertIn("session", result.stdout)
        self.assertIn("daily-current", result.stdout)
        self.assertIn("create-child", result.stdout)
        self.assertIn("delete-node", result.stdout)
    def test_dispatch_uses_public_prog_name_when_requested(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = dispatch(["--help"], prog_name="mubu-cli")
        self.assertEqual(result, 0)
        self.assertIn("Usage: mubu-cli", stdout.getvalue())
    def test_dispatch_uses_compat_prog_name_when_requested(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = dispatch(["--help"], prog_name="cli-anything-mubu")
        self.assertEqual(result, 0)
        self.assertIn("Usage: cli-anything-mubu", stdout.getvalue())
    def test_repl_help_renders(self):
        result = self.run_cli(["repl", "--help"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Interactive REPL", result.stdout)
        self.assertIn("use-node", result.stdout)
    def test_repl_help_text_supports_public_brand(self):
        self.assertIn("mubu-cli", repl_help_text("mubu-cli"))
    def test_session_state_dir_defaults_to_public_brand_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            with (
                mock.patch.dict(os.environ, {}, clear=False),
                mock.patch("cli_anything.mubu.mubu_cli.Path.home", return_value=home),
            ):
                self.assertEqual(session_state_dir(), home / ".config" / "mubu-cli")
    def test_session_state_dir_falls_back_to_legacy_path_when_only_legacy_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            legacy = home / ".config" / "cli-anything-mubu"
            legacy.mkdir(parents=True)
            with (
                mock.patch.dict(os.environ, {}, clear=False),
                mock.patch("cli_anything.mubu.mubu_cli.Path.home", return_value=home),
            ):
                self.assertEqual(session_state_dir(), legacy)
    def test_default_entrypoint_starts_repl_and_can_exit(self):
        result = self.run_cli([], input_text="exit\n")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Mubu REPL", result.stdout)
    def test_default_entrypoint_banner_includes_skill_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.run_cli(
                [],
                input_text="exit\n",
                extra_env={"CLI_ANYTHING_MUBU_STATE_DIR": tmpdir},
            )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Skill:", result.stdout)
        self.assertIn(
            str(REPO_ROOT / "agent-harness" / "cli_anything" / "mubu" / "skills" / "SKILL.md"),
            result.stdout,
        )
    def test_repl_can_store_current_doc_reference(self):
        result = self.run_cli(
            [],
            input_text=f"use-doc '{SAMPLE_DOC_REF}'\ncurrent-doc\nexit\n",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn(f"Current doc: {SAMPLE_DOC_REF}", result.stdout)
    def test_repl_can_store_current_node_reference(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.run_cli(
                [],
                input_text=f"use-node {SAMPLE_NODE_ID}\ncurrent-node\nexit\n",
                extra_env={"CLI_ANYTHING_MUBU_STATE_DIR": tmpdir},
            )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn(f"Current node: {SAMPLE_NODE_ID}", result.stdout)
    def test_repl_persists_current_doc_between_processes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {"CLI_ANYTHING_MUBU_STATE_DIR": tmpdir}

            first = self.run_cli(
                [],
                input_text=f"use-doc '{SAMPLE_DOC_REF}'\nexit\n",
                extra_env=env,
            )
            self.assertEqual(first.returncode, 0, msg=first.stderr)

            second = self.run_cli(
                [],
                input_text="current-doc\nexit\n",
                extra_env=env,
            )
            self.assertEqual(second.returncode, 0, msg=second.stderr)
            self.assertIn(f"Current doc: {SAMPLE_DOC_REF}", second.stdout)
