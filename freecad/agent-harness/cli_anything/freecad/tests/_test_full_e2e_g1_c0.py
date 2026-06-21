# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin0:
    """Test the CLI entry-point via subprocess invocations."""
    @pytest.fixture(autouse=True)
    def _cli_cmd(self):
        """Resolve the CLI command once for all tests."""
        self.cli = _resolve_cli("cli-anything-freecad")
    def _run(self, *args: str, timeout: int = 30, **kwargs) -> subprocess.CompletedProcess:
        """Run a CLI command and return the result."""
        cmd = self.cli + list(args)
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            **kwargs,
        )
    def test_help(self):
        """--help returns exit code 0 and prints usage."""
        result = self._run("--help")
        assert result.returncode == 0, (
            f"--help failed (rc={result.returncode}): {result.stderr}"
        )
        assert "freecad" in result.stdout.lower() or "usage" in result.stdout.lower(), (
            f"Unexpected help output: {result.stdout[:200]}"
        )
        print(f"\n  --help: rc={result.returncode}, {len(result.stdout)} chars")
    def test_document_new_json(self, tmp_path):
        """'--json document new -o <path>' creates valid JSON output."""
        out_file = str(tmp_path / "new_doc.json")
        result = self._run("--json", "document", "new",
                           "--name", "TestDoc", "-o", out_file)
        assert result.returncode == 0, (
            f"document new failed (rc={result.returncode}): {result.stderr}"
        )

        # stdout should be valid JSON
        data = json.loads(result.stdout)
        assert data["name"] == "TestDoc"
        assert "version" in data

        # File should exist
        assert os.path.isfile(out_file)
        print(f"\n  document new: {out_file} ({os.path.getsize(out_file):,} bytes)")
    def test_part_add_json(self, tmp_path):
        """Create doc then add a part, verify JSON output."""
        proj_file = str(tmp_path / "part_add.json")

        # Create document
        r1 = self._run("--json", "document", "new",
                        "--name", "PartTest", "-o", proj_file)
        assert r1.returncode == 0, f"doc new failed: {r1.stderr}"

        # Add a box part
        r2 = self._run("--json", "-p", proj_file, "part", "add", "box",
                        "--name", "MyBox", "-P", "length=30")
        assert r2.returncode == 0, f"part add failed: {r2.stderr}"

        data = json.loads(r2.stdout)
        assert data["type"] == "box"
        assert data["name"] == "MyBox"
        assert data["params"]["length"] == 30.0

        print(f"\n  part add: {data['name']} (type={data['type']})")
    def test_part_list_json(self, tmp_path):
        """Create doc, add parts, list them, verify count."""
        proj_file = str(tmp_path / "part_list.json")

        # Create document
        self._run("--json", "document", "new",
                   "--name", "ListTest", "-o", proj_file)

        # Add two parts
        self._run("--json", "-p", proj_file, "part", "add", "box", "--name", "A")
        self._run("--json", "-p", proj_file, "part", "add", "cylinder", "--name", "B")

        # List parts
        r = self._run("--json", "-p", proj_file, "part", "list")
        assert r.returncode == 0, f"part list failed: {r.stderr}"

        parts = json.loads(r.stdout)
        assert isinstance(parts, list)
        assert len(parts) == 2
        names = {p["name"] for p in parts}
        assert "A" in names
        assert "B" in names

        print(f"\n  part list: {len(parts)} parts ({names})")
