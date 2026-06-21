# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCalc:
    def _make_doc(self):
        return create_document(doc_type="calc")

    def test_add_sheet(self):
        proj = self._make_doc()
        sheet = add_sheet(proj, name="Data")
        assert sheet["name"] == "Data"
        assert len(proj["sheets"]) == 2  # Sheet1 + Data

    def test_add_sheet_duplicate_name(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="already exists"):
            add_sheet(proj, name="Sheet1")

    def test_remove_sheet(self):
        proj = self._make_doc()
        add_sheet(proj, name="Extra")
        removed = remove_sheet(proj, 1)
        assert removed["name"] == "Extra"
        assert len(proj["sheets"]) == 1

    def test_remove_last_sheet(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="Cannot remove the last"):
            remove_sheet(proj, 0)

    def test_rename_sheet(self):
        proj = self._make_doc()
        sheet = rename_sheet(proj, 0, "Renamed")
        assert sheet["name"] == "Renamed"

    def test_set_cell_string(self):
        proj = self._make_doc()
        result = set_cell(proj, "A1", "Hello")
        assert result["value"] == "Hello"
        assert result["type"] == "string"

    def test_set_cell_float(self):
        proj = self._make_doc()
        result = set_cell(proj, "B2", "42.5", cell_type="float")
        assert result["value"] == 42.5

    def test_set_cell_formula(self):
        proj = self._make_doc()
        result = set_cell(proj, "C1", "0", formula="=A1+B1")
        assert result["formula"] == "=A1+B1"

    def test_get_cell(self):
        proj = self._make_doc()
        set_cell(proj, "A1", "Test")
        result = get_cell(proj, "A1")
        assert result["value"] == "Test"

    def test_get_cell_empty(self):
        proj = self._make_doc()
        result = get_cell(proj, "Z99")
        assert result["type"] == "empty"
        assert result["value"] is None

    def test_clear_cell(self):
        proj = self._make_doc()
        set_cell(proj, "A1", "Temp")
        result = clear_cell(proj, "A1")
        assert result["cleared"] is True
        result2 = get_cell(proj, "A1")
        assert result2["type"] == "empty"

    def test_invalid_cell_ref(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="Invalid cell reference"):
            set_cell(proj, "123", "Bad")

    def test_list_sheets(self):
        proj = self._make_doc()
        add_sheet(proj, name="Sheet2")
        result = list_sheets(proj)
        assert len(result) == 2
        assert result[0]["name"] == "Sheet1"
        assert result[1]["name"] == "Sheet2"

    def test_get_sheet_data(self):
        proj = self._make_doc()
        set_cell(proj, "A1", "X")
        set_cell(proj, "B1", "Y")
        data = get_sheet_data(proj)
        assert data["cell_count"] == 2

    def test_calc_rejects_writer(self):
        proj = create_document(doc_type="writer")
        with pytest.raises(ValueError, match="expected 'calc'"):
            add_sheet(proj, name="S1")

    def test_cell_ref_case_insensitive(self):
        proj = self._make_doc()
        set_cell(proj, "a1", "lower")
        result = get_cell(proj, "A1")
        assert result["value"] == "lower"
