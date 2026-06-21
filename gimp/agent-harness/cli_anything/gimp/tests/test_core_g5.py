# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestLockedSaveJson:
    """Tests for _locked_save_json atomic file writes."""

    def test_basic_save(self, tmp_path):
        from cli_anything.gimp.core.session import _locked_save_json

        path = str(tmp_path / "test.json")
        _locked_save_json(path, {"key": "value"}, indent=2)
        with open(path) as f:
            data = json.load(f)
        assert data == {"key": "value"}

    def test_overwrite_existing(self, tmp_path):
        from cli_anything.gimp.core.session import _locked_save_json

        path = str(tmp_path / "test.json")
        _locked_save_json(path, {"version": 1}, indent=2)
        _locked_save_json(path, {"version": 2}, indent=2)
        with open(path) as f:
            data = json.load(f)
        assert data == {"version": 2}

    def test_overwrite_shorter_data(self, tmp_path):
        """Ensure truncation works — shorter data doesn't leave old bytes."""
        from cli_anything.gimp.core.session import _locked_save_json

        path = str(tmp_path / "test.json")
        _locked_save_json(path, {"key": "a" * 1000}, indent=2)
        _locked_save_json(path, {"k": 1}, indent=2)
        with open(path) as f:
            data = json.load(f)
        assert data == {"k": 1}

    def test_creates_parent_dirs(self, tmp_path):
        from cli_anything.gimp.core.session import _locked_save_json

        path = str(tmp_path / "nested" / "dir" / "test.json")
        _locked_save_json(path, {"nested": True})
        with open(path) as f:
            data = json.load(f)
        assert data == {"nested": True}

    def test_concurrent_writes_produce_valid_json(self, tmp_path):
        """Multiple threads writing to the same file should not corrupt it."""
        from cli_anything.gimp.core.session import _locked_save_json
        import threading

        path = str(tmp_path / "concurrent.json")
        errors = []

        def writer(thread_id):
            try:
                for i in range(50):
                    _locked_save_json(
                        path,
                        {"thread": thread_id, "iteration": i},
                        indent=2,
                        sort_keys=True,
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(t,)) for t in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Errors during concurrent writes: {errors}"
        # Final file must be valid JSON
        with open(path) as f:
            data = json.load(f)
        assert "thread" in data
        assert "iteration" in data
