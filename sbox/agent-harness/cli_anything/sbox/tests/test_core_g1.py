# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestScene:
    """Tests for cli_anything.sbox.core.scene."""

    def test_create_scene_with_defaults(self, tmp_path):
        """Create scene with default objects (Sun, Skybox, Plane, Camera)."""
        scene_path = str(tmp_path / "test.scene")
        data = create_scene("test", output_path=scene_path)

        objects = data["GameObjects"]
        names = [obj["Name"] for obj in objects]
        assert "Sun" in names
        assert "2D Skybox" in names
        assert "Plane" in names
        assert "Camera" in names

        props = data["SceneProperties"]
        assert props["FixedUpdateFrequency"] == 50
        assert props["NetworkFrequency"] == 60

    def test_create_scene_empty(self, tmp_path):
        """Create scene without defaults."""
        data = create_scene("empty", include_defaults=False)
        assert data["GameObjects"] == []
        assert data["Title"] == "empty"

    def test_list_objects(self, tmp_path):
        """List objects in a scene."""
        scene_path = str(tmp_path / "list.scene")
        create_scene("list", output_path=scene_path)

        objects = list_objects(scene_path)
        assert len(objects) >= 4  # Sun, Skybox, Plane, Camera
        for obj in objects:
            assert "guid" in obj
            assert "name" in obj
            assert "position" in obj
            assert "component_types" in obj

    def test_add_object(self, tmp_path):
        """Add a named object and verify it appears in list."""
        scene_path = str(tmp_path / "add.scene")
        create_scene("add", output_path=scene_path)

        guid = add_object(scene_path, "Turret", position="100,0,50")
        assert guid is not None

        objects = list_objects(scene_path)
        turret = [o for o in objects if o["name"] == "Turret"]
        assert len(turret) == 1
        assert turret[0]["guid"] == guid
        assert turret[0]["position"] == "100,0,50"

    def test_add_object_with_components(self, tmp_path):
        """Add object with component presets."""
        scene_path = str(tmp_path / "comps.scene")
        create_scene("comps", output_path=scene_path)

        guid = add_object(
            scene_path,
            "PhysicsBox",
            components=["model", "box_collider", "rigidbody"],
        )

        objects = list_objects(scene_path)
        box = [o for o in objects if o["name"] == "PhysicsBox"][0]
        types = box["component_types"]
        assert "Sandbox.ModelRenderer" in types
        assert "Sandbox.BoxCollider" in types
        assert "Sandbox.Rigidbody" in types

    def test_remove_object_by_name(self, tmp_path):
        """Remove an object and verify it's gone."""
        scene_path = str(tmp_path / "rem_name.scene")
        create_scene("rem_name", output_path=scene_path)
        add_object(scene_path, "Removable")

        removed = remove_object(scene_path, name="Removable")
        assert removed is True

        objects = list_objects(scene_path)
        names = [o["name"] for o in objects]
        assert "Removable" not in names

    def test_remove_object_by_guid(self, tmp_path):
        """Remove by GUID."""
        scene_path = str(tmp_path / "rem_guid.scene")
        create_scene("rem_guid", output_path=scene_path)
        guid = add_object(scene_path, "ByGuid")

        removed = remove_object(scene_path, guid=guid)
        assert removed is True

        objects = list_objects(scene_path)
        guids = [o["guid"] for o in objects]
        assert guid not in guids

    def test_find_object(self, tmp_path):
        """Find object by name and by GUID."""
        scene_path = str(tmp_path / "find.scene")
        create_scene("find", output_path=scene_path)
        guid = add_object(scene_path, "Findable")

        data = load_scene(scene_path)

        # Find by name
        obj_by_name = find_object(data, name="Findable")
        assert obj_by_name is not None
        assert obj_by_name["Name"] == "Findable"

        # Find by guid
        obj_by_guid = find_object(data, guid=guid)
        assert obj_by_guid is not None
        assert obj_by_guid["__guid"] == guid

        # Not found
        assert find_object(data, name="NonExistent") is None

    def test_add_component(self, tmp_path):
        """Add a component to an existing object."""
        scene_path = str(tmp_path / "add_comp.scene")
        create_scene("add_comp", output_path=scene_path)
        obj_guid = add_object(scene_path, "Target")

        comp_guid = add_component(scene_path, obj_guid, "rigidbody")
        assert comp_guid is not None

        data = load_scene(scene_path)
        obj = find_object(data, guid=obj_guid)
        comp_types = [c["__type"] for c in obj["Components"]]
        assert "Sandbox.Rigidbody" in comp_types

    def test_remove_component(self, tmp_path):
        """Remove a component from an object."""
        scene_path = str(tmp_path / "rem_comp.scene")
        create_scene("rem_comp", output_path=scene_path)
        obj_guid = add_object(scene_path, "WithRB", components=["rigidbody", "model"])

        removed = remove_component(
            scene_path, obj_guid, component_type="Sandbox.Rigidbody"
        )
        assert removed is True

        data = load_scene(scene_path)
        obj = find_object(data, guid=obj_guid)
        comp_types = [c["__type"] for c in obj["Components"]]
        assert "Sandbox.Rigidbody" not in comp_types
        # model should still be there
        assert "Sandbox.ModelRenderer" in comp_types

    def test_scene_guid_uniqueness(self, tmp_path):
        """All GUIDs in a scene should be unique."""
        scene_path = str(tmp_path / "guids.scene")
        create_scene("guids", output_path=scene_path)
        add_object(scene_path, "Extra1", components=["model", "rigidbody"])
        add_object(scene_path, "Extra2", components=["camera"])

        data = load_scene(scene_path)
        guids = []

        def collect_guids(objects):
            for obj in objects:
                if "__guid" in obj:
                    guids.append(obj["__guid"])
                for comp in obj.get("Components", []):
                    if "__guid" in comp:
                        guids.append(comp["__guid"])
                collect_guids(obj.get("Children", []))

        collect_guids(data.get("GameObjects", []))

        assert len(guids) == len(set(guids)), (
            f"Duplicate GUIDs found: {len(guids)} total, {len(set(guids))} unique"
        )

    def test_scene_json_valid(self, tmp_path):
        """Generated scene is valid JSON with expected structure."""
        scene_path = str(tmp_path / "valid.scene")
        create_scene("valid", output_path=scene_path)

        with open(scene_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "GameObjects" in data
        assert "SceneProperties" in data
        assert "Title" in data
        assert "__version" in data
        assert isinstance(data["GameObjects"], list)
        assert isinstance(data["SceneProperties"], dict)
