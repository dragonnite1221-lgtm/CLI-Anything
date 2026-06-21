# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestProjectPackages:
    """Tests for add_package and remove_package."""

    def test_add_package(self, tmp_path):
        info = create_project("test", output_dir=str(tmp_path))
        sbproj = info["sbproj"]
        result = add_package(sbproj, "facepunch.libsdf")
        assert "facepunch.libsdf" in result["package_references"]

    def test_add_duplicate_package(self, tmp_path):
        info = create_project("test", output_dir=str(tmp_path))
        sbproj = info["sbproj"]
        add_package(sbproj, "facepunch.libsdf")
        with pytest.raises(ValueError, match="already referenced"):
            add_package(sbproj, "facepunch.libsdf")

    def test_remove_package(self, tmp_path):
        info = create_project("test", output_dir=str(tmp_path))
        sbproj = info["sbproj"]
        add_package(sbproj, "facepunch.libsdf")
        add_package(sbproj, "local.mylib")
        result = remove_package(sbproj, "facepunch.libsdf")
        assert "facepunch.libsdf" not in result["package_references"]
        assert "local.mylib" in result["package_references"]

    def test_remove_missing_package(self, tmp_path):
        info = create_project("test", output_dir=str(tmp_path))
        sbproj = info["sbproj"]
        with pytest.raises(ValueError, match="not found"):
            remove_package(sbproj, "nonexistent.pkg")


class TestPrefabComponents:
    """Tests for prefab add-component and remove-component."""

    def test_prefab_add_component(self, tmp_path):
        path = str(tmp_path / "test.prefab")
        create_prefab("TestPrefab", output_path=path, components=["model"])
        data = load_prefab(path)
        assert len(data["RootObject"]["Components"]) == 1
        root = data["RootObject"]
        comp = copy.deepcopy(COMPONENT_PRESETS["rigidbody"])
        comp["__guid"] = str(uuid.uuid4())
        root["Components"].append(comp)
        save_prefab(path, data)
        data2 = load_prefab(path)
        assert len(data2["RootObject"]["Components"]) == 2
        types = [c["__type"] for c in data2["RootObject"]["Components"]]
        assert "Sandbox.Rigidbody" in types

    def test_prefab_remove_component(self, tmp_path):
        path = str(tmp_path / "test.prefab")
        create_prefab("TestPrefab", output_path=path, components=["model", "rigidbody"])
        data = load_prefab(path)
        assert len(data["RootObject"]["Components"]) == 2
        root = data["RootObject"]
        root["Components"] = [
            c for c in root["Components"] if c["__type"] != "Sandbox.Rigidbody"
        ]
        save_prefab(path, data)
        data2 = load_prefab(path)
        assert len(data2["RootObject"]["Components"]) == 1
        assert data2["RootObject"]["Components"][0]["__type"] == "Sandbox.ModelRenderer"


class TestCollisionRemoveLayer:
    """Test collision remove-layer success path."""

    def test_remove_custom_layer(self, tmp_path):
        path = str(tmp_path / "Collision.config")
        save_collision_config(path, get_default_collision_config())
        add_layer(path, "projectile", default="Collide")
        add_rule(path, "projectile", "solid", result="Collide")
        data = load_collision_config(path)
        assert "projectile" in data["Defaults"]
        removed = remove_layer(path, "projectile")
        assert removed is True
        data2 = load_collision_config(path)
        assert "projectile" not in data2["Defaults"]
        for pair in data2["Pairs"]:
            assert pair["a"] != "projectile" and pair["b"] != "projectile"


class TestJointPresets:
    """Test joint component presets in scenes."""

    def test_add_object_with_joints(self, tmp_path):
        scene_path = str(tmp_path / "test.scene")
        create_scene("test", output_path=scene_path, include_defaults=False)
        add_object(scene_path, "Door", components=["model", "hinge_joint"])
        objects = list_objects(scene_path)
        assert len(objects) == 1
        types = objects[0]["component_types"]
        assert "Sandbox.ModelRenderer" in types
        assert "Sandbox.HingeJoint" in types
