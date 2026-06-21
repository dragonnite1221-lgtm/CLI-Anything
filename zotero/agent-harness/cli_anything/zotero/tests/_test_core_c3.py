# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _ImportCoreTestsMixin3:
    def test_import_json_rejects_invalid_json(self):
        json_path = Path(self.tmpdir.name) / "bad.json"
        json_path.write_text("{not-valid", encoding="utf-8")
        with mock.patch.object(self.runtime, "connector_available", True):
            with self.assertRaises(RuntimeError):
                imports_mod.import_json(self.runtime, json_path)
    def test_import_requires_connector(self):
        json_path = Path(self.tmpdir.name) / "items.json"
        json_path.write_text("[]", encoding="utf-8")
        with mock.patch.object(self.runtime, "connector_available", False):
            with self.assertRaises(RuntimeError):
                imports_mod.import_json(self.runtime, json_path)
