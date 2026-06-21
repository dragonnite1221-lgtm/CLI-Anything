# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLISubprocessMixin2:
    def test_full_workflow_subprocess(self, tmp_path):
        """Full subprocess workflow: create -> box -> cylinder -> boolean cut -> list."""
        proj_file = str(tmp_path / "workflow.json")

        # 1. Create document
        r = self._run("--json", "document", "new",
                       "--name", "WorkflowTest", "-o", proj_file)
        assert r.returncode == 0, f"doc new: {r.stderr}"

        # 2. Add box
        r = self._run("--json", "-p", proj_file, "part", "add", "box",
                       "--name", "Base", "-P", "length=20", "-P", "width=20",
                       "-P", "height=20")
        assert r.returncode == 0, f"add box: {r.stderr}"
        box = json.loads(r.stdout)
        assert box["name"] == "Base"

        # 3. Add cylinder
        r = self._run("--json", "-p", proj_file, "part", "add", "cylinder",
                       "--name", "Hole", "-P", "radius=5", "-P", "height=30",
                       "-pos", "10,10,-5")
        assert r.returncode == 0, f"add cylinder: {r.stderr}"
        cyl = json.loads(r.stdout)
        assert cyl["name"] == "Hole"

        # 4. Boolean cut
        r = self._run("--json", "-p", proj_file,
                       "part", "boolean", "cut", "0", "1")
        assert r.returncode == 0, f"boolean cut: {r.stderr}"
        cut = json.loads(r.stdout)
        assert cut["type"] == "cut"

        # 5. List parts -- should have 3 (box, cylinder, cut-result)
        r = self._run("--json", "-p", proj_file, "part", "list")
        assert r.returncode == 0, f"part list: {r.stderr}"
        parts = json.loads(r.stdout)
        assert len(parts) == 3, f"Expected 3 parts, got {len(parts)}: {parts}"

        # Verify visibility: first two hidden, cut result visible
        visible_count = sum(1 for p in parts if p.get("visible", True))
        assert visible_count >= 1, "At least the cut result should be visible"

        type_names = [p["type"] for p in parts]
        assert "cut" in type_names, f"No 'cut' part found in types: {type_names}"

        print(f"\n  Workflow complete: {len(parts)} parts")
        for p in parts:
            print(f"    {p['name']}: type={p['type']}, visible={p.get('visible', '?')}")
    @pytest.mark.skipif(not _has_freecad_preview(), reason="GUI-capable FreeCAD not installed")
    def test_preview_capture_subprocess(self, tmp_path):
        proj_file = str(tmp_path / "preview_cli.json")

        proj = create_document(name="PreviewCLI")
        add_part(proj, "box", name="Body", params={"length": 24, "width": 18, "height": 10})
        save_document(proj, proj_file)

        result = self._run(
            "--json",
            "-p",
            proj_file,
            "preview",
            "capture",
            "--root-dir",
            str(tmp_path),
            timeout=240,
        )
        assert result.returncode == 0, result.stderr

        manifest = json.loads(result.stdout)
        assert manifest["software"] == "freecad"
        hero_path = _artifact_path(manifest, "hero")
        _assert_png(hero_path)

        latest = self._run(
            "--json",
            "preview",
            "latest",
            "--recipe",
            "quick",
            "--root-dir",
            str(tmp_path),
            timeout=60,
        )
        assert latest.returncode == 0, latest.stderr
        latest_manifest = json.loads(latest.stdout)
        assert latest_manifest["bundle_id"] == manifest["bundle_id"]

        print(f"\n  FreeCAD preview bundle: {manifest['_bundle_dir']}")
        print(f"  FreeCAD preview hero: {hero_path}")
