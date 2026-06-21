# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCCBackendConstants:
    def test_cloud_formats_has_las(self):
        from cli_anything.cloudcompare.utils.cc_backend import CLOUD_FORMATS

        assert "las" in CLOUD_FORMATS
        assert "laz" in CLOUD_FORMATS
        assert "ply" in CLOUD_FORMATS
        assert "xyz" in CLOUD_FORMATS

    def test_mesh_formats_has_obj(self):
        from cli_anything.cloudcompare.utils.cc_backend import MESH_FORMATS

        assert "obj" in MESH_FORMATS
        assert "stl" in MESH_FORMATS

    def test_find_cloudcompare_raises_when_not_found(self, monkeypatch):
        """When CloudCompare is absent, should raise RuntimeError with install hint."""
        import shutil
        import subprocess
        from cli_anything.cloudcompare.utils import cc_backend

        # Patch shutil.which to return None for all binaries
        monkeypatch.setattr(shutil, "which", lambda x: None)
        # Patch subprocess.run to simulate empty flatpak list
        monkeypatch.setattr(
            subprocess,
            "run",
            lambda *a, **kw: type("R", (), {"stdout": "", "stderr": ""})(),
        )
        # Patch os.path.exists to return False for snap path
        monkeypatch.setattr(os.path, "exists", lambda p: False)

        with pytest.raises(RuntimeError, match="CloudCompare is not installed"):
            cc_backend.find_cloudcompare()


class TestCoordToSFValidation:
    def test_invalid_dimension_raises(self):
        from cli_anything.cloudcompare.utils.cc_backend import coord_to_sf

        with pytest.raises(ValueError, match="dimension must be"):
            coord_to_sf("/nonexistent.las", "/out.las", dimension="W")

    def test_invalid_dimension_in_filter_raises(self):
        from cli_anything.cloudcompare.utils.cc_backend import coord_to_sf_and_filter

        with pytest.raises(ValueError, match="dimension must be"):
            coord_to_sf_and_filter("/nonexistent.las", "/out.las", dimension="Q")


class TestNoiseFilterImport:
    def test_noise_filter_importable(self):
        """noise_filter replaces color_filter (no -FILTER command exists in CC CLI)."""
        from cli_anything.cloudcompare.utils.cc_backend import noise_filter

        assert callable(noise_filter)

    def test_noise_filter_knn_mode(self):
        """noise_filter KNN mode should not raise ValueError."""
        from cli_anything.cloudcompare.utils.cc_backend import noise_filter

        try:
            noise_filter("/nonexistent.xyz", "/out.xyz", knn=6, noisiness=1.0)
        except RuntimeError:
            pass  # CC not found — acceptable; no ValueError expected

    def test_noise_filter_radius_mode(self):
        """noise_filter RADIUS mode should not raise ValueError."""
        from cli_anything.cloudcompare.utils.cc_backend import noise_filter

        try:
            noise_filter(
                "/nonexistent.xyz",
                "/out.xyz",
                use_radius=True,
                radius=0.2,
                absolute=True,
            )
        except RuntimeError:
            pass

    def test_color_filter_removed(self):
        """color_filter must no longer exist (backed a non-existent CC command)."""
        import cli_anything.cloudcompare.utils.cc_backend as backend

        assert not hasattr(backend, "color_filter")


class TestCSFFilterValidation:
    def test_invalid_scene_raises(self):
        from cli_anything.cloudcompare.utils.cc_backend import csf_filter

        with pytest.raises(ValueError, match="scene must be"):
            csf_filter("/nonexistent.las", "/out.las", scene="OCEAN")

    def test_valid_scenes_accepted(self):
        """Valid scene names should not raise at the validation stage."""
        from cli_anything.cloudcompare.utils.cc_backend import (
            csf_filter,
            find_cloudcompare,
        )

        for scene in ("SLOPE", "RELIEF", "FLAT"):
            try:
                # Will fail because /nonexistent.las doesn't exist, but NOT
                # because of invalid scene — the ValueError is raised before CC runs.
                csf_filter("/nonexistent.las", "/out.las", scene=scene)
            except ValueError:
                pytest.fail(f"scene={scene!r} incorrectly raised ValueError")
