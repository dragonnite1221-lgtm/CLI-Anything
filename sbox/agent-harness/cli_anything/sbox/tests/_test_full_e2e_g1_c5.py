# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin5:
    def test_scene_diff_added_removed_modified_json( self, tmp_path ):
        """scene diff captures all three categories of change."""
        a = os.path.join( str( tmp_path ), "a.scene" )
        b = os.path.join( str( tmp_path ), "b.scene" )
        self._run( ["--json", "scene", "new", "--name", "x", "-o", a, "--no-defaults"] )
        self._run( ["--json", "scene", "new", "--name", "x", "-o", b, "--no-defaults"] )
        self._run( ["--json", "scene", "add-object", a, "OnlyA"] )
        self._run( ["--json", "scene", "add-object", a, "Shared", "--position", "0,0,0"] )
        self._run( ["--json", "scene", "add-object", b, "Shared", "--position", "1,2,3"] )
        self._run( ["--json", "scene", "add-object", b, "OnlyB"] )
        result = self._run( ["--json", "scene", "diff", a, b] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert "OnlyB" in data["added"]
        assert "OnlyA" in data["removed"]
        assert any( m["name"] == "Shared" for m in data["modified"] )
    def test_prefab_diff_json( self, tmp_path ):
        """prefab diff reports root component changes."""
        a = os.path.join( str( tmp_path ), "a.prefab" )
        b = os.path.join( str( tmp_path ), "b.prefab" )
        self._run( ["--json", "prefab", "new", "--name", "P", "-o", a, "--components", "model"] )
        self._run( ["--json", "prefab", "new", "--name", "P", "-o", b, "--components", "model,rigidbody"] )
        result = self._run( ["--json", "prefab", "diff", a, b] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["identical"] is False
        assert data["root_changes"] is not None
    def test_scene_instantiate_prefab_json( self, tmp_path ):
        """scene instantiate-prefab inserts a prefab as a GameObject."""
        scene_path = os.path.join( str( tmp_path ), "level.scene" )
        prefab_path = os.path.join( str( tmp_path ), "Bullet.prefab" )
        self._run( ["--json", "scene", "new", "--name", "level", "-o", scene_path, "--no-defaults"] )
        self._run( ["--json", "prefab", "new", "--name", "Bullet", "-o", prefab_path, "--components", "model"] )

        result = self._run( [
            "--json", "scene", "instantiate-prefab", scene_path, prefab_path,
            "--position", "10,20,30",
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["guid"]

        # Verify scene now has a GameObject named "Bullet" with PrefabSource
        with open( scene_path, "r", encoding="utf-8" ) as f:
            scene_data = json.load( f )
        names = [o["Name"] for o in scene_data["GameObjects"]]
        assert "Bullet" in names
        bullet = next( o for o in scene_data["GameObjects"] if o["Name"] == "Bullet" )
        assert "PrefabSource" in bullet
        assert bullet["Position"] == "10,20,30"
    def test_asset_rename_json( self, tmp_path ):
        """asset rename moves the file and rewrites refs in scene+prefab."""
        self._run( ["--json", "project", "new", "--name", "rn", "--output-dir", str( tmp_path )] )

        # Asset on disk
        widget_dir = os.path.join( str( tmp_path ), "Assets", "models", "team" )
        os.makedirs( widget_dir, exist_ok=True )
        widget = os.path.join( widget_dir, "widget.vmdl" )
        with open( widget, "w", encoding="utf-8" ) as f:
            f.write( "<MODEL>" )

        # Scene that references it
        scene_path = os.path.join( str( tmp_path ), "Assets", "scenes", "level.scene" )
        self._run( ["--json", "scene", "new", "--name", "level", "-o", scene_path, "--no-defaults"] )
        add_obj = self._run( ["--json", "scene", "add-object", scene_path, "Box"] )
        guid = json.loads( add_obj.stdout )["guid"]
        self._run( [
            "--json", "scene", "add-component", scene_path, guid, "Sandbox.ModelRenderer",
            "--properties", '{"Model": "models/team/widget.vmdl"}',
        ] )

        result = self._run( [
            "--json", "--project", str( tmp_path ),
            "asset", "rename", "models/team/widget.vmdl", "gizmo",
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["new_path"] == "models/team/gizmo.vmdl"
        assert data["file_renamed"] is True
        assert len( data["references_updated"] ) >= 1

        # File renamed on disk
        assert os.path.isfile( os.path.join( widget_dir, "gizmo.vmdl" ) )
        assert not os.path.isfile( widget )
    def test_asset_rename_dry_run_json( self, tmp_path ):
        """asset rename --dry-run reports counts but doesn't touch files."""
        self._run( ["--json", "project", "new", "--name", "dry", "--output-dir", str( tmp_path )] )
        widget = os.path.join( str( tmp_path ), "Assets", "models", "team", "widget.vmdl" )
        os.makedirs( os.path.dirname( widget ), exist_ok=True )
        with open( widget, "w", encoding="utf-8" ) as f:
            f.write( "<X>" )

        result = self._run( [
            "--json", "--project", str( tmp_path ),
            "asset", "rename", "models/team/widget.vmdl", "renamed.vmdl",
            "--dry-run",
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["dry_run"] is True
        assert data["file_renamed"] is False
        # File still exists at the original path
        assert os.path.isfile( widget )
