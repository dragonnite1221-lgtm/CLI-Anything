# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestRealWorldWorkflows:
    def test_photo_editing_workflow(self, tmp_dir, sample_image):
        """Simulate a photo editing workflow: open, adjust, export."""
        proj = create_project(width=300, height=200, name="photo_edit")
        add_from_file(proj, sample_image, name="Photo")
        add_filter(proj, "brightness", 0, {"factor": 1.15})
        add_filter(proj, "contrast", 0, {"factor": 1.1})
        add_filter(proj, "saturation", 0, {"factor": 1.2})
        add_filter(proj, "sharpness", 0, {"factor": 1.5})

        out = os.path.join(tmp_dir, "edited.jpg")
        result = render(proj, out, preset="jpeg-high", overwrite=True)
        assert os.path.exists(out)
        assert result["layers_rendered"] == 1

    def test_collage_workflow(self, tmp_dir):
        """Create a collage from multiple images."""
        images = []
        colors = ["red", "green", "blue", "yellow"]
        for color in colors:
            img = Image.new("RGB", (100, 100), color)
            path = os.path.join(tmp_dir, f"{color}.png")
            img.save(path)
            images.append(path)

        proj = create_project(width=200, height=200, name="collage")
        add_from_file(proj, images[0], name="TL")
        proj["layers"][0]["offset_x"] = 0
        proj["layers"][0]["offset_y"] = 0
        add_from_file(proj, images[1], name="TR")
        proj["layers"][0]["offset_x"] = 100
        proj["layers"][0]["offset_y"] = 0
        add_from_file(proj, images[2], name="BL")
        proj["layers"][0]["offset_x"] = 0
        proj["layers"][0]["offset_y"] = 100
        add_from_file(proj, images[3], name="BR")
        proj["layers"][0]["offset_x"] = 100
        proj["layers"][0]["offset_y"] = 100

        out = os.path.join(tmp_dir, "collage.png")
        render(proj, out, preset="png", overwrite=True)

        result = Image.open(out)
        assert result.size == (200, 200)

    def test_text_overlay_workflow(self, tmp_dir, sample_image):
        """Add text overlay to an image."""
        proj = create_project(width=300, height=200)
        add_from_file(proj, sample_image, name="Background")
        add_layer(proj, name="Title", layer_type="text")
        proj["layers"][0]["text"] = "Hello World"
        proj["layers"][0]["font_size"] = 32
        proj["layers"][0]["color"] = "#ffffff"

        out = os.path.join(tmp_dir, "text_overlay.png")
        render(proj, out, preset="png", overwrite=True)
        assert os.path.exists(out)

    def test_draw_ops_overlay_workflow(self, tmp_dir, sample_image):
        """Render non-destructive draw operations on top of an image layer."""
        proj = create_project(width=300, height=200)
        add_from_file(proj, sample_image, name="Background")
        overlay = add_layer(proj, name="Overlay", layer_type="image")
        overlay.setdefault("draw_ops", []).append(
            {
                "type": "rect",
                "x1": 10,
                "y1": 10,
                "x2": 290,
                "y2": 60,
                "fill": "#111111cc",
                "outline": "#ffffff",
                "width": 2,
            }
        )
        overlay["draw_ops"].append(
            {
                "type": "text",
                "x": 20,
                "y": 20,
                "text": "Overlay Title",
                "font": "Arial",
                "size": 24,
                "color": "#ffffff",
            }
        )

        out = os.path.join(tmp_dir, "draw_ops_overlay.png")
        render(proj, out, preset="png", overwrite=True)
        assert os.path.exists(out)

    def test_batch_filter_workflow(self, tmp_dir, sample_image):
        """Apply multiple artistic filters in sequence."""
        proj = create_project(width=300, height=200)
        add_from_file(proj, sample_image)
        add_filter(proj, "grayscale", 0, {})
        add_filter(proj, "contrast", 0, {"factor": 1.5})
        add_filter(proj, "find_edges", 0, {})

        out = os.path.join(tmp_dir, "artistic.png")
        render(proj, out, preset="png", overwrite=True)
        assert os.path.exists(out)

    def test_save_load_complex_project(self, tmp_dir, sample_image):
        """Create complex project, save, reload, verify integrity."""
        proj = create_project(width=300, height=200, name="complex")
        add_from_file(proj, sample_image, name="Photo")
        add_layer(
            proj, name="Overlay", layer_type="solid", fill="#ff000080", opacity=0.5
        )
        add_layer(proj, name="Text", layer_type="text")
        add_filter(proj, "brightness", 2, {"factor": 1.3})  # On bottom layer (Photo)
        add_filter(proj, "gaussian_blur", 2, {"radius": 2.0})

        path = os.path.join(tmp_dir, "complex.json")
        save_project(proj, path)

        loaded = open_project(path)
        assert len(loaded["layers"]) == 3
        assert loaded["layers"][2]["filters"][0]["name"] == "brightness"
        assert loaded["layers"][2]["filters"][1]["name"] == "gaussian_blur"
