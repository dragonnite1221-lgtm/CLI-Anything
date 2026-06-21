# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin2:
    def test_scene_get_object_json( self, tmp_path ):
        """Get object details via subprocess."""
        self._run( ["--json", "project", "new", "--name", "test_proj", "--output-dir", str( tmp_path )] )
        scene_path = os.path.join( str( tmp_path ), "Assets", "scenes", "minimal.scene" )

        result = self._run( ["--json", "scene", "get-object", scene_path, "--name", "Sun"] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["name"] == "Sun"
        assert "components" in data
        assert len( data["components"] ) > 0
    def test_project_add_remove_package_json( self, tmp_path ):
        """Add and remove package references via subprocess."""
        self._run( ["--json", "project", "new", "--name", "test_proj", "--output-dir", str( tmp_path )] )

        add_result = self._run( ["--json", "--project", str( tmp_path ), "project", "add-package", "facepunch.libsdf"] )
        assert add_result.returncode == 0
        data = json.loads( add_result.stdout )
        assert "facepunch.libsdf" in data["package_references"]

        rm_result = self._run( ["--json", "--project", str( tmp_path ), "project", "remove-package", "facepunch.libsdf"] )
        assert rm_result.returncode == 0
        data = json.loads( rm_result.stdout )
        assert "facepunch.libsdf" not in data["package_references"]
    def test_scene_list_presets_json( self, tmp_path ):
        """List presets via subprocess."""
        result = self._run( ["--json", "scene", "list-presets"] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert isinstance( data, list )
        assert len( data ) == 29
        names = [p["name"] for p in data]
        assert "model" in names
        assert "hinge_joint" in names
    def test_material_set_json( self, tmp_path ):
        """Update material via subprocess."""
        mat_path = os.path.join( str( tmp_path ), "test.vmat" )
        self._run( ["--json", "material", "new", "--name", "test", "-o", mat_path] )
        result = self._run( ["--json", "material", "set", mat_path, "--metalness", "0.9"] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["properties"]["g_flMetalness"] == "0.9"
    def test_sound_set_json( self, tmp_path ):
        """Update sound event via subprocess."""
        snd_path = os.path.join( str( tmp_path ), "test.sound" )
        self._run( ["--json", "sound", "new", "--name", "test", "-o", snd_path] )
        result = self._run( ["--json", "sound", "set", snd_path, "--volume", "0.3"] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["volume"] == "0.3"
    def test_prefab_add_remove_component_json( self, tmp_path ):
        """Add and remove component from prefab via subprocess."""
        prefab_path = os.path.join( str( tmp_path ), "test.prefab" )
        self._run( ["--json", "prefab", "new", "--name", "TestPrefab", "-o", prefab_path, "--components", "model"] )
        add_result = self._run( ["--json", "prefab", "add-component", prefab_path, "rigidbody"] )
        assert add_result.returncode == 0
        data = json.loads( add_result.stdout )
        assert data["type"] == "Sandbox.Rigidbody"
        rm_result = self._run( ["--json", "prefab", "remove-component", prefab_path, "--component-type", "Sandbox.Rigidbody"] )
        assert rm_result.returncode == 0
        data = json.loads( rm_result.stdout )
        assert data["removed"] is True
    def test_prefab_list_json( self, tmp_path ):
        """List prefabs via subprocess."""
        self._run( ["--json", "project", "new", "--name", "test_proj", "--output-dir", str( tmp_path )] )
        prefab_dir = os.path.join( str( tmp_path ), "Assets", "prefabs" )
        os.makedirs( prefab_dir, exist_ok=True )
        prefab_path = os.path.join( prefab_dir, "bullet.prefab" )
        self._run( ["--json", "prefab", "new", "--name", "Bullet", "-o", prefab_path, "--components", "model"] )
        result = self._run( ["--json", "--project", str( tmp_path ), "prefab", "list"] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert isinstance( data, list )
        assert any( "bullet" in p["name"] for p in data )
    def test_scene_modify_component_json( self, tmp_path ):
        """Modify component via subprocess."""
        self._run( ["--json", "project", "new", "--name", "test_proj", "--output-dir", str( tmp_path )] )
        scene_path = os.path.join( str( tmp_path ), "Assets", "scenes", "minimal.scene" )
        add_result = self._run( ["--json", "scene", "add-object", scene_path, "PhysBox", "--components", "model,rigidbody"] )
        guid = json.loads( add_result.stdout )["guid"]
        result = self._run( [
            "--json", "scene", "modify-component", scene_path, guid,
            "--component-type", "Sandbox.Rigidbody",
            "--properties", '{"Gravity": false, "LinearDamping": 10}',
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert "Gravity" in data["updated_keys"]
    def test_codegen_class_json( self, tmp_path ):
        """Generate plain class via subprocess."""
        output_path = os.path.join( str( tmp_path ), "GameUtils.cs" )
        result = self._run( [
            "--json", "codegen", "class",
            "--name", "GameUtils", "--static",
            "--properties", '[{"name":"Version","type":"string","default":"\\"1.0\\""}]',
            "-o", output_path,
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["class_name"] == "GameUtils"
        assert os.path.isfile( output_path )
        with open( output_path, "r", encoding="utf-8" ) as f:
            content = f.read()
        assert "public static class GameUtils" in content
