# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestFileTransformBackend:
    def _make_context(self):
        from cli_anything.macrocli.backends.base import BackendContext

        return BackendContext(params={})

    def test_json_set_and_get(self, tmp_path):
        from cli_anything.macrocli.backends.file_transform import FileTransformBackend
        from cli_anything.macrocli.core.macro_model import MacroStep

        b = FileTransformBackend()
        ctx = self._make_context()

        json_file = tmp_path / "data.json"
        json_file.write_text('{"a": 1}', encoding="utf-8")

        step = MacroStep(
            id="set",
            backend="file_transform",
            action="json_set",
            params={
                "input_file": str(json_file),
                "output_file": str(json_file),
                "path": "settings.theme",
                "value": "dark",
            },
        )
        result = b.execute(step, {}, ctx)
        assert result.success

        import json

        data = json.loads(json_file.read_text())
        assert data["settings"]["theme"] == "dark"

    def test_text_replace(self, tmp_path):
        from cli_anything.macrocli.backends.file_transform import FileTransformBackend
        from cli_anything.macrocli.core.macro_model import MacroStep

        b = FileTransformBackend()
        ctx = self._make_context()

        txt_file = tmp_path / "config.ini"
        txt_file.write_text("theme=default\nsize=10\n", encoding="utf-8")

        step = MacroStep(
            id="replace",
            backend="file_transform",
            action="text_replace",
            params={
                "input_file": str(txt_file),
                "output_file": str(txt_file),
                "find": "theme=default",
                "replace": "theme=dark",
            },
        )
        result = b.execute(step, {}, ctx)
        assert result.success
        assert "theme=dark" in txt_file.read_text()
        assert result.output["replacements"] == 1

    def test_copy_file(self, tmp_path):
        from cli_anything.macrocli.backends.file_transform import FileTransformBackend
        from cli_anything.macrocli.core.macro_model import MacroStep

        b = FileTransformBackend()
        ctx = self._make_context()

        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("content", encoding="utf-8")

        step = MacroStep(
            id="copy",
            backend="file_transform",
            action="copy_file",
            params={
                "src": str(src),
                "dst": str(dst),
            },
        )
        result = b.execute(step, {}, ctx)
        assert result.success
        assert dst.read_text() == "content"

    def test_unknown_action(self):
        from cli_anything.macrocli.backends.file_transform import FileTransformBackend
        from cli_anything.macrocli.core.macro_model import MacroStep

        b = FileTransformBackend()
        step = MacroStep(
            id="x", backend="file_transform", action="unknown_op", params={}
        )
        result = b.execute(step, {}, self._make_context())
        assert not result.success


class TestStepResult:
    def test_to_dict(self):
        from cli_anything.macrocli.backends.base import StepResult

        r = StepResult(success=True, output={"key": "val"}, backend_used="native_api")
        d = r.to_dict()
        assert d["success"] is True
        assert d["output"]["key"] == "val"
        assert d["backend_used"] == "native_api"


class TestRoutingEngine:
    def test_select_native_api(self):
        from cli_anything.macrocli.core.routing import RoutingEngine
        from cli_anything.macrocli.core.macro_model import MacroStep

        engine = RoutingEngine()
        step = MacroStep(id="x", backend="native_api", action="run_command")
        backend = engine.select(step)
        assert backend.name == "native_api"

    def test_select_file_transform(self):
        from cli_anything.macrocli.core.routing import RoutingEngine
        from cli_anything.macrocli.core.macro_model import MacroStep

        engine = RoutingEngine()
        step = MacroStep(id="x", backend="file_transform", action="json_set")
        backend = engine.select(step)
        assert backend.name == "file_transform"

    def test_describe(self):
        from cli_anything.macrocli.core.routing import RoutingEngine

        engine = RoutingEngine()
        desc = engine.describe()
        assert "native_api" in desc
        assert "file_transform" in desc
        assert "recovery" in desc

    def test_execute_step_native_api(self):
        from cli_anything.macrocli.core.routing import RoutingEngine
        from cli_anything.macrocli.core.macro_model import MacroStep
        from cli_anything.macrocli.backends.base import BackendContext

        engine = RoutingEngine()
        step = MacroStep(
            id="x",
            backend="native_api",
            action="run_command",
            params={"command": ["echo", "hello"]},
        )
        ctx = BackendContext(params={})
        result = engine.execute_step(step, {}, ctx)
        assert result.success
