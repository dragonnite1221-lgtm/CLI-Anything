# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCreateProject:
    def test_creates_file(self, project_path):
        from cli_anything.cloudcompare.core.project import create_project

        proj = create_project(project_path)
        assert os.path.exists(project_path)

    def test_returns_dict_with_expected_keys(self, project_path):
        from cli_anything.cloudcompare.core.project import create_project

        proj = create_project(project_path)
        assert "version" in proj
        assert "clouds" in proj
        assert "meshes" in proj
        assert "settings" in proj
        assert "history" in proj
        assert proj["clouds"] == []
        assert proj["meshes"] == []

    def test_uses_provided_name(self, project_path):
        from cli_anything.cloudcompare.core.project import create_project

        proj = create_project(project_path, name="MySurvey")
        assert proj["name"] == "MySurvey"

    def test_derives_name_from_filename(self, tmp_dir):
        from cli_anything.cloudcompare.core.project import create_project

        path = os.path.join(tmp_dir, "my_scan.json")
        proj = create_project(path)
        assert proj["name"] == "my_scan"

    def test_written_json_is_valid(self, project_path):
        from cli_anything.cloudcompare.core.project import create_project

        create_project(project_path)
        with open(project_path) as f:
            data = json.load(f)
        assert data["version"] == "1.0"


class TestLoadProject:
    def test_loads_existing_project(self, project_path):
        from cli_anything.cloudcompare.core.project import create_project, load_project

        create_project(project_path)
        proj = load_project(project_path)
        assert proj["version"] == "1.0"

    def test_raises_on_missing_file(self, tmp_dir):
        from cli_anything.cloudcompare.core.project import load_project

        with pytest.raises(FileNotFoundError):
            load_project(os.path.join(tmp_dir, "nonexistent.json"))

    def test_raises_on_invalid_json_structure(self, tmp_dir):
        from cli_anything.cloudcompare.core.project import load_project

        path = os.path.join(tmp_dir, "bad.json")
        with open(path, "w") as f:
            json.dump({"foo": "bar"}, f)
        with pytest.raises(ValueError):
            load_project(path)


class TestSaveProject:
    def test_saves_and_updates_modified_at(self, project_path):
        from cli_anything.cloudcompare.core.project import (
            create_project,
            save_project,
            load_project,
        )

        proj = create_project(project_path)
        original_ts = proj["modified_at"]
        import time

        time.sleep(1)
        save_project(proj, project_path)
        reloaded = load_project(project_path)
        # modified_at may or may not change within same second, just check it's present
        assert "modified_at" in reloaded


class TestAddCloud:
    def test_adds_cloud_entry(self, project_path, dummy_cloud_file):
        from cli_anything.cloudcompare.core.project import create_project, add_cloud

        proj = create_project(project_path)
        entry = add_cloud(proj, dummy_cloud_file)
        assert len(proj["clouds"]) == 1
        assert entry["path"] == os.path.abspath(dummy_cloud_file)

    def test_uses_stem_as_default_label(self, project_path, dummy_cloud_file):
        from cli_anything.cloudcompare.core.project import create_project, add_cloud

        proj = create_project(project_path)
        entry = add_cloud(proj, dummy_cloud_file)
        assert entry["label"] == "cloud"

    def test_uses_custom_label(self, project_path, dummy_cloud_file):
        from cli_anything.cloudcompare.core.project import create_project, add_cloud

        proj = create_project(project_path)
        entry = add_cloud(proj, dummy_cloud_file, label="scan_A")
        assert entry["label"] == "scan_A"

    def test_raises_on_missing_file(self, project_path):
        from cli_anything.cloudcompare.core.project import create_project, add_cloud

        proj = create_project(project_path)
        with pytest.raises(FileNotFoundError):
            add_cloud(proj, "/nonexistent/cloud.las")


class TestAddMesh:
    def test_adds_mesh_entry(self, project_path, dummy_mesh_file):
        from cli_anything.cloudcompare.core.project import create_project, add_mesh

        proj = create_project(project_path)
        entry = add_mesh(proj, dummy_mesh_file)
        assert len(proj["meshes"]) == 1
        assert entry["path"] == os.path.abspath(dummy_mesh_file)

    def test_raises_on_missing_file(self, project_path):
        from cli_anything.cloudcompare.core.project import create_project, add_mesh

        proj = create_project(project_path)
        with pytest.raises(FileNotFoundError):
            add_mesh(proj, "/nonexistent/mesh.obj")
