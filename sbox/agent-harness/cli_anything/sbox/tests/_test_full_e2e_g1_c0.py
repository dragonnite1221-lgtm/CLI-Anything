# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin0:
    """Test the installed cli-anything-sbox command via subprocess."""
    @classmethod
    def setup_class(cls):
        try:
            cls.CLI_BASE = _resolve_cli("cli-anything-sbox")
        except RuntimeError as e:
            pytest.skip(str(e), allow_module_level=False)
    def _run(self, args, check=True):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            timeout=30,
            stdin=subprocess.DEVNULL,
        )
    def test_help(self):
        """CLI --help works."""
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "cli-anything-sbox" in result.stdout or "sbox" in result.stdout.lower()
    def test_project_new_json(self, tmp_path):
        """Create project via subprocess with --json."""
        result = self._run([
            "--json", "project", "new",
            "--name", "test_proj",
            "--output-dir", str(tmp_path),
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "test_proj"
        assert os.path.exists(data["sbproj"])
    def test_scene_info_json(self, tmp_path):
        """Get scene info via subprocess."""
        # First create a project
        self._run([
            "--json", "project", "new",
            "--name", "test_proj",
            "--output-dir", str(tmp_path),
        ])
        scene_path = os.path.join(str(tmp_path), "Assets", "scenes", "minimal.scene")
        result = self._run(["--json", "scene", "info", scene_path])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "object_count" in data
        assert data["object_count"] > 0
    def test_scene_add_object_json(self, tmp_path):
        """Add object to scene via subprocess."""
        self._run([
            "--json", "project", "new",
            "--name", "test_proj",
            "--output-dir", str(tmp_path),
        ])
        scene_path = os.path.join(str(tmp_path), "Assets", "scenes", "minimal.scene")
        result = self._run([
            "--json", "scene", "add-object",
            scene_path, "TestCube",
            "--position", "100,200,0",
            "--components", "model,box_collider,rigidbody",
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "guid" in data
    def test_codegen_component_json(self, tmp_path):
        """Generate component via subprocess."""
        output_file = os.path.join(str(tmp_path), "TestComp.cs")
        result = self._run([
            "--json", "codegen", "component",
            "--name", "TestComp",
            "--methods", "OnUpdate,OnStart",
            "--output", output_file,
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["class_name"] == "TestComp"
        assert os.path.exists(output_file)
        # Verify actual file content
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert "public sealed class TestComp : Component" in content
        assert "OnUpdate" in content
    def test_input_list_json(self, tmp_path):
        """List input actions via subprocess."""
        self._run([
            "--json", "project", "new",
            "--name", "test_proj",
            "--output-dir", str(tmp_path),
        ])
        result = self._run([
            "--json", "--project", str(tmp_path),
            "input", "list",
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) > 0
    def test_collision_list_json(self, tmp_path):
        """List collision layers via subprocess."""
        self._run([
            "--json", "project", "new",
            "--name", "test_proj",
            "--output-dir", str(tmp_path),
        ])
        result = self._run([
            "--json", "--project", str(tmp_path),
            "collision", "list",
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "defaults" in data or "layers" in data or isinstance(data, dict)
