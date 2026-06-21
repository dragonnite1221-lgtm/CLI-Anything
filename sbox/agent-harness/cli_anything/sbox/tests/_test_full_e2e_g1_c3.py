# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin3:
    def test_localization_bulk_set_json( self, tmp_path ):
        """Bulk set translation keys via subprocess."""
        loc_path = os.path.join( str( tmp_path ), "en.json" )
        self._run( ["--json", "localization", "new", "--lang", "en", "-o", loc_path] )
        result = self._run( [
            "--json", "localization", "bulk-set", loc_path,
            "--keys", '{"game.title": "Test Game", "ui.ok": "OK"}',
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["added"] == 2
    def test_scene_query_json( self, tmp_path ):
        """scene query filters objects via subprocess."""
        scene_path = os.path.join( str( tmp_path ), "q.scene" )
        self._run( ["--json", "scene", "new", "--name", "q", "-o", scene_path, "--no-defaults"] )
        self._run( ["--json", "scene", "add-object", scene_path, "T1", "--tags", "tower", "--components", "rigidbody"] )
        self._run( ["--json", "scene", "add-object", scene_path, "T2", "--tags", "tower"] )
        self._run( ["--json", "scene", "add-object", scene_path, "E1", "--tags", "enemy"] )

        result = self._run( ["--json", "scene", "query", scene_path, "--has-tag", "tower"] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        names = sorted( r["name"] for r in data )
        assert names == ["T1", "T2"]

        # Compose two filters
        result2 = self._run( ["--json", "scene", "query", scene_path, "--has-tag", "tower", "--has-component", "rigidbody"] )
        data2 = json.loads( result2.stdout )
        assert len( data2 ) == 1
        assert data2[0]["name"] == "T1"
    def test_scene_refs_json( self, tmp_path ):
        """scene refs lists asset references via subprocess."""
        scene_path = os.path.join( str( tmp_path ), "r.scene" )
        self._run( ["--json", "scene", "new", "--name", "r", "-o", scene_path] )
        result = self._run( ["--json", "scene", "refs", scene_path] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert isinstance( data, dict )
        # Default scene has at least one model and one material
        assert "models" in data or "materials" in data
    def test_scene_bulk_modify_json( self, tmp_path ):
        """scene bulk-modify modifies all matches via subprocess."""
        scene_path = os.path.join( str( tmp_path ), "b.scene" )
        self._run( ["--json", "scene", "new", "--name", "b", "-o", scene_path, "--no-defaults"] )
        for n in ["A", "B", "C"]:
            self._run( ["--json", "scene", "add-object", scene_path, n, "--tags", "movable"] )

        result = self._run( [
            "--json", "scene", "bulk-modify", scene_path,
            "--has-tag", "movable",
            "--position", "999,888,777",
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["modified_count"] == 3

        # Verify via query
        check = self._run( ["--json", "scene", "query", scene_path, "--has-tag", "movable"] )
        for row in json.loads( check.stdout ):
            assert row["position"] == "999,888,777"
    def test_prefab_refs_json( self, tmp_path ):
        """prefab refs lists asset references via subprocess."""
        prefab_path = os.path.join( str( tmp_path ), "p.prefab" )
        self._run( ["--json", "prefab", "new", "--name", "P", "-o", prefab_path, "--components", "model,rigidbody"] )
        result = self._run( ["--json", "prefab", "refs", prefab_path] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert "models" in data
        assert any( "models/dev/box.vmdl" in r for r in data["models"] )
    def test_prefab_modify_component_json( self, tmp_path ):
        """prefab modify-component edits component props via subprocess."""
        prefab_path = os.path.join( str( tmp_path ), "m.prefab" )
        self._run( ["--json", "prefab", "new", "--name", "M", "-o", prefab_path, "--components", "rigidbody"] )
        result = self._run( [
            "--json", "prefab", "modify-component", prefab_path,
            "--component-type", "Sandbox.Rigidbody",
            "--properties", '{"Gravity": false, "MassOverride": 50}',
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert "Gravity" in data["updated_keys"]
        assert "MassOverride" in data["updated_keys"]
    def test_asset_find_refs_json( self, tmp_path ):
        """asset find-refs locates referrers via subprocess."""
        # Build a small project
        self._run( ["--json", "project", "new", "--name", "rg", "--output-dir", str( tmp_path )] )

        scene_path = os.path.join( str( tmp_path ), "Assets", "scenes", "level.scene" )
        self._run( ["--json", "scene", "new", "--name", "level", "-o", scene_path, "--no-defaults"] )
        # Inject a custom model ref via add-component on a fresh object
        add_obj = self._run( ["--json", "scene", "add-object", scene_path, "Box"] )
        guid = json.loads( add_obj.stdout )["guid"]
        self._run( [
            "--json", "scene", "add-component", scene_path, guid, "Sandbox.ModelRenderer",
            "--properties", '{"Model": "models/team/widget.vmdl"}',
        ] )

        # Create the actual asset file so list_assets finds it
        os.makedirs( os.path.join( str( tmp_path ), "Assets", "models", "team" ), exist_ok=True )
        with open( os.path.join( str( tmp_path ), "Assets", "models", "team", "widget.vmdl" ), "w", encoding="utf-8" ) as f:
            f.write( "<model>" )

        result = self._run( [
            "--json", "--project", str( tmp_path ),
            "asset", "find-refs", "models/team/widget.vmdl",
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert len( data ) >= 1
        assert any( "level.scene" in row["file"] for row in data )
