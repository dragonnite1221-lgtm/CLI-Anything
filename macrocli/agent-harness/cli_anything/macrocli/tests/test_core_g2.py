# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestNativeAPIBackend:
    def _make_context(self, params=None):
        from cli_anything.macrocli.backends.base import BackendContext

        return BackendContext(params=params or {})

    def _make_step(self, action, step_params):
        from cli_anything.macrocli.core.macro_model import MacroStep

        return MacroStep(
            id="test", backend="native_api", action=action, params=step_params
        )

    def test_run_command_success(self):
        from cli_anything.macrocli.backends.native_api import NativeAPIBackend

        b = NativeAPIBackend()
        step = self._make_step("run_command", {"command": ["echo", "hello"]})
        result = b.execute(step, {}, self._make_context())
        assert result.success

    def test_run_command_fails_bad_exit(self):
        from cli_anything.macrocli.backends.native_api import NativeAPIBackend

        b = NativeAPIBackend()
        step = self._make_step("run_command", {"command": ["false"]})
        result = b.execute(step, {}, self._make_context())
        assert not result.success
        assert "exit" in result.error.lower() or "failed" in result.error.lower()

    def test_run_command_not_found(self):
        from cli_anything.macrocli.backends.native_api import NativeAPIBackend

        b = NativeAPIBackend()
        step = self._make_step("run_command", {"command": ["__nonexistent_cmd__"]})
        result = b.execute(step, {}, self._make_context())
        assert not result.success

    def test_find_executable_found(self):
        from cli_anything.macrocli.backends.native_api import NativeAPIBackend

        b = NativeAPIBackend()
        step = self._make_step("find_executable", {"name": "echo"})
        result = b.execute(step, {}, self._make_context())
        assert result.success
        assert "executable" in result.output

    def test_find_executable_missing(self):
        from cli_anything.macrocli.backends.native_api import NativeAPIBackend

        b = NativeAPIBackend()
        step = self._make_step(
            "find_executable",
            {"name": "__nonexistent__", "install_hint": "brew install nonexistent"},
        )
        result = b.execute(step, {}, self._make_context())
        assert not result.success
        assert "brew install" in result.error

    def test_dry_run_does_not_execute(self):
        from cli_anything.macrocli.backends.native_api import NativeAPIBackend
        from cli_anything.macrocli.backends.base import BackendContext

        b = NativeAPIBackend()
        step = self._make_step("run_command", {"command": ["false"]})
        ctx = BackendContext(params={}, dry_run=True)
        result = b.execute(step, {}, ctx)
        assert result.success
        assert result.output.get("dry_run")

    def test_param_substitution_in_command(self):
        from cli_anything.macrocli.backends.native_api import NativeAPIBackend

        b = NativeAPIBackend()
        step = self._make_step("run_command", {"command": ["echo", "${msg}"]})
        result = b.execute(
            step, {"msg": "substituted"}, self._make_context({"msg": "substituted"})
        )
        assert result.success

    def test_unknown_action(self):
        from cli_anything.macrocli.backends.native_api import NativeAPIBackend

        b = NativeAPIBackend()
        step = self._make_step("unknown_action", {})
        result = b.execute(step, {}, self._make_context())
        assert not result.success
        assert "unknown action" in result.error.lower()
