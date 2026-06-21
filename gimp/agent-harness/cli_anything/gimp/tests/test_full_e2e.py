# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestProjectLifecycle:
    def test_create_save_open_roundtrip(self, tmp_dir):
        proj = create_project(name="roundtrip")
        path = os.path.join(tmp_dir, "project.gimp-cli.json")
        save_project(proj, path)
        loaded = open_project(path)
        assert loaded["name"] == "roundtrip"
        assert loaded["canvas"]["width"] == 1920

    def test_project_with_layers_roundtrip(self, tmp_dir, sample_image):
        proj = create_project(name="with_layers")
        add_from_file(proj, sample_image, name="Photo")
        add_filter(proj, "brightness", 0, {"factor": 1.3})
        path = os.path.join(tmp_dir, "project.json")
        save_project(proj, path)
        loaded = open_project(path)
        assert len(loaded["layers"]) == 1
        assert loaded["layers"][0]["filters"][0]["name"] == "brightness"

    def test_project_info_with_layers(self, sample_image):
        proj = create_project()
        add_from_file(proj, sample_image)
        info = get_project_info(proj)
        assert info["layer_count"] == 1


class TestLayerOperations:
    def test_add_from_file(self, sample_image):
        proj = create_project()
        layer = add_from_file(proj, sample_image)
        assert layer["source"] == os.path.abspath(sample_image)
        assert layer["width"] == 300
        assert layer["height"] == 200

    def test_multiple_layers_order(self, tmp_dir):
        img1 = Image.new("RGB", (100, 100), "red")
        img2 = Image.new("RGB", (100, 100), "blue")
        p1 = os.path.join(tmp_dir, "red.png")
        p2 = os.path.join(tmp_dir, "blue.png")
        img1.save(p1)
        img2.save(p2)

        proj = create_project(width=100, height=100)
        add_from_file(proj, p1, name="Red")
        add_from_file(proj, p2, name="Blue")
        layers = list_layers(proj)
        assert layers[0]["name"] == "Blue"  # Top
        assert layers[1]["name"] == "Red"  # Bottom
