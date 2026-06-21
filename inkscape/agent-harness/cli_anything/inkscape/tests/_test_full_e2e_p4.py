# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import tmp_dir  # noqa: F401,E501


def _resolve_cli(name):
    """Resolve installed CLI command; falls back to python -m for dev.

    Set env CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed command.
    """
    import shutil
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = name.replace("cli-anything-", "cli_anything.") + "." + name.split("-")[-1] + "_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything-inkscape")

    def _run(self, args, check=True):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True, text=True,
            check=check,
        )

    def test_help(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "Inkscape CLI" in result.stdout

    def test_document_new(self, tmp_dir):
        out = os.path.join(tmp_dir, "test.json")
        result = self._run(["document", "new", "-o", out])
        assert result.returncode == 0
        assert os.path.exists(out)

    def test_document_new_json_output(self, tmp_dir):
        out = os.path.join(tmp_dir, "test.json")
        result = self._run(["--json", "document", "new", "-o", out])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["document"]["width"] == 1920

    def test_document_profiles(self):
        result = self._run(["document", "profiles"])
        assert result.returncode == 0
        assert "a4_portrait" in result.stdout

    def test_shape_types(self):
        result = self._run(["shape", "--help"])
        assert result.returncode == 0
        assert "add-rect" in result.stdout

    def test_style_list_properties(self):
        result = self._run(["style", "list-properties"])
        assert result.returncode == 0
        assert "fill" in result.stdout

    def test_export_presets(self):
        result = self._run(["export", "presets"])
        assert result.returncode == 0
        assert "png_web" in result.stdout

    def test_path_list_operations(self):
        result = self._run(["path", "list-operations"])
        assert result.returncode == 0
        assert "union" in result.stdout

    def test_full_workflow_json(self, tmp_dir):
        proj_path = os.path.join(tmp_dir, "workflow.json")

        # Create document
        self._run(["--json", "document", "new", "-o", proj_path, "-n", "workflow"])
        assert os.path.exists(proj_path)

        # Load and verify
        result = self._run(["--json", "--project", proj_path, "document", "info"])
        assert result.returncode == 0
        info = json.loads(result.stdout)
        assert info["name"] == "workflow"

    def test_cli_error_handling(self):
        result = self._run(["document", "open", "/nonexistent/file.json"], check=False)
        assert result.returncode != 0

    def test_gradient_commands(self):
        result = self._run(["gradient", "--help"])
        assert result.returncode == 0
        assert "add-linear" in result.stdout

    def test_transform_commands(self):
        result = self._run(["transform", "--help"])
        assert result.returncode == 0
        assert "translate" in result.stdout

    def test_layer_commands(self):
        result = self._run(["layer", "--help"])
        assert result.returncode == 0
        assert "add" in result.stdout
