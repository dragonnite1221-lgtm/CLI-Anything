# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestBlendModes:
    def _two_layer_project(self, tmp_dir, color1, color2, mode):
        img1 = Image.new("RGBA", (100, 100), color1)
        img2 = Image.new("RGBA", (100, 100), color2)
        p1 = os.path.join(tmp_dir, "layer1.png")
        p2 = os.path.join(tmp_dir, "layer2.png")
        img1.save(p1)
        img2.save(p2)

        proj = create_project(
            width=100, height=100, color_mode="RGBA", background="transparent"
        )
        add_from_file(proj, p1, name="Bottom")
        add_from_file(proj, p2, name="Top")
        proj["layers"][0]["blend_mode"] = mode
        return proj

    def test_multiply_darkens(self, tmp_dir):
        proj = self._two_layer_project(
            tmp_dir, (200, 200, 200, 255), (128, 128, 128, 255), "multiply"
        )
        out = os.path.join(tmp_dir, "multiply.png")
        render(proj, out, preset="png", overwrite=True)
        result = np.array(Image.open(out).convert("RGB"), dtype=float)
        # Multiply always darkens
        assert result.mean() < 200

    def test_screen_brightens(self, tmp_dir):
        proj = self._two_layer_project(
            tmp_dir, (100, 100, 100, 255), (100, 100, 100, 255), "screen"
        )
        out = os.path.join(tmp_dir, "screen.png")
        render(proj, out, preset="png", overwrite=True)
        result = np.array(Image.open(out).convert("RGB"), dtype=float)
        # Screen always brightens
        assert result.mean() > 100

    def test_difference(self, tmp_dir):
        proj = self._two_layer_project(
            tmp_dir, (200, 100, 50, 255), (100, 100, 100, 255), "difference"
        )
        out = os.path.join(tmp_dir, "diff.png")
        render(proj, out, preset="png", overwrite=True)
        result = np.array(Image.open(out).convert("RGB"), dtype=float)
        # Difference of (200,100,50) and (100,100,100) = (100,0,50)
        assert abs(result[:, :, 0].mean() - 100) < 5
        assert abs(result[:, :, 1].mean() - 0) < 5
        assert abs(result[:, :, 2].mean() - 50) < 5


class TestCanvasRendering:
    def test_scale_and_export(self, tmp_dir, sample_image):
        proj = create_project(width=300, height=200)
        add_from_file(proj, sample_image)
        scale_canvas(proj, 150, 100)
        out = os.path.join(tmp_dir, "scaled.png")
        render(proj, out, preset="png", overwrite=True)
        result = Image.open(out)
        assert result.size == (150, 100)


class TestMediaProbing:
    def test_probe_png(self, sample_image):
        info = probe_image(sample_image)
        assert info["width"] == 300
        assert info["height"] == 200
        assert info["format"] == "PNG"
        assert info["mode"] == "RGB"

    def test_probe_jpeg(self, tmp_dir):
        img = Image.new("RGB", (100, 100), "red")
        path = os.path.join(tmp_dir, "test.jpg")
        img.save(path, "JPEG")
        info = probe_image(path)
        assert info["format"] == "JPEG"
        assert info["width"] == 100

    def test_probe_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            probe_image("/nonexistent/image.png")

    def test_check_media(self, sample_image):
        proj = create_project()
        add_from_file(proj, sample_image)
        result = check_media(proj)
        assert result["status"] == "ok"
        assert result["missing"] == 0

    def test_check_media_missing(self, sample_image):
        proj = create_project()
        add_from_file(proj, sample_image)
        proj["layers"][0]["source"] = "/nonexistent/file.png"
        result = check_media(proj)
        assert result["status"] == "missing_files"


class TestSessionIntegration:
    def test_undo_layer_add(self, sample_image):
        sess = Session()
        proj = create_project()
        sess.set_project(proj)

        sess.snapshot("add layer")
        add_from_file(proj, sample_image)
        assert len(proj["layers"]) == 1

        sess.undo()
        assert len(sess.get_project()["layers"]) == 0

    def test_undo_filter_add(self, sample_image):
        sess = Session()
        proj = create_project()
        add_from_file(proj, sample_image)
        sess.set_project(proj)

        sess.snapshot("add filter")
        add_filter(proj, "brightness", 0, {"factor": 1.5})
        assert len(proj["layers"][0]["filters"]) == 1

        sess.undo()
        assert len(sess.get_project()["layers"][0]["filters"]) == 0
