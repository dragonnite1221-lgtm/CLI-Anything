# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


def _invoke_json(runner, args):
    """Invoke CLI with --json flag and return parsed dict."""
    result = runner.invoke(cli, ["--json"] + args)
    assert result.exit_code == 0, f"CLI exited {result.exit_code}: {result.output}"
    return json.loads(result.output)


def _invoke_project_json(runner, project_path, args):
    """Invoke CLI with --json and -p flags and return parsed dict."""
    return _invoke_json(runner, ["-p", str(project_path)] + args)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def e2e_project(tmp_path, runner):
    """Create a real Godot project for E2E tests."""
    project_dir = tmp_path / "e2e_game"
    data = _invoke_json(runner, ["project", "create", str(project_dir), "--name", "E2E Game"])
    assert data["status"] == "ok"
    return project_dir


@skip_no_godot
class TestE2EEngineVersion:
    def test_version(self, runner):
        data = _invoke_json(runner, ["engine", "version"])
        assert "version" in data

    def test_status(self, runner):
        data = _invoke_json(runner, ["engine", "status"])
        assert data["available"] is True
        assert data["binary"] != "not found"


@skip_no_godot
class TestE2EProject:
    def test_create_and_info(self, runner, tmp_path):
        project_dir = tmp_path / "test_game"
        data = _invoke_json(runner, ["project", "create", str(project_dir), "--name", "Test Game"])
        assert data["status"] == "ok"

        data = _invoke_project_json(runner, project_dir, ["project", "info"])
        assert data["name"] == "Test Game"

    def test_reimport(self, runner, e2e_project):
        data = _invoke_project_json(runner, e2e_project, ["project", "reimport"])
        assert "status" in data


@skip_no_godot
class TestE2EScene:
    def test_create_and_read(self, runner, e2e_project):
        data = _invoke_project_json(
            runner, e2e_project,
            ["scene", "create", "scenes/TestScene.tscn", "--root-type", "Node2D"],
        )
        assert data["status"] == "ok"

        data = _invoke_project_json(
            runner, e2e_project,
            ["scene", "read", "scenes/TestScene.tscn"],
        )
        assert data["status"] == "ok"
        assert len(data["nodes"]) >= 1

    def test_add_node_and_verify(self, runner, e2e_project):
        _invoke_project_json(
            runner, e2e_project,
            ["scene", "create", "scenes/NodeTest.tscn"],
        )
        data = _invoke_project_json(
            runner, e2e_project,
            ["scene", "add-node", "scenes/NodeTest.tscn",
             "--name", "Sprite", "--type", "Sprite2D"],
        )
        assert data["status"] == "ok"

        data = _invoke_project_json(
            runner, e2e_project,
            ["scene", "read", "scenes/NodeTest.tscn"],
        )
        node_names = [n.get("name") for n in data["nodes"]]
        assert "Sprite" in node_names


@skip_no_godot
class TestE2EScript:
    def test_run_script(self, runner, e2e_project):
        script_path = e2e_project / "tool_test.gd"
        script_path.write_text(
            "extends SceneTree\n\n"
            "func _init():\n"
            '\tprint("Hello from E2E!")\n'
            "\tquit()\n",
            encoding="utf-8",
        )
        data = _invoke_project_json(
            runner, e2e_project, ["script", "run", "tool_test.gd"],
        )
        assert "status" in data
        if data["status"] == "ok":
            assert "Hello from E2E!" in data.get("stdout", "")

    def test_inline_script(self, runner, e2e_project):
        data = _invoke_project_json(
            runner, e2e_project,
            ["script", "inline", 'print("inline test")'],
        )
        assert "status" in data
