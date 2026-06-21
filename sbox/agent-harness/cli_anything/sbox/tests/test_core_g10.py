# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestMaterial:
    """Tests for material creation and parsing."""

    def test_create_material_default(self, tmp_path):
        path = str(tmp_path / "test.vmat")
        result = create_material("test", output_path=path)
        assert result["name"] == "test"
        assert result["shader"] == "shaders/complex.vfx"
        assert os.path.isfile(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert 'shader "shaders/complex.vfx"' in content
        assert "Layer0" in content

    def test_create_material_with_textures(self, tmp_path):
        path = str(tmp_path / "brick.vmat")
        result = create_material(
            "brick",
            color_texture="textures/brick_color.tga",
            normal_texture="textures/brick_normal.tga",
            metalness=0.2,
            output_path=path,
        )
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert 'TextureColor "textures/brick_color.tga"' in content
        assert 'TextureNormal "textures/brick_normal.tga"' in content
        assert 'g_flMetalness "0.2"' in content

    def test_parse_material(self, tmp_path):
        path = str(tmp_path / "mat.vmat")
        create_material(
            "mat", color_texture="tex/color.tga", metalness=0.8, output_path=path
        )
        parsed = parse_material(path)
        assert parsed["name"] == "mat"
        assert parsed["shader"] == "shaders/complex.vfx"
        assert "TextureColor" in parsed["properties"]
        assert parsed["properties"]["g_flMetalness"] == "0.8"

    def test_list_materials(self, tmp_path):
        create_project("test", output_dir=str(tmp_path))
        mat_dir = tmp_path / "Assets" / "materials"
        mat_dir.mkdir(parents=True, exist_ok=True)
        create_material("floor", output_path=str(mat_dir / "floor.vmat"))
        create_material("wall", output_path=str(mat_dir / "wall.vmat"))
        materials = list_materials(str(tmp_path))
        names = [m["name"] for m in materials]
        assert "floor" in names
        assert "wall" in names

    def test_vmat_format(self, tmp_path):
        """Verify .vmat is text format, not JSON."""
        path = str(tmp_path / "test.vmat")
        create_material("test", output_path=path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # Should NOT be valid JSON
        try:
            json.loads(content)
            assert False, "vmat should not be JSON"
        except json.JSONDecodeError:
            pass  # Expected
