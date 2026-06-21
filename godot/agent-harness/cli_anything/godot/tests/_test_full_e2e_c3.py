# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _invoke_json  # noqa: F401,E501


class _TestE2EDemoGamePipelineMixin3:
    def test_14_complete_game_assembly(self):
        """Walk through the entire game-creation pipeline in one test:
        create project → build scenes → add nodes → write scripts →
        validate → list assets → configure export → verify presets.

        This is the true end-to-end rendering-pipeline test: every CLI
        command that an agent would invoke to assemble a playable demo.
        """
        proj = self.project_dir

        # 1. Create project
        data = _invoke_json(
            self.runner,
            ["project", "create", str(proj), "--name", "Full Pipeline Game"],
        )
        assert data["status"] == "ok"

        # 2. Create main scene
        data = self._pj([
            "scene", "create", "scenes/Main.tscn",
            "--root-type", "Node2D", "--root-name", "Main",
        ])
        assert data["status"] == "ok"

        # 3. Create player scene with full hierarchy
        self._pj([
            "scene", "create", "scenes/Player.tscn",
            "--root-type", "CharacterBody2D", "--root-name", "Player",
        ])
        for name, ntype in [
            ("Sprite", "Sprite2D"),
            ("Collision", "CollisionShape2D"),
            ("Anim", "AnimationPlayer"),
        ]:
            data = self._pj([
                "scene", "add-node", "scenes/Player.tscn",
                "--name", name, "--type", ntype,
            ])
            assert data["status"] == "ok"

        # 4. Create level scene with nested hierarchy
        self._pj([
            "scene", "create", "scenes/Level1.tscn",
            "--root-type", "Node2D", "--root-name", "Level1",
        ])
        self._pj([
            "scene", "add-node", "scenes/Level1.tscn",
            "--name", "Platforms", "--type", "Node2D",
        ])
        self._pj([
            "scene", "add-node", "scenes/Level1.tscn",
            "--name", "Ground", "--type", "StaticBody2D",
            "--parent", "Platforms",
        ])

        # 5. Verify player scene structure
        data = self._pj(["scene", "read", "scenes/Player.tscn"])
        node_names = {n["name"] for n in data["nodes"] if "name" in n}
        assert {"Player", "Sprite", "Collision", "Anim"} <= node_names

        # 6. Write and validate game scripts
        scripts_dir = proj / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        (scripts_dir / "player.gd").write_text(textwrap.dedent("""\
            extends CharacterBody2D

            const SPEED = 300.0
            const JUMP_VELOCITY = -400.0

            func _physics_process(delta: float) -> void:
                if not is_on_floor():
                    velocity += get_gravity() * delta
                if Input.is_action_just_pressed("ui_accept") and is_on_floor():
                    velocity.y = JUMP_VELOCITY
                var direction := Input.get_axis("ui_left", "ui_right")
                velocity.x = direction * SPEED if direction else move_toward(velocity.x, 0, SPEED)
                move_and_slide()
        """), encoding="utf-8")

        (scripts_dir / "main.gd").write_text(textwrap.dedent("""\
            extends Node2D

            func _ready() -> void:
                print("Game started")
        """), encoding="utf-8")

        for script_name in ["scripts/player.gd", "scripts/main.gd"]:
            data = self._pj(["script", "validate", script_name])
            assert data["status"] == "ok"
            assert data["valid"] is True, (
                f"{script_name} failed validation: {data.get('errors')}"
            )

        # 7. Run a tool-script that verifies the project is well-formed
        checker = proj / "check_project.gd"
        checker.write_text(textwrap.dedent("""\
            extends SceneTree

            func _init():
                var dir := DirAccess.open("res://scenes")
                var scenes := []
                if dir:
                    dir.list_dir_begin()
                    var file_name := dir.get_next()
                    while file_name != "":
                        if file_name.ends_with(".tscn"):
                            scenes.append(file_name)
                        file_name = dir.get_next()
                print(JSON.stringify({"scene_count": scenes.size(), "scenes": scenes}))
                quit()
        """), encoding="utf-8")

        data = self._pj(["script", "run", "check_project.gd"])
        assert data["status"] == "ok"
        stdout = data.get("stdout", "")
        report = json.loads(stdout.strip().splitlines()[-1])
        assert report["scene_count"] == 3  # Main, Player, Level1

        # 8. Verify asset inventory
        data = self._pj(["project", "scenes"])
        assert len(data["scenes"]) >= 3

        data = self._pj(["project", "scripts"])
        assert data["count"] >= 2

        # 9. Configure export and verify presets
        (proj / "export_presets.cfg").write_text(textwrap.dedent("""\
            [preset.0]
            name="Windows Desktop"
            platform="Windows Desktop"
            export_path="build/game.exe"

            [preset.0.options]

            [preset.1]
            name="Linux/X11"
            platform="Linux/X11"
            export_path="build/game.x86_64"

            [preset.1.options]
        """), encoding="utf-8")

        data = self._pj(["export", "presets"])
        assert data["count"] == 2

        # 10. Attempt export build (will fail without export templates,
        #     but we verify the CLI invokes Godot correctly)
        result = self.runner.invoke(cli, [
            "--json", "-p", str(proj), "export", "build",
        ])
        data = json.loads(result.output)
        assert data["preset"] == "all"
        assert "returncode" in data
