# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestStylesInODF:
    def test_custom_style_in_odt(self, tmp_dir):
        proj = create_document(doc_type="writer")
        create_style(
            proj,
            "MyTitle",
            properties={"font_size": "24pt", "bold": True, "color": "#003366"},
        )
        add_paragraph(proj, text="Styled text")
        apply_style(proj, "MyTitle", 0)

        path = os.path.join(tmp_dir, "styled.odt")
        to_odt(proj, path)

        parsed = parse_odf(path)
        styles_xml = parsed["styles_xml"]
        assert "MyTitle" in styles_xml
        assert "24pt" in styles_xml

    def test_page_layout_in_odt(self, tmp_dir):
        proj = create_document(doc_type="writer", profile="letter_portrait")
        add_paragraph(proj, text="Letter size")
        path = os.path.join(tmp_dir, "letter.odt")
        to_odt(proj, path)

        parsed = parse_odf(path)
        styles_xml = parsed["styles_xml"]
        assert "21.59cm" in styles_xml


class TestProjectLifecycle:
    def test_create_save_open_roundtrip(self, tmp_dir):
        proj = create_document(name="roundtrip")
        path = os.path.join(tmp_dir, "project.lo-cli.json")
        save_document(proj, path)
        loaded = open_document(path)
        assert loaded["name"] == "roundtrip"
        assert loaded["type"] == "writer"

    def test_complex_project_roundtrip(self, tmp_dir):
        proj = create_document(doc_type="writer", name="complex")
        add_heading(proj, text="Title", level=1)
        add_paragraph(proj, text="Body")
        add_table(proj, rows=2, cols=2, data=[["A", "B"], ["C", "D"]])
        create_style(proj, "Bold", properties={"bold": True})

        path = os.path.join(tmp_dir, "complex.json")
        save_document(proj, path)
        loaded = open_document(path)
        assert len(loaded["content"]) == 3
        assert "Bold" in loaded["styles"]

    def test_calc_project_roundtrip(self, tmp_dir):
        proj = create_document(doc_type="calc")
        set_cell(proj, "A1", "Test")
        set_cell(proj, "B1", "42", cell_type="float")
        path = os.path.join(tmp_dir, "calc.json")
        save_document(proj, path)
        loaded = open_document(path)
        assert loaded["sheets"][0]["cells"]["A1"]["value"] == "Test"
        assert loaded["sheets"][0]["cells"]["B1"]["value"] == 42.0


class TestSessionIntegration:
    def test_undo_paragraph_add(self):
        sess = Session()
        proj = create_document(doc_type="writer")
        sess.set_project(proj)

        sess.snapshot("add paragraph")
        add_paragraph(proj, text="Hello")
        assert len(proj["content"]) == 1

        sess.undo()
        assert len(sess.get_project()["content"]) == 0

    def test_undo_cell_change(self):
        sess = Session()
        proj = create_document(doc_type="calc")
        sess.set_project(proj)

        sess.snapshot("set cell")
        set_cell(proj, "A1", "Original")

        sess.snapshot("change cell")
        set_cell(proj, "A1", "Changed")

        sess.undo()
        assert sess.get_project()["sheets"][0]["cells"]["A1"]["value"] == "Original"

    def test_undo_slide_add(self):
        sess = Session()
        proj = create_document(doc_type="impress")
        sess.set_project(proj)

        sess.snapshot("add slide")
        add_slide(proj, title="Slide 1")
        assert len(proj["slides"]) == 1

        sess.undo()
        assert len(sess.get_project()["slides"]) == 0

    def test_undo_style_create(self):
        sess = Session()
        proj = create_document(doc_type="writer")
        sess.set_project(proj)

        sess.snapshot("create style")
        create_style(proj, "TestStyle")
        assert "TestStyle" in proj["styles"]

        sess.undo()
        assert "TestStyle" not in sess.get_project()["styles"]
