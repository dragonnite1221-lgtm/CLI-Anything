# ruff: noqa: F403, F405, E501
from ._test_cli_entrypoint_base import *  # noqa: F403


class _CliEntrypointTestsMixin1:
    def test_repl_persists_current_node_between_processes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {"CLI_ANYTHING_MUBU_STATE_DIR": tmpdir}

            first = self.run_cli(
                [],
                input_text=f"use-node {SAMPLE_NODE_ID}\nexit\n",
                extra_env=env,
            )
            self.assertEqual(first.returncode, 0, msg=first.stderr)

            second = self.run_cli(
                [],
                input_text="current-node\nexit\n",
                extra_env=env,
            )
            self.assertEqual(second.returncode, 0, msg=second.stderr)
            self.assertIn(f"Current node: {SAMPLE_NODE_ID}", second.stdout)
    def test_repl_aliases_expand_current_doc_and_node(self):
        expanded = expand_repl_aliases_with_state(
            ["delete-node", "@doc", "--node-id", "@node", "--from", "@current"],
            {"current_doc": SAMPLE_DOC_REF, "current_node": SAMPLE_NODE_ID},
        )
        self.assertEqual(
            expanded,
            ["delete-node", SAMPLE_DOC_REF, "--node-id", SAMPLE_NODE_ID, "--from", SAMPLE_DOC_REF],
        )
    def test_repl_clear_doc_persists_between_processes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {"CLI_ANYTHING_MUBU_STATE_DIR": tmpdir}

            self.run_cli(
                [],
                input_text=f"use-doc '{SAMPLE_DOC_REF}'\nexit\n",
                extra_env=env,
            )

            cleared = self.run_cli(
                [],
                input_text="clear-doc\nexit\n",
                extra_env=env,
            )
            self.assertEqual(cleared.returncode, 0, msg=cleared.stderr)

            final = self.run_cli(
                [],
                input_text="current-doc\nexit\n",
                extra_env=env,
            )
            self.assertEqual(final.returncode, 0, msg=final.stderr)
            self.assertIn("Current doc: <unset>", final.stdout)
    def test_repl_clear_node_persists_between_processes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {"CLI_ANYTHING_MUBU_STATE_DIR": tmpdir}

            self.run_cli(
                [],
                input_text=f"use-node {SAMPLE_NODE_ID}\nexit\n",
                extra_env=env,
            )

            cleared = self.run_cli(
                [],
                input_text="clear-node\nexit\n",
                extra_env=env,
            )
            self.assertEqual(cleared.returncode, 0, msg=cleared.stderr)

            final = self.run_cli(
                [],
                input_text="current-node\nexit\n",
                extra_env=env,
            )
            self.assertEqual(final.returncode, 0, msg=final.stderr)
            self.assertIn("Current node: <unset>", final.stdout)
    @unittest.skipUnless(HAS_DAILY_FOLDER, "Mubu local data or daily folder not found")
    def test_grouped_discover_daily_current_supports_global_json_flag(self):
        missing = self.run_cli(["--json", "discover", "daily-current"])
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("MUBU_DAILY_FOLDER", missing.stderr)

        result = self.run_cli(
            ["--json", "discover", "daily-current"],
            extra_env={"MUBU_DAILY_FOLDER": DETECTED_DAILY_FOLDER_REF},
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"doc_path"', result.stdout)
    def test_session_status_reports_json_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {"CLI_ANYTHING_MUBU_STATE_DIR": tmpdir}
            self.run_cli(
                ["session", "use-doc", SAMPLE_DOC_REF],
                extra_env=env,
            )
            self.run_cli(
                ["session", "use-node", SAMPLE_NODE_ID],
                extra_env=env,
            )
            result = self.run_cli(
                ["session", "status", "--json"],
                extra_env=env,
            )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn(f'"current_doc": "{SAMPLE_DOC_REF}"', result.stdout)
        self.assertIn(f'"current_node": "{SAMPLE_NODE_ID}"', result.stdout)
