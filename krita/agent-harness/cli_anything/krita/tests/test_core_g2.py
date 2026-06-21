# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestExport:
    def test_list_presets(self):
        presets = list_presets()
        assert len(presets) > 0
        assert all("name" in p for p in presets)

    def test_get_supported_formats(self):
        formats = get_supported_formats()
        assert "png" in formats
        assert "jpg" in formats

    def test_export_presets_keys(self):
        for name, preset in EXPORT_PRESETS.items():
            assert "extension" in preset or "format" in preset, (
                f"Preset {name} missing format key"
            )
            assert "description" in preset, f"Preset {name} missing 'description'"

    def test_build_kra_from_project(self, tmp_dir, sample_project):
        kra_path = os.path.join(tmp_dir, "test.kra")
        result = build_kra_from_project(sample_project, kra_path)
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0

    def test_kra_has_mimetype(self, tmp_dir, sample_project):
        kra_path = os.path.join(tmp_dir, "test.kra")
        build_kra_from_project(sample_project, kra_path)
        with zipfile.ZipFile(kra_path, "r") as zf:
            assert "mimetype" in zf.namelist()
            assert zf.read("mimetype") == b"application/x-kra"

    def test_kra_has_maindoc(self, tmp_dir, sample_project):
        kra_path = os.path.join(tmp_dir, "test.kra")
        build_kra_from_project(sample_project, kra_path)
        with zipfile.ZipFile(kra_path, "r") as zf:
            assert "maindoc.xml" in zf.namelist()
            content = zf.read("maindoc.xml").decode("utf-8")
            assert "krita" in content.lower() or "DOC" in content

    def test_kra_has_documentinfo(self, tmp_dir, sample_project):
        kra_path = os.path.join(tmp_dir, "test.kra")
        build_kra_from_project(sample_project, kra_path)
        with zipfile.ZipFile(kra_path, "r") as zf:
            assert "documentinfo.xml" in zf.namelist()


class TestKritaBackend:
    def test_find_krita(self):
        from cli_anything.krita.utils.krita_backend import find_krita

        path = find_krita()
        assert path is not None
        assert os.path.exists(path)

    def test_get_version(self):
        from cli_anything.krita.utils.krita_backend import get_version

        version = get_version()
        assert isinstance(version, str)
        assert len(version) > 0
