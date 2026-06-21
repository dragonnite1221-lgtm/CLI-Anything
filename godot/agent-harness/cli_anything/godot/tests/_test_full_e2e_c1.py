# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _invoke_json  # noqa: F401,E501


class _TestE2EDemoGamePipelineMixin1:
    def test_06_write_and_validate_script(self):
        """Write a player movement script and validate its syntax."""
        _invoke_json(
            self.runner,
            ["project", "create", str(self.project_dir), "--name", "Demo Platformer"],
        )

        scripts_dir = self.project_dir / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        (scripts_dir / "player_movement.gd").write_text(textwrap.dedent("""\
            extends CharacterBody2D

            const SPEED = 300.0
            const JUMP_VELOCITY = -400.0

            func _physics_process(delta: float) -> void:
                if not is_on_floor():
                    velocity += get_gravity() * delta

                if Input.is_action_just_pressed("ui_accept") and is_on_floor():
                    velocity.y = JUMP_VELOCITY

                var direction := Input.get_axis("ui_left", "ui_right")
                if direction:
                    velocity.x = direction * SPEED
                else:
                    velocity.x = move_toward(velocity.x, 0, SPEED)

                move_and_slide()
        """), encoding="utf-8")

        data = self._pj(["script", "validate", "scripts/player_movement.gd"])
        assert data["status"] == "ok"
        # Godot's check-only should find no errors in valid GDScript
        assert data["valid"] is True, f"Validation errors: {data.get('errors')}"
    def test_07_validate_invalid_script(self):
        """Ensure the validator catches syntax errors."""
        _invoke_json(
            self.runner,
            ["project", "create", str(self.project_dir), "--name", "Demo Platformer"],
        )

        bad_script = self.project_dir / "bad.gd"
        bad_script.write_text(
            "extends Node2D\n\nfunc broken(\n  # missing closing paren and body\n",
            encoding="utf-8",
        )

        data = self._pj(["script", "validate", "bad.gd"])
        assert data["status"] == "ok"  # command itself succeeds
        assert data["valid"] is False
    def test_08_run_procedural_generation_script(self):
        """Run a script that programmatically generates data, simulating
        procedural level generation — the kind of thing an agent would do."""
        _invoke_json(
            self.runner,
            ["project", "create", str(self.project_dir), "--name", "Demo Platformer"],
        )

        gen_script = self.project_dir / "gen_level.gd"
        gen_script.write_text(textwrap.dedent("""\
            extends SceneTree

            func _init():
                var platforms := []
                for i in range(5):
                    platforms.append({
                        "x": i * 200,
                        "y": 500 - (i * 30),
                        "width": 150,
                    })
                print(JSON.stringify(platforms))
                quit()
        """), encoding="utf-8")

        data = self._pj(["script", "run", "gen_level.gd"])
        assert data["status"] == "ok"
        # The script should emit valid JSON describing platform positions
        stdout = data.get("stdout", "")
        platforms = json.loads(stdout.strip().splitlines()[-1])
        assert len(platforms) == 5
        assert platforms[0]["x"] == 0
        assert platforms[4]["x"] == 800
    def test_09_inline_script_computes_result(self):
        """Run inline code that performs a computation and verify output."""
        _invoke_json(
            self.runner,
            ["project", "create", str(self.project_dir), "--name", "Demo Platformer"],
        )

        data = self._pj([
            "script", "inline",
            'var total := 0\nfor i in range(1, 11):\n\ttotal += i\nprint(total)',
        ])
        assert data["status"] == "ok"
        assert "55" in data.get("stdout", "")
