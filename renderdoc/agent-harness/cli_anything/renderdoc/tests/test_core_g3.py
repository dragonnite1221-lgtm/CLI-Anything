# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestResourcesModule:
    def test_list_resources(self):
        from cli_anything.renderdoc.core.resources import list_resources

        r1 = MagicMock()
        r1.resourceId = MagicMock()
        r1.resourceId.__str__ = lambda s: "1"
        r1.name = "Backbuffer"
        r1.type = MagicMock()
        r1.type.__str__ = lambda s: "Texture"

        controller = MagicMock()
        controller.GetResources.return_value = [r1]

        result = list_resources(controller)
        assert len(result) == 1
        assert result[0]["name"] == "Backbuffer"

    def test_list_buffers(self):
        from cli_anything.renderdoc.core.resources import list_buffers

        b1 = MagicMock()
        b1.resourceId = MagicMock()
        b1.resourceId.__str__ = lambda s: "5"
        b1.length = 4096
        b1.creationFlags = 0

        controller = MagicMock()
        controller.GetBuffers.return_value = [b1]

        result = list_buffers(controller)
        assert len(result) == 1
        assert result[0]["length"] == 4096

    def test_get_buffer_data_hex(self):
        from cli_anything.renderdoc.core.resources import get_buffer_data

        b1 = MagicMock()
        b1.resourceId = MagicMock()
        b1.resourceId.__str__ = lambda s: "5"

        controller = MagicMock()
        controller.GetBuffers.return_value = [b1]
        controller.GetBufferData.return_value = b"\x01\x02\x03\x04"

        result = get_buffer_data(controller, "5", 0, 4, "hex")
        assert result["data"] == "01020304"
        assert result["length"] == 4

    def test_get_buffer_data_float32(self):
        from cli_anything.renderdoc.core.resources import get_buffer_data

        b1 = MagicMock()
        b1.resourceId = MagicMock()
        b1.resourceId.__str__ = lambda s: "5"

        controller = MagicMock()
        controller.GetBuffers.return_value = [b1]
        test_data = struct.pack("<2f", 1.0, 2.5)
        controller.GetBufferData.return_value = test_data

        result = get_buffer_data(controller, "5", 0, 8, "float32")
        assert len(result["data"]) == 2
        assert abs(result["data"][0] - 1.0) < 0.001
        assert abs(result["data"][1] - 2.5) < 0.001

    def test_get_buffer_data_not_found(self):
        from cli_anything.renderdoc.core.resources import get_buffer_data

        controller = MagicMock()
        controller.GetBuffers.return_value = []

        result = get_buffer_data(controller, "999", 0, 4, "hex")
        assert "error" in result
