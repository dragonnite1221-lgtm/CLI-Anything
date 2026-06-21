# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestRealCLIWorkflows:
    def test_scratch_project_to_pdf(self, runner: CliRunner, tmp_path: Path):
        build = _build_cli_project(runner, tmp_path, "pdf_workflow")
        pdf_path = tmp_path / "workflow.pdf"

        exported = _invoke_json(
            runner,
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
        )

        output_path = Path(exported["output"])
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        assert output_path.read_bytes()[:5] == b"%PDF-"
        print(f"PDF artifact: {output_path}")

    def test_scratch_project_to_png(self, runner: CliRunner, tmp_path: Path):
        from qgis.PyQt.QtGui import QImage

        build = _build_cli_project(runner, tmp_path, "png_workflow")
        png_path = tmp_path / "workflow.png"

        exported = _invoke_json(
            runner,
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
        )

        output_path = Path(exported["output"])
        assert output_path.exists()
        assert output_path.read_bytes()[:8] == PNG_SIGNATURE

        image = QImage(str(output_path))
        assert not image.isNull()
        assert image.width() > 0
        assert image.height() > 0
        print(f"PNG artifact: {output_path}")

    def test_processing_passthrough_buffer(self, runner: CliRunner, tmp_path: Path):
        from qgis.core import QgsVectorLayer

        build = _build_cli_project(runner, tmp_path, "buffer_workflow")
        output_path = tmp_path / "buffer.geojson"

        data = _invoke_json(
            runner,
            [
                "--project",
                build["project_path"],
                "process",
                "run",
                "native:buffer",
                "--param",
                f"INPUT={build['layer_source']}",
                "--param",
                "DISTANCE=1",
                "--param",
                "SEGMENTS=8",
                "--param",
                "END_CAP_STYLE=0",
                "--param",
                "JOIN_STYLE=0",
                "--param",
                "MITER_LIMIT=2",
                "--param",
                "DISSOLVE=false",
                "--param",
                f"OUTPUT={output_path}",
            ],
        )

        result_path = Path(data["results"]["OUTPUT"])
        assert result_path.exists()

        backend.ensure_qgis_app()
        layer = QgsVectorLayer(str(result_path), "buffer", "ogr")
        assert layer.isValid()
        assert int(layer.featureCount()) > 0
