# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCLISubprocess:
    def test_help(self, tmp_path: Path):
        command = _resolve_cli("cli-anything-qgis")
        env = os.environ.copy()
        env["HOME"] = str(tmp_path / "home")
        env.setdefault("QT_QPA_PLATFORM", "offscreen")

        completed = subprocess.run(
            [*command, "--help"], capture_output=True, text=True, check=False, env=env
        )
        assert completed.returncode == 0
        assert "QGIS CLI" in completed.stdout

    def test_process_help_json(self, tmp_path: Path):
        command = _resolve_cli("cli-anything-qgis")
        env = os.environ.copy()
        env["HOME"] = str(tmp_path / "home")
        env.setdefault("QT_QPA_PLATFORM", "offscreen")

        payload = _subprocess_json(
            command, ["process", "help", "native:printlayouttopdf"], env
        )
        assert payload["algorithm"]["id"] == "native:printlayouttopdf"

    def test_project_new_json(self, tmp_path: Path):
        command = _resolve_cli("cli-anything-qgis")
        env = os.environ.copy()
        env["HOME"] = str(tmp_path / "home")
        env.setdefault("QT_QPA_PLATFORM", "offscreen")

        project_path = tmp_path / "subprocess.qgz"
        payload = _subprocess_json(
            command,
            ["project", "new", "-o", str(project_path), "--title", "Subprocess"],
            env,
        )
        assert payload["path"] == str(project_path.resolve())
        assert Path(payload["path"]).exists()

    def test_full_pdf_workflow(self, tmp_path: Path):
        command = _resolve_cli("cli-anything-qgis")
        env = os.environ.copy()
        env["HOME"] = str(tmp_path / "home")
        env.setdefault("QT_QPA_PLATFORM", "offscreen")

        build = _build_subprocess_project(command, tmp_path, "subprocess_pdf", env)
        pdf_path = tmp_path / "subprocess.pdf"
        exported = _subprocess_json(
            command,
            [
                "--project",
                build["project_path"],
                "export",
                "pdf",
                str(pdf_path),
                "--layout",
                "Main",
                "--overwrite",
            ],
            env,
        )

        output_path = Path(exported["output"])
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        assert output_path.read_bytes()[:5] == b"%PDF-"
        print(f"Subprocess PDF artifact: {output_path}")

    def test_full_png_workflow(self, tmp_path: Path):
        command = _resolve_cli("cli-anything-qgis")
        env = os.environ.copy()
        env["HOME"] = str(tmp_path / "home")
        env.setdefault("QT_QPA_PLATFORM", "offscreen")

        build = _build_subprocess_project(command, tmp_path, "subprocess_png", env)
        png_path = tmp_path / "subprocess.png"
        exported = _subprocess_json(
            command,
            [
                "--project",
                build["project_path"],
                "export",
                "image",
                str(png_path),
                "--layout",
                "Main",
                "--overwrite",
            ],
            env,
        )

        output_path = Path(exported["output"])
        assert output_path.exists()
        assert output_path.read_bytes()[:8] == PNG_SIGNATURE
        print(f"Subprocess PNG artifact: {output_path}")

    def test_point_only_project_add_map_without_extent(self, tmp_path: Path):
        command = _resolve_cli("cli-anything-qgis")
        env = os.environ.copy()
        env["HOME"] = str(tmp_path / "home")
        env.setdefault("QT_QPA_PLATFORM", "offscreen")

        build = _build_subprocess_point_project(
            command, tmp_path, "subprocess_point", env
        )
        add_map = _subprocess_json(
            command,
            [
                "--project",
                build["project_path"],
                "layout",
                "add-map",
                "--layout",
                "Main",
                "--x",
                "10",
                "--y",
                "20",
                "--width",
                "180",
                "--height",
                "120",
            ],
            env,
        )
        assert any(item["type"] == "QgsLayoutItemMap" for item in add_map["items"])

        pdf_path = tmp_path / "subprocess_point.pdf"
        exported = _subprocess_json(
            command,
            [
                "--project",
                build["project_path"],
                "export",
                "pdf",
                str(pdf_path),
                "--layout",
                "Main",
                "--overwrite",
            ],
            env,
        )

        output_path = Path(exported["output"])
        assert output_path.exists()
        assert output_path.read_bytes()[:5] == b"%PDF-"
        print(f"Subprocess point-only PDF artifact: {output_path}")
