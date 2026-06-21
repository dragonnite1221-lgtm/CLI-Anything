# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestImpress:
    def _make_doc(self):
        return create_document(doc_type="impress")

    def test_add_slide(self):
        proj = self._make_doc()
        slide = add_slide(proj, title="Welcome", content="Hello")
        assert slide["title"] == "Welcome"
        assert len(proj["slides"]) == 1

    def test_add_slide_at_position(self):
        proj = self._make_doc()
        add_slide(proj, title="First")
        add_slide(proj, title="Third")
        add_slide(proj, title="Second", position=1)
        assert proj["slides"][1]["title"] == "Second"

    def test_remove_slide(self):
        proj = self._make_doc()
        add_slide(proj, title="Remove Me")
        removed = remove_slide(proj, 0)
        assert removed["title"] == "Remove Me"
        assert len(proj["slides"]) == 0

    def test_remove_slide_empty(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="No slides"):
            remove_slide(proj, 0)

    def test_set_slide_content(self):
        proj = self._make_doc()
        add_slide(proj, title="Old Title", content="Old Content")
        slide = set_slide_content(proj, 0, title="New Title")
        assert slide["title"] == "New Title"
        assert slide["content"] == "Old Content"  # Unchanged

    def test_add_element(self):
        proj = self._make_doc()
        add_slide(proj, title="Slide 1")
        elem = add_slide_element(proj, 0, text="Box text")
        assert elem["type"] == "text_box"
        assert elem["text"] == "Box text"

    def test_remove_element(self):
        proj = self._make_doc()
        add_slide(proj, title="S1")
        add_slide_element(proj, 0, text="E1")
        removed = remove_slide_element(proj, 0, 0)
        assert removed["text"] == "E1"

    def test_move_slide(self):
        proj = self._make_doc()
        add_slide(proj, title="A")
        add_slide(proj, title="B")
        add_slide(proj, title="C")
        move_slide(proj, 0, 2)
        assert proj["slides"][2]["title"] == "A"

    def test_duplicate_slide(self):
        proj = self._make_doc()
        add_slide(proj, title="Original")
        dup = duplicate_slide(proj, 0)
        assert dup["title"] == "Original (copy)"
        assert len(proj["slides"]) == 2

    def test_list_slides(self):
        proj = self._make_doc()
        add_slide(proj, title="S1")
        add_slide(proj, title="S2")
        result = list_slides(proj)
        assert len(result) == 2
        assert result[0]["title"] == "S1"

    def test_get_slide(self):
        proj = self._make_doc()
        add_slide(proj, title="Test Slide")
        slide = get_slide(proj, 0)
        assert slide["title"] == "Test Slide"

    def test_impress_rejects_writer(self):
        proj = create_document(doc_type="writer")
        with pytest.raises(ValueError, match="expected 'impress'"):
            add_slide(proj, title="No")

    def test_invalid_element_type(self):
        proj = self._make_doc()
        add_slide(proj, title="S1")
        with pytest.raises(ValueError, match="Invalid element type"):
            add_slide_element(proj, 0, element_type="video")
