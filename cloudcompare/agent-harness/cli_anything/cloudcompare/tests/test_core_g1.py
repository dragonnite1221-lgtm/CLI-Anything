# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestRemoveCloud:
    def test_removes_cloud_by_index(self, project_path, dummy_cloud_file):
        from cli_anything.cloudcompare.core.project import (
            create_project,
            add_cloud,
            remove_cloud,
        )

        proj = create_project(project_path)
        add_cloud(proj, dummy_cloud_file)
        removed = remove_cloud(proj, 0)
        assert len(proj["clouds"]) == 0
        assert removed["path"] == os.path.abspath(dummy_cloud_file)

    def test_raises_on_out_of_range_index(self, project_path):
        from cli_anything.cloudcompare.core.project import create_project, remove_cloud

        proj = create_project(project_path)
        with pytest.raises(IndexError):
            remove_cloud(proj, 0)

    def test_raises_on_negative_index(self, project_path, dummy_cloud_file):
        from cli_anything.cloudcompare.core.project import (
            create_project,
            add_cloud,
            remove_cloud,
        )

        proj = create_project(project_path)
        add_cloud(proj, dummy_cloud_file)
        with pytest.raises(IndexError):
            remove_cloud(proj, -1)


class TestGetCloud:
    def test_returns_cloud_by_index(self, project_path, dummy_cloud_file):
        from cli_anything.cloudcompare.core.project import (
            create_project,
            add_cloud,
            get_cloud,
        )

        proj = create_project(project_path)
        add_cloud(proj, dummy_cloud_file, label="my_scan")
        entry = get_cloud(proj, 0)
        assert entry["label"] == "my_scan"

    def test_raises_on_invalid_index(self, project_path):
        from cli_anything.cloudcompare.core.project import create_project, get_cloud

        proj = create_project(project_path)
        with pytest.raises(IndexError):
            get_cloud(proj, 99)


class TestProjectInfo:
    def test_returns_summary(self, project_path, dummy_cloud_file, dummy_mesh_file):
        from cli_anything.cloudcompare.core.project import (
            create_project,
            add_cloud,
            add_mesh,
            project_info,
        )

        proj = create_project(project_path, name="TestProj")
        add_cloud(proj, dummy_cloud_file)
        add_mesh(proj, dummy_mesh_file)
        info = project_info(proj)
        assert info["name"] == "TestProj"
        assert info["cloud_count"] == 1
        assert info["mesh_count"] == 1
        assert len(info["clouds"]) == 1
        assert info["clouds"][0]["index"] == 0


class TestRecordOperation:
    def test_appends_to_history(self, project_path):
        from cli_anything.cloudcompare.core.project import (
            create_project,
            record_operation,
        )

        proj = create_project(project_path)
        record_operation(
            proj, "subsample", ["in.las"], ["out.las"], {"method": "SPATIAL"}
        )
        assert len(proj["history"]) == 1
        assert proj["history"][0]["operation"] == "subsample"
        assert proj["history"][0]["params"]["method"] == "SPATIAL"
