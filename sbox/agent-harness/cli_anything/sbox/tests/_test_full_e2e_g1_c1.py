# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin1:
    def test_full_workflow_subprocess(self, tmp_path):
        """Full workflow: create project -> add scene objects -> generate code -> verify."""
        # Create project
        self._run([
            "--json", "project", "new",
            "--name", "workflow_test",
            "--output-dir", str(tmp_path),
        ])

        scene_path = os.path.join(str(tmp_path), "Assets", "scenes", "minimal.scene")

        # Add objects
        self._run([
            "--json", "scene", "add-object",
            scene_path, "Player",
            "--components", "model,box_collider",
        ])
        self._run([
            "--json", "scene", "add-object",
            scene_path, "Enemy",
            "--position", "200,0,0",
            "--components", "model,rigidbody",
        ])

        # Verify objects exist
        result = self._run(["--json", "scene", "list", scene_path])
        objects = json.loads(result.stdout)
        names = [o["name"] for o in objects]
        assert "Player" in names
        assert "Enemy" in names

        # Generate component
        comp_path = os.path.join(str(tmp_path), "Code", "PlayerController.cs")
        self._run([
            "--json", "codegen", "component",
            "--name", "PlayerController",
            "--methods", "OnUpdate,OnFixedUpdate",
            "--properties", json.dumps([
                {"name": "Speed", "type": "float", "default": "200f"},
            ]),
            "--output", comp_path,
        ])
        assert os.path.exists(comp_path)

        # Print artifacts
        print(f"\n  Project:   {tmp_path}")
        print(f"  Scene:     {scene_path}")
        print(f"  Component: {comp_path}")
        for obj in objects:
            print(f"  Object:    {obj['name']} ({obj['guid']})")
    def test_material_new_json( self, tmp_path ):
        """Create material via subprocess."""
        mat_path = os.path.join( str( tmp_path ), "test.vmat" )
        result = self._run( ["--json", "material", "new", "--name", "test", "-o", mat_path] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["name"] == "test"
        assert os.path.isfile( mat_path )
    def test_codegen_razor_json( self, tmp_path ):
        """Generate Razor component via subprocess."""
        razor_path = os.path.join( str( tmp_path ), "TestPanel.razor" )
        result = self._run( [
            "--json", "codegen", "razor",
            "--name", "TestPanel",
            "--properties", '[{"name":"Score","type":"int","default":"0"}]',
            "-o", razor_path,
        ] )
        assert result.returncode == 0
        data = json.loads( result.stdout )
        assert data["class_name"] == "TestPanel"
        assert os.path.isfile( razor_path )
        with open( razor_path, "r", encoding="utf-8" ) as f:
            content = f.read()
        assert "@inherits PanelComponent" in content
    def test_scene_modify_object_json( self, tmp_path ):
        """Modify scene object via subprocess."""
        self._run( ["--json", "project", "new", "--name", "test_proj", "--output-dir", str( tmp_path )] )
        scene_path = os.path.join( str( tmp_path ), "Assets", "scenes", "minimal.scene" )

        add_result = self._run( ["--json", "scene", "add-object", scene_path, "TestObj", "--position", "0,0,0"] )
        guid = json.loads( add_result.stdout )["guid"]

        modify_result = self._run( [
            "--json", "scene", "modify-object", scene_path,
            "--guid", guid,
            "--name", "RenamedObj",
            "--position", "100,200,300",
        ] )
        assert modify_result.returncode == 0
        data = json.loads( modify_result.stdout )
        assert data["name"] == "RenamedObj"
        assert "Position" in data["modified_fields"]
    def test_scene_clone_object_json( self, tmp_path ):
        """Clone scene object via subprocess."""
        self._run( ["--json", "project", "new", "--name", "test_proj", "--output-dir", str( tmp_path )] )
        scene_path = os.path.join( str( tmp_path ), "Assets", "scenes", "minimal.scene" )

        add_result = self._run( ["--json", "scene", "add-object", scene_path, "Source", "--components", "model,rigidbody"] )
        guid = json.loads( add_result.stdout )["guid"]

        clone_result = self._run( [
            "--json", "scene", "clone-object", scene_path,
            "--guid", guid,
            "--new-name", "ClonedObj",
            "--position", "500,0,0",
        ] )
        assert clone_result.returncode == 0
        data = json.loads( clone_result.stdout )
        assert data["name"] == "ClonedObj"
        assert data["original_name"] == "Source"
