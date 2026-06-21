# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import cloud_xyz, tmp_dir  # noqa: F401,E501


class TestExportPipeline:
    def test_export_cloud_to_las(self, tmp_dir, cloud_xyz):
        """Export a cloud to LAS using the export module."""
        from cli_anything.cloudcompare.core.export import export_cloud

        output_path = os.path.join(tmp_dir, "exported.las")
        result = export_cloud(cloud_xyz, output_path, preset="las", overwrite=True)

        assert result["format"] == "LAS"
        assert result["file_size"] > 0
        assert os.path.exists(result["output"])

        with open(result["output"], "rb") as f:
            assert f.read(4) == b"LASF"

        print(f"\n  Export LAS: {result['output']} ({result['file_size']:,} bytes)")

    def test_export_cloud_to_ply(self, tmp_dir, cloud_xyz):
        """Export a cloud to PLY using the export module."""
        from cli_anything.cloudcompare.core.export import export_cloud

        output_path = os.path.join(tmp_dir, "exported.ply")
        result = export_cloud(cloud_xyz, output_path, preset="ply", overwrite=True)

        assert result["format"] == "PLY"
        assert result["file_size"] > 0

        with open(result["output"], "rb") as f:
            assert f.read(3) == b"ply"

        print(f"\n  Export PLY: {result['output']} ({result['file_size']:,} bytes)")

    def test_export_raises_on_no_overwrite(self, tmp_dir, cloud_xyz):
        """Export raises FileExistsError when output exists and overwrite=False."""
        from cli_anything.cloudcompare.core.export import export_cloud

        output_path = os.path.join(tmp_dir, "exported_noover.las")
        # First export
        export_cloud(cloud_xyz, output_path, preset="las", overwrite=True)
        # Second export without overwrite should raise
        with pytest.raises(FileExistsError):
            export_cloud(cloud_xyz, output_path, preset="las", overwrite=False)

    def test_list_presets(self):
        """list_presets returns cloud and mesh format dicts."""
        from cli_anything.cloudcompare.core.export import list_presets
        presets = list_presets()
        assert "cloud" in presets
        assert "mesh" in presets
        assert "las" in presets["cloud"]
        assert "obj" in presets["mesh"]


class TestProjectWorkflow:
    def test_full_project_lifecycle(self, tmp_dir, cloud_xyz):
        """Create project → add cloud → subsample → save → reload."""
        from cli_anything.cloudcompare.core.session import Session
        from cli_anything.cloudcompare.utils.cc_backend import subsample

        proj_path = os.path.join(tmp_dir, "workflow.json")
        output_cloud = os.path.join(tmp_dir, "subsampled.xyz")

        # 1. Create session and add cloud
        s = Session(proj_path)
        s.add_cloud(cloud_xyz, label="raw_scan")
        s.save()

        # 2. Subsample
        cloud_entry = s.get_cloud(0)
        result = subsample(cloud_entry["path"], output_cloud, "SPATIAL", 0.2)
        assert result["returncode"] == 0
        assert result.get("exists")

        # 3. Add output back to project
        s.add_cloud(output_cloud, label="thinned")
        s.record("subsample", [cloud_entry["path"]], [output_cloud],
                 {"method": "SPATIAL", "param": 0.2})
        s.save()

        # 4. Verify persisted state
        s2 = Session(proj_path)
        assert s2.cloud_count == 2
        assert s2.history(1)[0]["operation"] == "subsample"
        print(f"\n  Project workflow complete: {proj_path}")
        print(f"  Subsampled cloud: {output_cloud} ({result['file_size']:,} bytes)")
