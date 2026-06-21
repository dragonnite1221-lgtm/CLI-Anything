# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class SessionTests(unittest.TestCase):
    def test_save_and_load_session_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict("os.environ", {"CLI_ANYTHING_ZOTERO_STATE_DIR": tmpdir}, clear=False):
                state = session_mod.default_session_state()
                state["current_item"] = "REG12345"
                session_mod.save_session_state(state)
                loaded = session_mod.load_session_state()
                self.assertEqual(loaded["current_item"], "REG12345")

    def test_expand_repl_aliases(self):
        state = {"current_library": "1", "current_collection": "2", "current_item": "REG12345"}
        expanded = session_mod.expand_repl_aliases_with_state(["item", "get", "@item", "@collection"], state)
        self.assertEqual(expanded, ["item", "get", "REG12345", "2"])

    def test_normalize_library_ref_accepts_plain_and_tree_view_ids(self):
        self.assertEqual(zotero_sqlite.normalize_library_ref("1"), 1)
        self.assertEqual(zotero_sqlite.normalize_library_ref("L1"), 1)
        self.assertEqual(zotero_sqlite.normalize_library_ref(2), 2)


class HttpUtilityTests(unittest.TestCase):
    def test_build_runtime_context_reports_unavailable_services(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = create_sample_environment(Path(tmpdir))
            prefs_path = env["profile_dir"] / "prefs.js"
            prefs_text = prefs_path.read_text(encoding="utf-8").replace("23119", "23191")
            prefs_path.write_text(prefs_text, encoding="utf-8")
            runtime = discovery.build_runtime_context(
                data_dir=str(env["data_dir"]),
                profile_dir=str(env["profile_dir"]),
                executable=str(env["executable"]),
            )
            self.assertFalse(runtime.connector_available)
            self.assertFalse(runtime.local_api_available)

    def test_catalog_style_list_parses_csl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = create_sample_environment(Path(tmpdir))
            runtime = discovery.build_runtime_context(
                data_dir=str(env["data_dir"]),
                profile_dir=str(env["profile_dir"]),
                executable=str(env["executable"]),
            )
            styles = catalog.list_styles(runtime)
            self.assertEqual(styles[0]["title"], "Sample Style")

    def test_wait_for_endpoint_requires_explicit_ready_status(self):
        with fake_zotero_http_server(local_api_root_status=403) as server:
            ready = zotero_http.wait_for_endpoint(
                server["port"],
                "/api/",
                timeout=1,
                poll_interval=0.05,
                headers={"Zotero-API-Version": zotero_http.LOCAL_API_VERSION},
            )
        self.assertFalse(ready)

        with fake_zotero_http_server(local_api_root_status=200) as server:
            ready = zotero_http.wait_for_endpoint(
                server["port"],
                "/api/",
                timeout=1,
                poll_interval=0.05,
                headers={"Zotero-API-Version": zotero_http.LOCAL_API_VERSION},
            )
        self.assertTrue(ready)

    def test_launch_zotero_raises_when_executable_is_unresolved(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = create_sample_environment(Path(tmpdir))
            runtime = discovery.build_runtime_context(
                data_dir=str(env["data_dir"]),
                profile_dir=str(env["profile_dir"]),
                executable=str(env["executable"]),
            )
            runtime.environment.executable = None
            with self.assertRaisesRegex(RuntimeError, "could not be resolved"):
                discovery.launch_zotero(runtime)
