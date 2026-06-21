# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSessionStateDefaults(unittest.TestCase):
    def test_defaults(self):
        s = SessionState()
        self.assertIsNone(s.window_id)
        self.assertIsNone(s.tab_id)
        self.assertIsNone(s.session_id)
        self.assertEqual(s.notes, "")

    def test_summary_empty(self):
        s = SessionState()
        self.assertEqual(s.summary(), "no context set")

    def test_summary_partial_window_only(self):
        s = SessionState(window_id="w1")
        self.assertIn("window=w1", s.summary())

    def test_summary_partial_tab_only(self):
        s = SessionState(tab_id="t1")
        self.assertIn("tab=t1", s.summary())

    def test_summary_full(self):
        s = SessionState(window_id="w1", tab_id="t1", session_id="s1")
        summary = s.summary()
        self.assertIn("window=w1", summary)
        self.assertIn("tab=t1", summary)
        self.assertIn("session=s1", summary)

    def test_to_dict(self):
        s = SessionState(window_id="w1", tab_id="t1", session_id="s1", notes="test")
        d = s.to_dict()
        self.assertEqual(d["window_id"], "w1")
        self.assertEqual(d["tab_id"], "t1")
        self.assertEqual(d["session_id"], "s1")
        self.assertEqual(d["notes"], "test")

    def test_from_dict(self):
        d = {"window_id": "w2", "tab_id": "t2", "session_id": "s2", "notes": "hi"}
        s = SessionState.from_dict(d)
        self.assertEqual(s.window_id, "w2")
        self.assertEqual(s.tab_id, "t2")
        self.assertEqual(s.session_id, "s2")
        self.assertEqual(s.notes, "hi")

    def test_from_dict_missing_keys(self):
        s = SessionState.from_dict({})
        self.assertIsNone(s.window_id)
        self.assertIsNone(s.tab_id)
        self.assertIsNone(s.session_id)
        self.assertEqual(s.notes, "")

    def test_clear(self):
        s = SessionState(window_id="w1", tab_id="t1", session_id="s1")
        s.clear()
        self.assertIsNone(s.window_id)
        self.assertIsNone(s.tab_id)
        self.assertIsNone(s.session_id)


class TestSessionStatePersistence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "session.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_save_and_load_roundtrip(self):
        s = SessionState(window_id="w1", tab_id="t1", session_id="s1")
        save_state(s, self.path)
        loaded = load_state(self.path)
        self.assertEqual(loaded.window_id, "w1")
        self.assertEqual(loaded.tab_id, "t1")
        self.assertEqual(loaded.session_id, "s1")

    def test_save_creates_parent_dir(self):
        nested = os.path.join(self.tmp.name, "deep", "nested", "session.json")
        s = SessionState(window_id="w99")
        save_state(s, nested)
        self.assertTrue(os.path.exists(nested))

    def test_load_missing_file_returns_empty(self):
        missing = os.path.join(self.tmp.name, "nonexistent.json")
        s = load_state(missing)
        self.assertIsNone(s.window_id)

    def test_load_invalid_json_returns_empty(self):
        bad_path = os.path.join(self.tmp.name, "bad.json")
        with open(bad_path, "w") as f:
            f.write("NOT JSON {{{{")
        s = load_state(bad_path)
        self.assertIsNone(s.window_id)

    def test_clear_state(self):
        s = SessionState(window_id="w1")
        save_state(s, self.path)
        clear_state(self.path)
        loaded = load_state(self.path)
        self.assertIsNone(loaded.window_id)

    def test_overwrite_existing_state(self):
        s1 = SessionState(window_id="w1")
        save_state(s1, self.path)
        s2 = SessionState(window_id="w2", session_id="s2")
        save_state(s2, self.path)
        loaded = load_state(self.path)
        self.assertEqual(loaded.window_id, "w2")
        self.assertEqual(loaded.session_id, "s2")

    def test_saved_file_is_valid_json(self):
        s = SessionState(window_id="w1", tab_id="t1")
        save_state(s, self.path)
        with open(self.path) as f:
            data = json.load(f)
        self.assertEqual(data["window_id"], "w1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
