# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


@unittest.skipUnless(HAS_DAILY_FOLDER, SKIP_REASON)
class SessionE2ETests(unittest.TestCase):
    CLI_BASE = resolve_cli()

    def run_cli(self, args: list[str], input_text: str | None = None, extra_env: dict | None = None) -> subprocess.CompletedProcess:
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
            timeout=30,
        )

    def test_session_use_daily_sets_current_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {
                "CLI_ANYTHING_MUBU_STATE_DIR": tmpdir,
                "MUBU_DAILY_FOLDER": DETECTED_DAILY_FOLDER_REF,
            }
            self.run_cli(["session", "use-daily"], extra_env=env)
            result = self.run_cli(["session", "status", "--json"], extra_env=env)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            data = json.loads(result.stdout)
            self.assertIsNotNone(data.get("current_doc"))
            self.assertIn(DETECTED_DAILY_FOLDER_REF, data["current_doc"])

    def test_repl_use_daily_then_daily_nodes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {
                "CLI_ANYTHING_MUBU_STATE_DIR": tmpdir,
                "MUBU_DAILY_FOLDER": DETECTED_DAILY_FOLDER_REF,
            }
            result = self.run_cli(
                [],
                input_text="use-daily\ndaily-nodes --json\nexit\n",
                extra_env=env,
            )
            assert_cli_success_or_skip(self, result)
            self.assertIn('"nodes"', result.stdout)


@unittest.skipUnless(HAS_DAILY_FOLDER, SKIP_REASON)
class MutateDryRunE2ETests(unittest.TestCase):
    """Test mutation commands in dry-run mode (no --execute)."""

    CLI_BASE = resolve_cli()

    def run_cli(self, args: list[str], extra_env: dict | None = None) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )

    def _resolve_daily_node(self) -> tuple[str, str]:
        """Helper: get a stable daily document reference and first node id."""
        result = self.run_cli(
            ["daily-nodes", "--json"],
            extra_env={"MUBU_DAILY_FOLDER": DETECTED_DAILY_FOLDER_REF},
        )
        assert_cli_success_or_skip(self, result)
        data = json.loads(result.stdout)
        doc = data.get("document", data)
        doc_ref = doc.get("doc_id") or doc["doc_path"]
        node_id = data["nodes"][0]["node_id"]
        return doc_ref, node_id

    def test_update_text_dry_run(self):
        doc_ref, node_id = self._resolve_daily_node()
        result = self.run_cli([
            "update-text", doc_ref,
            "--node-id", node_id,
            "--text", "dry run test",
            "--json",
        ])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        data = json.loads(result.stdout)
        self.assertIn("request", data)
        self.assertFalse(data.get("executed", False))

    def test_create_child_dry_run(self):
        doc_ref, node_id = self._resolve_daily_node()
        result = self.run_cli([
            "create-child", doc_ref,
            "--parent-node-id", node_id,
            "--text", "dry run child",
            "--json",
        ])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        data = json.loads(result.stdout)
        self.assertIn("request", data)
        self.assertFalse(data.get("executed", False))

    def test_delete_node_dry_run(self):
        doc_ref, node_id = self._resolve_daily_node()
        result = self.run_cli([
            "delete-node", doc_ref,
            "--node-id", node_id,
            "--json",
        ])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        data = json.loads(result.stdout)
        self.assertFalse(data.get("executed", False))
