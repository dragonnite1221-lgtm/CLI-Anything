# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestProjectCreate:
    def test_create_new_project(self, runner, tmp_path):
        project_dir = tmp_path / "new_game"
        result = runner.invoke(cli, ["--json", "project", "create", str(project_dir)])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["project_name"] == "new_game"
        assert (project_dir / "project.godot").exists()

    def test_create_with_custom_name(self, runner, tmp_path):
        project_dir = tmp_path / "my_dir"
        result = runner.invoke(
            cli,
            ["--json", "project", "create", str(project_dir), "--name", "Cool Game"],
        )
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["project_name"] == "Cool Game"

    def test_create_duplicate_fails(self, runner, tmp_project):
        result = runner.invoke(cli, ["--json", "project", "create", str(tmp_project)])
        data = json.loads(result.output)
        assert data["status"] == "error"


class TestProjectInfo:
    def test_info_valid_project(self, runner, tmp_project):
        result = runner.invoke(
            cli, ["--json", "-p", str(tmp_project), "project", "info"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["name"] == "TestGame"
        assert "4.4" in data["features"]

    def test_info_invalid_project(self, runner, tmp_path):
        result = runner.invoke(cli, ["--json", "-p", str(tmp_path), "project", "info"])
        data = json.loads(result.output)
        assert data["status"] == "error"


class TestProjectList:
    def test_list_scenes(self, runner, tmp_project):
        result = runner.invoke(
            cli, ["--json", "-p", str(tmp_project), "project", "scenes"]
        )
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["count"] == 2
        assert "scenes/Main.tscn" in data["scenes"]
        assert "scenes/Level1.tscn" in data["scenes"]

    def test_list_scripts(self, runner, tmp_project):
        result = runner.invoke(
            cli, ["--json", "-p", str(tmp_project), "project", "scripts"]
        )
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["count"] == 1
        assert "scripts/player.gd" in data["scripts"]

    def test_list_resources(self, runner, tmp_project):
        result = runner.invoke(
            cli, ["--json", "-p", str(tmp_project), "project", "resources"]
        )
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["count"] == 1


class TestSceneCreate:
    def test_create_scene(self, runner, tmp_project):
        result = runner.invoke(
            cli,
            [
                "--json",
                "-p",
                str(tmp_project),
                "scene",
                "create",
                "scenes/NewScene.tscn",
                "--root-type",
                "Node3D",
            ],
        )
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["root_type"] == "Node3D"
        assert (tmp_project / "scenes" / "NewScene.tscn").exists()

    def test_create_duplicate_scene_fails(self, runner, tmp_project):
        result = runner.invoke(
            cli,
            [
                "--json",
                "-p",
                str(tmp_project),
                "scene",
                "create",
                "scenes/Main.tscn",
            ],
        )
        data = json.loads(result.output)
        assert data["status"] == "error"


class TestSceneRead:
    def test_read_scene(self, runner, tmp_project):
        result = runner.invoke(
            cli,
            [
                "--json",
                "-p",
                str(tmp_project),
                "scene",
                "read",
                "scenes/Level1.tscn",
            ],
        )
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert len(data["nodes"]) == 2
        assert data["nodes"][0]["name"] == "Level1"
        assert data["nodes"][1]["name"] == "Player"

    def test_read_nonexistent_scene(self, runner, tmp_project):
        result = runner.invoke(
            cli,
            [
                "--json",
                "-p",
                str(tmp_project),
                "scene",
                "read",
                "scenes/Nope.tscn",
            ],
        )
        data = json.loads(result.output)
        assert data["status"] == "error"


class TestSceneAddNode:
    def test_add_node(self, runner, tmp_project):
        result = runner.invoke(
            cli,
            [
                "--json",
                "-p",
                str(tmp_project),
                "scene",
                "add-node",
                "scenes/Main.tscn",
                "--name",
                "Camera",
                "--type",
                "Camera2D",
            ],
        )
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["node_name"] == "Camera"

        # Verify the node was added to the file
        content = (tmp_project / "scenes" / "Main.tscn").read_text()
        assert 'name="Camera"' in content
        assert 'type="Camera2D"' in content
