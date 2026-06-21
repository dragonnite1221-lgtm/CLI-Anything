# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestE2EProjectWorkflowMixin5:
    def test_material_sound_workflow( self, tmp_path ):
        """Create project, add materials and sounds, verify files."""
        from cli_anything.sbox.core import project as proj
        from cli_anything.sbox.core import material as mat
        from cli_anything.sbox.core import sound as snd

        proj.create_project( "test_proj", output_dir=str( tmp_path ) )
        mat_dir = os.path.join( str( tmp_path ), "Assets", "materials" )
        os.makedirs( mat_dir, exist_ok=True )
        snd_dir = os.path.join( str( tmp_path ), "Assets", "sounds" )
        os.makedirs( snd_dir, exist_ok=True )

        m = mat.create_material( "floor", shader="complex", metalness=0.3, output_path=os.path.join( mat_dir, "floor.vmat" ) )
        assert os.path.isfile( m["path"] )

        s = snd.create_sound_event( "gunshot", sounds=["sounds/gun.vsnd"], volume="0.8", output_path=os.path.join( snd_dir, "gunshot.sound" ) )
        assert os.path.isfile( s["path"] )

        materials = mat.list_materials( str( tmp_path ) )
        assert len( materials ) >= 1

        print( f"\n  Material: {m['path']}" )
        print( f"  Sound: {s['path']}" )
    def test_scene_modify_workflow( self, tmp_path ):
        """Create project, add objects, modify them, verify changes."""
        from cli_anything.sbox.core import project as proj
        from cli_anything.sbox.core import scene as sc

        proj.create_project( "test_proj", output_dir=str( tmp_path ) )
        scene_path = os.path.join( str( tmp_path ), "Assets", "scenes", "minimal.scene" )

        guid = sc.add_object( scene_path, "Enemy", position="100,0,0", components=["model", "rigidbody"] )
        sc.modify_object( scene_path, guid=guid, new_name="Boss", position="200,0,50", tags="enemy,boss" )

        objects = sc.list_objects( scene_path )
        boss = [o for o in objects if o["guid"] == guid][0]
        assert boss["name"] == "Boss"
        assert boss["position"] == "200,0,50"

        print( f"\n  Scene: {scene_path}" )
        print( f"  Boss GUID: {guid}" )
