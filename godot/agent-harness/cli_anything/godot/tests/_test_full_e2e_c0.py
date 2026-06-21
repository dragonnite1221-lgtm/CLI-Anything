# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _invoke_json, _invoke_project_json, runner  # noqa: F401,E501


class _TestE2EDemoGamePipelineMixin0:
    """Build a mini platformer project from scratch and verify each stage."""
    @pytest.fixture(autouse=True)
    def _setup(self, runner, tmp_path):
        self.runner = runner
        self.project_dir = tmp_path / "demo_platformer"
    def _pj(self, args):
        return _invoke_project_json(self.runner, self.project_dir, args)
    def test_01_create_project(self):
        data = _invoke_json(
            self.runner,
            ["project", "create", str(self.project_dir), "--name", "Demo Platformer"],
        )
        assert data["status"] == "ok"
        assert (self.project_dir / "project.godot").exists()
    def test_02_project_info(self):
        _invoke_json(
            self.runner,
            ["project", "create", str(self.project_dir), "--name", "Demo Platformer"],
        )
        data = self._pj(["project", "info"])
        assert data["name"] == "Demo Platformer"
    def test_03_create_multiple_scenes(self):
        _invoke_json(
            self.runner,
            ["project", "create", str(self.project_dir), "--name", "Demo Platformer"],
        )

        scenes = [
            ("scenes/Main.tscn", "Node2D", "Main"),
            ("scenes/Player.tscn", "CharacterBody2D", "Player"),
            ("scenes/Level1.tscn", "Node2D", "Level1"),
            ("scenes/UI.tscn", "Control", "UI"),
        ]
        for path, root_type, root_name in scenes:
            data = self._pj([
                "scene", "create", path,
                "--root-type", root_type,
                "--root-name", root_name,
            ])
            assert data["status"] == "ok", f"Failed to create {path}"
            assert data["root_type"] == root_type
    def test_04_build_node_hierarchy(self):
        """Assemble a player scene with multiple child nodes."""
        _invoke_json(
            self.runner,
            ["project", "create", str(self.project_dir), "--name", "Demo Platformer"],
        )
        self._pj([
            "scene", "create", "scenes/Player.tscn",
            "--root-type", "CharacterBody2D",
            "--root-name", "Player",
        ])

        children = [
            ("Sprite", "Sprite2D"),
            ("CollisionShape", "CollisionShape2D"),
            ("AnimPlayer", "AnimationPlayer"),
            ("Camera", "Camera2D"),
        ]
        for name, node_type in children:
            data = self._pj([
                "scene", "add-node", "scenes/Player.tscn",
                "--name", name, "--type", node_type,
            ])
            assert data["status"] == "ok"

        data = self._pj(["scene", "read", "scenes/Player.tscn"])
        node_names = {n.get("name") for n in data["nodes"]}
        assert {"Player", "Sprite", "CollisionShape", "AnimPlayer", "Camera"} <= node_names
    def test_05_nested_node_hierarchy(self):
        """Add nodes under non-root parents to verify parent path handling."""
        _invoke_json(
            self.runner,
            ["project", "create", str(self.project_dir), "--name", "Demo Platformer"],
        )
        self._pj([
            "scene", "create", "scenes/Level1.tscn",
            "--root-type", "Node2D",
            "--root-name", "Level1",
        ])
        self._pj([
            "scene", "add-node", "scenes/Level1.tscn",
            "--name", "Platforms", "--type", "Node2D",
        ])
        self._pj([
            "scene", "add-node", "scenes/Level1.tscn",
            "--name", "Platform1", "--type", "StaticBody2D",
            "--parent", "Platforms",
        ])
        self._pj([
            "scene", "add-node", "scenes/Level1.tscn",
            "--name", "CollisionShape", "--type", "CollisionShape2D",
            "--parent", "Platforms/Platform1",
        ])

        data = self._pj(["scene", "read", "scenes/Level1.tscn"])
        nodes_by_name = {n["name"]: n for n in data["nodes"] if "name" in n}
        assert "Platform1" in nodes_by_name
        assert nodes_by_name["Platform1"].get("parent") == "Platforms"
        assert nodes_by_name["CollisionShape"].get("parent") == "Platforms/Platform1"
