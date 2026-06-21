# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_project_info(self):
        proj = create_project()
        info = get_project_info(proj)
        assert info["counts"]["total_sources"] == 0

    def test_source_on_nonexistent_scene(self):
        proj = create_project()
        with pytest.raises(IndexError):
            add_source(proj, "image", scene_index=99)

    def test_filter_on_nonexistent_source(self):
        proj = create_project()
        with pytest.raises(ValueError):
            add_filter(proj, "gain", source_index=99)

    def test_remove_source_empty_scene(self):
        proj = create_project()
        with pytest.raises(ValueError):
            remove_source(proj, 0)

    def test_transform_nonexistent_source(self):
        proj = create_project()
        with pytest.raises(ValueError):
            transform_source(proj, 0, position={"x": 0, "y": 0})

    def test_negative_crop(self):
        proj = create_project()
        add_source(proj, "image")
        with pytest.raises(ValueError, match="non-negative"):
            transform_source(proj, 0, crop={"top": -1})

    def test_all_source_types_addable(self):
        proj = create_project()
        for stype in SOURCE_TYPES:
            src = add_source(proj, stype)
            assert src is not None
        assert len(proj["scenes"][0]["sources"]) == len(SOURCE_TYPES)

    def test_all_filter_types_addable(self):
        proj = create_project()
        add_source(proj, "video_capture", name="Camera")
        for ftype in FILTER_TYPES:
            filt = add_filter(proj, ftype, 0)
            assert filt is not None
        assert len(proj["scenes"][0]["sources"][0]["filters"]) == len(FILTER_TYPES)

    def test_chroma_key_invalid_color_type(self):
        proj = create_project()
        add_source(proj, "video_capture")
        with pytest.raises(ValueError):
            add_filter(proj, "chroma_key", 0, params={"key_color_type": "red"})

    def test_session_save_no_path(self):
        sess = Session()
        proj = create_project()
        sess.set_project(proj)
        with pytest.raises(ValueError, match="No save path"):
            sess.save_session()

    def test_large_scene_collection(self):
        proj = create_project()
        for i in range(20):
            add_scene(proj, name=f"Scene {i}")
        assert len(proj["scenes"]) == 21
        for i in range(21):
            add_source(proj, "text", scene_index=i, name=f"Text {i}")
        info = get_project_info(proj)
        assert info["counts"]["total_sources"] == 21
