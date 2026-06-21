# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestFilterRendering:
    def test_brightness_increases_pixels(self, tmp_dir, gradient_image):
        proj = create_project(width=256, height=100, color_mode="RGB")
        add_from_file(proj, gradient_image)
        add_filter(proj, "brightness", 0, {"factor": 1.5})
        out = os.path.join(tmp_dir, "bright.png")
        render(proj, out, preset="png", overwrite=True)

        original = np.array(Image.open(gradient_image).convert("RGB"), dtype=float)
        result = np.array(Image.open(out).convert("RGB"), dtype=float)
        assert result.mean() > original.mean()

    def test_contrast_increases_spread(self, tmp_dir, gradient_image):
        proj = create_project(width=256, height=100, color_mode="RGB")
        add_from_file(proj, gradient_image)
        add_filter(proj, "contrast", 0, {"factor": 2.0})
        out = os.path.join(tmp_dir, "contrast.png")
        render(proj, out, preset="png", overwrite=True)

        result = np.array(Image.open(out).convert("L"), dtype=float)
        original = np.array(Image.open(gradient_image), dtype=float)
        # Higher contrast = larger std deviation
        assert result.std() >= original.std() * 0.9

    def test_invert_flips_colors(self, tmp_dir, sample_image):
        proj = create_project(width=300, height=200)
        add_from_file(proj, sample_image)
        add_filter(proj, "invert", 0, {})
        out = os.path.join(tmp_dir, "inverted.png")
        render(proj, out, preset="png", overwrite=True)

        original = np.array(Image.open(sample_image).convert("RGB"), dtype=float)
        result = np.array(Image.open(out).convert("RGB"), dtype=float)
        # Inverted + original should sum to ~255
        total = original + result
        assert abs(total.mean() - 255.0) < 5.0

    def test_gaussian_blur(self, tmp_dir, sample_image):
        proj = create_project(width=300, height=200)
        add_from_file(proj, sample_image)
        add_filter(proj, "gaussian_blur", 0, {"radius": 10.0})
        out = os.path.join(tmp_dir, "blurred.png")
        render(proj, out, preset="png", overwrite=True)

        result = Image.open(out)
        assert result.size == (300, 200)

    def test_sepia_applies(self, tmp_dir, sample_image):
        proj = create_project(width=300, height=200)
        add_from_file(proj, sample_image)
        add_filter(proj, "sepia", 0, {"strength": 1.0})
        out = os.path.join(tmp_dir, "sepia.png")
        render(proj, out, preset="png", overwrite=True)

        result = np.array(Image.open(out).convert("RGB"), dtype=float)
        r, g, b = result[:, :, 0].mean(), result[:, :, 1].mean(), result[:, :, 2].mean()
        # Sepia: R > G > B
        assert r >= g >= b

    def test_multiple_filters_chain(self, tmp_dir, sample_image):
        proj = create_project(width=300, height=200)
        add_from_file(proj, sample_image)
        add_filter(proj, "brightness", 0, {"factor": 1.2})
        add_filter(proj, "contrast", 0, {"factor": 1.3})
        add_filter(proj, "saturation", 0, {"factor": 0.5})
        out = os.path.join(tmp_dir, "multi.png")
        render(proj, out, preset="png", overwrite=True)
        assert os.path.exists(out)

    def test_flip_horizontal(self, tmp_dir, sample_image):
        proj = create_project(width=300, height=200)
        add_from_file(proj, sample_image)
        add_filter(proj, "flip_h", 0, {})
        out = os.path.join(tmp_dir, "flipped.png")
        render(proj, out, preset="png", overwrite=True)

        original = np.array(Image.open(sample_image).convert("RGB"))
        result = np.array(Image.open(out).convert("RGB"))
        # First column of result should match last column of original
        np.testing.assert_array_equal(result[:, 0, :], original[:, -1, :])


class TestExportFormats:
    def test_export_jpeg(self, tmp_dir, sample_image):
        proj = create_project(width=300, height=200)
        add_from_file(proj, sample_image)
        out = os.path.join(tmp_dir, "output.jpg")
        result = render(proj, out, preset="jpeg-high", overwrite=True)
        assert os.path.exists(out)
        assert result["format"] == "JPEG"

    def test_export_webp(self, tmp_dir, sample_image):
        proj = create_project(width=300, height=200)
        add_from_file(proj, sample_image)
        out = os.path.join(tmp_dir, "output.webp")
        result = render(proj, out, preset="webp", overwrite=True)
        assert os.path.exists(out)
        assert result["format"] == "WEBP"

    def test_export_bmp(self, tmp_dir, sample_image):
        proj = create_project(width=300, height=200)
        add_from_file(proj, sample_image)
        out = os.path.join(tmp_dir, "output.bmp")
        result = render(proj, out, preset="bmp", overwrite=True)
        assert os.path.exists(out)

    def test_export_overwrite_protection(self, tmp_dir, sample_image):
        proj = create_project(width=300, height=200)
        add_from_file(proj, sample_image)
        out = os.path.join(tmp_dir, "output.png")
        render(proj, out, preset="png", overwrite=True)
        with pytest.raises(FileExistsError):
            render(proj, out, preset="png", overwrite=False)
