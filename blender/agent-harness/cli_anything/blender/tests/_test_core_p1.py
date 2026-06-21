# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestObjects:
    def _make_scene(self):
        return create_scene()

    def test_add_cube(self):
        proj = self._make_scene()
        obj = add_object(proj, mesh_type="cube", name="TestCube")
        assert obj["name"] == "TestCube"
        assert obj["type"] == "MESH"
        assert obj["mesh_type"] == "cube"
        assert len(proj["objects"]) == 1

    def test_add_sphere(self):
        proj = self._make_scene()
        obj = add_object(proj, mesh_type="sphere")
        assert obj["mesh_type"] == "sphere"
        assert obj["mesh_params"]["radius"] == 1.0
        assert obj["mesh_params"]["segments"] == 32

    def test_add_all_primitives(self):
        proj = self._make_scene()
        for prim in MESH_PRIMITIVES:
            obj = add_object(proj, mesh_type=prim)
            assert obj["mesh_type"] == prim
        assert len(proj["objects"]) == len(MESH_PRIMITIVES)

    def test_add_with_location(self):
        proj = self._make_scene()
        obj = add_object(proj, location=[1.0, 2.0, 3.0])
        assert obj["location"] == [1.0, 2.0, 3.0]

    def test_add_with_rotation_and_scale(self):
        proj = self._make_scene()
        obj = add_object(proj, rotation=[90.0, 0.0, 45.0], scale=[2.0, 2.0, 2.0])
        assert obj["rotation"] == [90.0, 0.0, 45.0]
        assert obj["scale"] == [2.0, 2.0, 2.0]

    def test_add_with_custom_params(self):
        proj = self._make_scene()
        obj = add_object(proj, mesh_type="sphere", mesh_params={"radius": 2.5, "segments": 64})
        assert obj["mesh_params"]["radius"] == 2.5
        assert obj["mesh_params"]["segments"] == 64

    def test_add_invalid_mesh_type(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="Unknown mesh type"):
            add_object(proj, mesh_type="octahedron")

    def test_add_invalid_location(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="3 components"):
            add_object(proj, location=[1.0, 2.0])

    def test_unique_names(self):
        proj = self._make_scene()
        obj1 = add_object(proj, name="Cube")
        obj2 = add_object(proj, name="Cube")
        assert obj1["name"] != obj2["name"]

    def test_unique_ids(self):
        proj = self._make_scene()
        obj1 = add_object(proj, name="A")
        obj2 = add_object(proj, name="B")
        assert obj1["id"] != obj2["id"]

    def test_remove_object(self):
        proj = self._make_scene()
        add_object(proj, name="A")
        add_object(proj, name="B")
        removed = remove_object(proj, 0)
        assert removed["name"] == "A"
        assert len(proj["objects"]) == 1

    def test_remove_object_empty(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="No objects"):
            remove_object(proj, 0)

    def test_remove_object_invalid_index(self):
        proj = self._make_scene()
        add_object(proj)
        with pytest.raises(IndexError):
            remove_object(proj, 5)

    def test_duplicate_object(self):
        proj = self._make_scene()
        add_object(proj, name="Original")
        dup = duplicate_object(proj, 0)
        assert "copy" in dup["name"].lower() or "Original" in dup["name"]
        assert len(proj["objects"]) == 2
        assert dup["id"] != proj["objects"][0]["id"]

    def test_transform_translate(self):
        proj = self._make_scene()
        add_object(proj, location=[0, 0, 0])
        obj = transform_object(proj, 0, translate=[1.0, 2.0, 3.0])
        assert obj["location"] == [1.0, 2.0, 3.0]

    def test_transform_rotate(self):
        proj = self._make_scene()
        add_object(proj, rotation=[0, 0, 0])
        obj = transform_object(proj, 0, rotate=[90.0, 0.0, 0.0])
        assert obj["rotation"] == [90.0, 0.0, 0.0]

    def test_transform_scale(self):
        proj = self._make_scene()
        add_object(proj, scale=[1, 1, 1])
        obj = transform_object(proj, 0, scale=[2.0, 3.0, 4.0])
        assert obj["scale"] == [2.0, 3.0, 4.0]

    def test_transform_compound(self):
        proj = self._make_scene()
        add_object(proj, location=[1, 0, 0])
        obj = transform_object(proj, 0, translate=[1, 0, 0], scale=[2, 2, 2])
        assert obj["location"] == [2.0, 0.0, 0.0]
        assert obj["scale"] == [2.0, 2.0, 2.0]

    def test_set_property_name(self):
        proj = self._make_scene()
        add_object(proj, name="Old")
        set_object_property(proj, 0, "name", "New")
        assert proj["objects"][0]["name"] == "New"

    def test_set_property_visible(self):
        proj = self._make_scene()
        add_object(proj)
        set_object_property(proj, 0, "visible", "false")
        assert proj["objects"][0]["visible"] is False

    def test_set_property_parent(self):
        proj = self._make_scene()
        parent = add_object(proj, name="Parent")
        add_object(proj, name="Child")
        set_object_property(proj, 1, "parent", 0)
        assert proj["objects"][1]["parent"] == parent["id"]

    def test_set_property_parent_invalid_index(self):
        proj = self._make_scene()
        add_object(proj, name="Child")
        with pytest.raises(IndexError, match="Parent index 2 out of range"):
            set_object_property(proj, 0, "parent", 2)

    def test_set_property_parent_self(self):
        proj = self._make_scene()
        add_object(proj, name="Solo")
        with pytest.raises(ValueError, match="cannot be its own parent"):
            set_object_property(proj, 0, "parent", 0)

    def test_set_property_invalid(self):
        proj = self._make_scene()
        add_object(proj)
        with pytest.raises(ValueError, match="Unknown property"):
            set_object_property(proj, 0, "bogus", "value")

    def test_get_object(self):
        proj = self._make_scene()
        add_object(proj, name="Test")
        obj = get_object(proj, 0)
        assert obj["name"] == "Test"

    def test_list_objects(self):
        proj = self._make_scene()
        add_object(proj, name="A")
        add_object(proj, name="B")
        result = list_objects(proj)
        assert len(result) == 2

    def test_object_added_to_collection(self):
        proj = self._make_scene()
        obj = add_object(proj, mesh_type="cube")
        assert obj["id"] in proj["collections"][0]["objects"]

    def test_empty_object(self):
        proj = self._make_scene()
        obj = add_object(proj, mesh_type="empty")
        assert obj["type"] == "EMPTY"

    def test_add_monkey(self):
        proj = self._make_scene()
        obj = add_object(proj, mesh_type="monkey")
        assert obj["mesh_type"] == "monkey"

    def test_add_torus_with_params(self):
        proj = self._make_scene()
        obj = add_object(proj, mesh_type="torus",
                         mesh_params={"major_radius": 2.0, "minor_radius": 0.5})
        assert obj["mesh_params"]["major_radius"] == 2.0
        assert obj["mesh_params"]["minor_radius"] == 0.5
