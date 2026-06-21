# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSession:
    def test_creates_new_project_when_missing(self, tmp_dir):
        from cli_anything.cloudcompare.core.session import Session

        path = os.path.join(tmp_dir, "new.json")
        assert not os.path.exists(path)
        s = Session(path)
        # Session creates project in memory; save() to persist
        s.save()
        assert os.path.exists(path)

    def test_loads_existing_project(self, project_path):
        from cli_anything.cloudcompare.core.project import create_project
        from cli_anything.cloudcompare.core.session import Session

        create_project(project_path, name="Loaded")
        s = Session(project_path)
        assert s.name == "Loaded"

    def test_cloud_count_increments(self, project_path, dummy_cloud_file):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        assert s.cloud_count == 0
        s.add_cloud(dummy_cloud_file)
        assert s.cloud_count == 1

    def test_mesh_count_increments(self, project_path, dummy_mesh_file):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        assert s.mesh_count == 0
        s.add_mesh(dummy_mesh_file)
        assert s.mesh_count == 1

    def test_is_modified_after_add(self, project_path, dummy_cloud_file):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        assert not s.is_modified
        s.add_cloud(dummy_cloud_file)
        assert s.is_modified

    def test_is_not_modified_after_save(self, project_path, dummy_cloud_file):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        s.add_cloud(dummy_cloud_file)
        s.save()
        assert not s.is_modified

    def test_remove_cloud(self, project_path, dummy_cloud_file):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        s.add_cloud(dummy_cloud_file)
        removed = s.remove_cloud(0)
        assert s.cloud_count == 0
        assert "path" in removed

    def test_get_cloud(self, project_path, dummy_cloud_file):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        s.add_cloud(dummy_cloud_file, label="scan_a")
        entry = s.get_cloud(0)
        assert entry["label"] == "scan_a"

    def test_history_recording(self, project_path):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        s.record("test_op", ["a.las"], ["b.las"], {"key": "val"})
        hist = s.history()
        assert len(hist) == 1
        assert hist[0]["operation"] == "test_op"

    def test_history_last_n(self, project_path):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        for i in range(5):
            s.record(f"op_{i}", [], [], {})
        assert len(s.history(3)) == 3
        assert len(s.history(10)) == 5

    def test_undo_last_removes_entry(self, project_path):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        s.record("op_1", [], [], {})
        s.record("op_2", [], [], {})
        removed = s.undo_last()
        assert removed["operation"] == "op_2"
        assert len(s.history()) == 1

    def test_undo_last_returns_none_when_empty(self, project_path):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        result = s.undo_last()
        assert result is None

    def test_set_export_format(self, project_path):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        s.set_export_format(cloud_fmt="PLY", cloud_ext="ply")
        settings = s.get_settings()
        assert settings["cloud_export_format"] == "PLY"
        assert settings["cloud_export_ext"] == "ply"

    def test_set_export_format_ignores_none(self, project_path):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        original_mesh_fmt = s.get_settings().get("mesh_export_format")
        s.set_export_format(cloud_fmt="PLY")  # mesh args are None
        settings = s.get_settings()
        assert settings["cloud_export_format"] == "PLY"
        # mesh format unchanged
        assert settings.get("mesh_export_format") == original_mesh_fmt

    def test_status_dict_keys(self, project_path):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        status = s.status()
        assert "project" in status
        assert "clouds" in status
        assert "meshes" in status
        assert "modified" in status

    def test_repr_contains_path(self, project_path):
        from cli_anything.cloudcompare.core.session import Session

        s = Session(project_path)
        assert "Session(" in repr(s)
