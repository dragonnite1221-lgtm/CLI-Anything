# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestProject:
    def test_create_project_defaults(self):
        proj = create_project(name="Default")
        assert proj["name"] == "Default"
        assert proj["canvas"]["width"] == 1920
        assert proj["canvas"]["height"] == 1080
        assert proj["canvas"]["colorspace"] == "RGBA"
        assert proj["canvas"]["depth"] == "U8"
        assert proj["canvas"]["resolution"] == 300
        assert len(proj["layers"]) == 1
        assert proj["layers"][0]["name"] == "Background"

    def test_create_project_custom(self):
        proj = create_project(
            name="Custom",
            width=4096,
            height=4096,
            colorspace="CMYKA",
            depth="F32",
            resolution=600,
        )
        assert proj["canvas"]["width"] == 4096
        assert proj["canvas"]["height"] == 4096
        assert proj["canvas"]["colorspace"] == "CMYKA"
        assert proj["canvas"]["depth"] == "F32"
        assert proj["canvas"]["resolution"] == 600

    def test_save_and_open_project(self, tmp_dir, sample_project):
        path = os.path.join(tmp_dir, "proj.json")
        save_project(sample_project, path)
        assert os.path.exists(path)
        loaded = open_project(path)
        assert loaded["name"] == "Test"
        assert loaded["canvas"]["width"] == 800

    def test_project_info(self, sample_project):
        info = project_info(sample_project)
        assert "name" in info
        assert "canvas" in info or "layer_count" in info

    def test_add_layer_paintlayer(self, sample_project):
        add_layer(sample_project, "Sketch", layer_type="paintlayer")
        layers = list_layers(sample_project)
        names = [l["name"] for l in layers]
        assert "Sketch" in names

    def test_add_layer_grouplayer(self, sample_project):
        add_layer(sample_project, "Group1", layer_type="grouplayer")
        layers = list_layers(sample_project)
        found = [l for l in layers if l["name"] == "Group1"]
        assert len(found) == 1
        assert found[0]["type"] == "grouplayer"

    def test_add_layer_all_types(self, sample_project):
        types = [
            "paintlayer",
            "grouplayer",
            "vectorlayer",
            "filterlayer",
            "filllayer",
            "clonelayer",
            "filelayer",
        ]
        for lt in types:
            add_layer(sample_project, f"Layer_{lt}", layer_type=lt)
        layers = list_layers(sample_project)
        assert len(layers) == 1 + len(types)  # Background + added

    def test_remove_layer(self, sample_project):
        add_layer(sample_project, "ToRemove")
        remove_layer(sample_project, "ToRemove")
        names = [l["name"] for l in list_layers(sample_project)]
        assert "ToRemove" not in names

    def test_remove_layer_not_found(self, sample_project):
        with pytest.raises((ValueError, KeyError, RuntimeError)):
            remove_layer(sample_project, "NonExistent")

    def test_list_layers(self, sample_project):
        add_layer(sample_project, "A")
        add_layer(sample_project, "B")
        layers = list_layers(sample_project)
        assert len(layers) == 3  # Background + A + B
        assert all("name" in l for l in layers)

    def test_set_layer_property_opacity(self, sample_project):
        set_layer_property(sample_project, "Background", "opacity", 128)
        layers = list_layers(sample_project)
        bg = [l for l in layers if l["name"] == "Background"][0]
        assert bg["opacity"] == 128

    def test_set_layer_property_visible(self, sample_project):
        set_layer_property(sample_project, "Background", "visible", False)
        layers = list_layers(sample_project)
        bg = [l for l in layers if l["name"] == "Background"][0]
        assert bg["visible"] is False

    def test_set_layer_property_blending(self, sample_project):
        set_layer_property(sample_project, "Background", "blending_mode", "multiply")
        layers = list_layers(sample_project)
        bg = [l for l in layers if l["name"] == "Background"][0]
        assert bg["blending_mode"] == "multiply"

    def test_add_filter(self, sample_project):
        add_filter(sample_project, "Background", "blur")
        layers = list_layers(sample_project)
        bg = [l for l in layers if l["name"] == "Background"][0]
        assert len(bg["filters"]) == 1
        assert bg["filters"][0]["name"] == "blur"

    def test_add_filter_with_config(self, sample_project):
        add_filter(sample_project, "Background", "blur", {"radius": 5.0})
        layers = list_layers(sample_project)
        bg = [l for l in layers if l["name"] == "Background"][0]
        assert bg["filters"][0]["config"]["radius"] == 5.0

    def test_set_canvas(self, sample_project):
        set_canvas(sample_project, width=3840, height=2160, resolution=150)
        assert sample_project["canvas"]["width"] == 3840
        assert sample_project["canvas"]["height"] == 2160
        assert sample_project["canvas"]["resolution"] == 150

    def test_set_canvas_partial(self, sample_project):
        original_height = sample_project["canvas"]["height"]
        set_canvas(sample_project, width=1024)
        assert sample_project["canvas"]["width"] == 1024
        assert sample_project["canvas"]["height"] == original_height
