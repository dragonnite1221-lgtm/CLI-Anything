# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


@unittest.skipUnless(HAS_DAILY_FOLDER, SKIP_REASON)
class DiscoverE2ETests(unittest.TestCase):
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

    def test_docs_returns_json_list(self):
        result = self.run_cli(["docs", "--limit", "3", "--json"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        data = json.loads(result.stdout)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("doc_id", data[0])

    def test_folders_returns_json_list(self):
        result = self.run_cli(["folders", "--json"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        data = json.loads(result.stdout)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("folder_id", data[0])

    def test_recent_returns_json_list(self):
        result = self.run_cli(["recent", "--limit", "3", "--json"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        data = json.loads(result.stdout)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_daily_current_returns_doc_path(self):
        result = self.run_cli(
            ["daily-current", "--json"],
            extra_env={"MUBU_DAILY_FOLDER": DETECTED_DAILY_FOLDER_REF},
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        data = json.loads(result.stdout)
        # Response wraps document info in a nested structure
        doc = data.get("document", data)
        self.assertIn("doc_path", doc)
        self.assertIn(DETECTED_DAILY_FOLDER_REF, doc["doc_path"])


@unittest.skipUnless(HAS_DAILY_FOLDER, SKIP_REASON)
class InspectE2ETests(unittest.TestCase):
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

    def test_search_finds_results(self):
        result = self.run_cli(["search", "日", "--limit", "3", "--json"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        data = json.loads(result.stdout)
        self.assertIsInstance(data, list)

    def test_daily_nodes_returns_node_list(self):
        result = self.run_cli(
            ["daily-nodes", "--json"],
            extra_env={"MUBU_DAILY_FOLDER": DETECTED_DAILY_FOLDER_REF},
        )
        assert_cli_success_or_skip(self, result)
        data = json.loads(result.stdout)
        self.assertIn("nodes", data)
        self.assertIsInstance(data["nodes"], list)
