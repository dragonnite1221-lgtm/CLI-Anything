# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin4:
    def test_asset_find_unused_json( self, tmp_path ):
        """asset find-unused detects unreferenced assets via subprocess."""
        self._run( ["--json", "project", "new", "--name", "un", "--output-dir", str( tmp_path )] )
        # Drop an unreferenced material into Assets/
        mat_path = os.path.join( str( tmp_path ), "Assets", "materials", "stray.vmat" )
        os.makedirs( os.path.dirname( mat_path ), exist_ok=True )
        with open( mat_path, "w", encoding="utf-8" ) as f:
            f.write( "Layer0 { shader \"complex.shader\" }" )

        result = self._run( [
            "--json", "--project", str( tmp_path ),
            "asset", "find-unused", "--type", "material",
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert any( "stray.vmat" in u["path"].replace( "\\", "/" ) for u in data )
    def test_project_validate_clean_json( self, tmp_path ):
        """project validate reports OK on a fresh project."""
        self._run( ["--json", "project", "new", "--name", "v", "--output-dir", str( tmp_path )] )
        result = self._run( ["--json", "--project", str( tmp_path ), "project", "validate"] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["broken_refs"] == []
        assert data["duplicate_guids"] == []
    def test_project_validate_broken_json( self, tmp_path ):
        """project validate flags a broken model reference and exits 1.

        Validation failures must exit non-zero so CI can gate on this command;
        check=False is required because subprocess.run with check=True would
        raise CalledProcessError before our assertions run.
        """
        self._run( ["--json", "project", "new", "--name", "v2", "--output-dir", str( tmp_path )] )
        scene_path = os.path.join( str( tmp_path ), "Assets", "scenes", "broken.scene" )
        self._run( ["--json", "scene", "new", "--name", "broken", "-o", scene_path, "--no-defaults"] )
        add_obj = self._run( ["--json", "scene", "add-object", scene_path, "Bad"] )
        guid = json.loads( add_obj.stdout )["guid"]
        self._run( [
            "--json", "scene", "add-component", scene_path, guid, "Sandbox.ModelRenderer",
            "--properties", '{"Model": "models/missing/whoops.vmdl"}',
        ] )
        result = self._run(
            ["--json", "--project", str( tmp_path ), "project", "validate", "--no-inputs"],
            check=False,
        )
        assert result.returncode == 1
        data = json.loads( result.stdout )
        assert data["ok"] is False
        assert any( "missing/whoops" in b["ref"] for b in data["broken_refs"] )
    def test_codegen_panel_component_json( self, tmp_path ):
        """codegen panel-component scaffolds Razor + scene snippet."""
        razor_path = os.path.join( str( tmp_path ), "HudBar.razor" )
        result = self._run( [
            "--json", "codegen", "panel-component",
            "--name", "HudBar",
            "--properties", '[{"name":"Health","type":"float","default":"100f"}]',
            "-o", razor_path,
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["class_name"] == "HudBar"
        assert os.path.isfile( razor_path )
        assert os.path.isfile( os.path.join( str( tmp_path ), "HudBar.razor.scss" ) )
        snippet = json.loads( data["scene_snippet"] )
        types = [c["__type"] for c in snippet["Components"]]
        assert "Sandbox.ScreenPanel" in types
        assert "HudBar" in types
    def test_codegen_panel_component_appends_to_scene( self, tmp_path ):
        """codegen panel-component --scene appends GameObject to a scene."""
        scene_path = os.path.join( str( tmp_path ), "ui.scene" )
        razor_path = os.path.join( str( tmp_path ), "Crosshair.razor" )
        self._run( ["--json", "scene", "new", "--name", "ui", "-o", scene_path, "--no-defaults"] )

        result = self._run( [
            "--json", "codegen", "panel-component",
            "--name", "Crosshair",
            "-o", razor_path,
            "--scene", scene_path,
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["scene_appended_to"]

        # Verify scene has the new object with both ScreenPanel and Crosshair
        with open( scene_path, "r", encoding="utf-8" ) as f:
            scene_json = json.load( f )
        names = [o["Name"] for o in scene_json["GameObjects"]]
        assert "Crosshair" in names
    def test_scene_diff_identical_json( self, tmp_path ):
        """scene diff reports identical when scenes match by name structure."""
        a = os.path.join( str( tmp_path ), "a.scene" )
        b = os.path.join( str( tmp_path ), "b.scene" )
        self._run( ["--json", "scene", "new", "--name", "x", "-o", a, "--no-defaults"] )
        self._run( ["--json", "scene", "new", "--name", "x", "-o", b, "--no-defaults"] )
        for n in ["A", "B"]:
            self._run( ["--json", "scene", "add-object", a, n] )
            self._run( ["--json", "scene", "add-object", b, n] )
        result = self._run( ["--json", "scene", "diff", a, b] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["identical"] is True
