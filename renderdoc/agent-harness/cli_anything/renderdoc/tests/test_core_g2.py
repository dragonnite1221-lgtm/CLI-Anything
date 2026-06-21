# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestTexturesModule:
    def _make_mock_tex(self, rid="123", w=512, h=512, mips=1, fmt="R8G8B8A8_UNORM"):
        tex = MagicMock()
        tex.resourceId = MagicMock()
        tex.resourceId.__str__ = lambda s: rid
        tex.name = f"Texture_{rid}"
        tex.width = w
        tex.height = h
        tex.depth = 1
        tex.mips = mips
        tex.arraysize = 1
        tex.msQual = 0
        tex.msSamp = 1
        tex.format = MagicMock()
        tex.format.__str__ = lambda s: fmt
        tex.dimension = 2
        tex.type = MagicMock()
        tex.type.__str__ = lambda s: "Texture2D"
        tex.cubemap = False
        tex.byteSize = w * h * 4
        tex.creationFlags = 0
        return tex

    def test_tex_to_dict(self):
        from cli_anything.renderdoc.core.textures import _tex_to_dict

        tex = self._make_mock_tex()
        d = _tex_to_dict(tex)
        assert d["resourceId"] == "123"
        assert d["width"] == 512
        assert d["height"] == 512
        assert d["mips"] == 1

    def test_list_textures(self):
        from cli_anything.renderdoc.core.textures import list_textures

        controller = MagicMock()
        controller.GetTextures.return_value = [
            self._make_mock_tex("1", 256, 256),
            self._make_mock_tex("2", 1024, 1024),
        ]
        result = list_textures(controller)
        assert len(result) == 2
        assert result[0]["width"] == 256
        assert result[1]["width"] == 1024

    def test_get_texture_found(self):
        from cli_anything.renderdoc.core.textures import get_texture

        controller = MagicMock()
        controller.GetTextures.return_value = [
            self._make_mock_tex("42", 800, 600),
        ]
        result = get_texture(controller, "42")
        assert result is not None
        assert result["width"] == 800

    def test_get_texture_not_found(self):
        from cli_anything.renderdoc.core.textures import get_texture

        controller = MagicMock()
        controller.GetTextures.return_value = []
        result = get_texture(controller, "999")
        assert result is None
