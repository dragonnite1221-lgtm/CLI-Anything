# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin6:
    def test_asset_move_json( self, tmp_path ):
        """asset move relocates file across directories and rewrites refs."""
        self._run( ["--json", "project", "new", "--name", "mv", "--output-dir", str( tmp_path )] )
        widget = os.path.join( str( tmp_path ), "Assets", "models", "team", "widget.vmdl" )
        os.makedirs( os.path.dirname( widget ), exist_ok=True )
        with open( widget, "w", encoding="utf-8" ) as f:
            f.write( "<X>" )

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
            "asset", "move", "models/team/widget.vmdl", "models/shared/widget.vmdl",
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["file_moved"] is True
        assert data["new_path"] == "models/shared/widget.vmdl"

        moved = os.path.join( str( tmp_path ), "Assets", "models", "shared", "widget.vmdl" )
        assert os.path.isfile( moved )
        assert not os.path.isfile( widget )
