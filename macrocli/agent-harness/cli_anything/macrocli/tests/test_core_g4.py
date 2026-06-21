# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestMacroRuntime:
    def _make_runtime(self, tmp_path):
        from cli_anything.macrocli.core.registry import MacroRegistry
        from cli_anything.macrocli.core.runtime import MacroRuntime

        # Register a real macro that just echoes
        yaml_content = textwrap.dedent("""\
            name: echo_macro
            parameters:
              msg:
                type: string
                required: false
                default: hello
            steps:
              - id: step1
                backend: native_api
                action: run_command
                params:
                  command: [echo, "${msg}"]
        """)
        write_macro(tmp_path, "echo_macro", yaml_content)
        reg = MacroRegistry(str(tmp_path))
        return MacroRuntime(registry=reg)

    def test_execute_success(self, tmp_path):
        rt = self._make_runtime(tmp_path)
        result = rt.execute("echo_macro", {"msg": "test"})
        assert result.success
        assert result.telemetry["steps_run"] == 1

    def test_execute_unknown_macro(self, tmp_path):
        rt = self._make_runtime(tmp_path)
        result = rt.execute("nonexistent_macro", {})
        assert not result.success
        assert "not found" in result.error.lower()

    def test_execute_param_validation_failure(self, tmp_path):
        from cli_anything.macrocli.core.registry import MacroRegistry
        from cli_anything.macrocli.core.runtime import MacroRuntime

        yaml_content = textwrap.dedent("""\
            name: required_param_macro
            parameters:
              output:
                type: string
                required: true
            steps:
              - id: s1
                backend: native_api
                action: run_command
                params:
                  command: [echo, "${output}"]
        """)
        write_macro(tmp_path, "required_param_macro", yaml_content)
        reg = MacroRegistry(str(tmp_path))
        rt = MacroRuntime(registry=reg)
        result = rt.execute("required_param_macro", {})
        assert not result.success
        assert "output" in result.error

    def test_precondition_failure(self, tmp_path):
        from cli_anything.macrocli.core.registry import MacroRegistry
        from cli_anything.macrocli.core.runtime import MacroRuntime

        yaml_content = textwrap.dedent("""\
            name: precond_macro
            preconditions:
              - file_exists: /nonexistent_file_xyz_abc
            steps:
              - id: s1
                backend: native_api
                action: run_command
                params:
                  command: [echo, ok]
        """)
        write_macro(tmp_path, "precond_macro", yaml_content)
        reg = MacroRegistry(str(tmp_path))
        rt = MacroRuntime(registry=reg)
        result = rt.execute("precond_macro", {})
        assert not result.success
        assert "precondition" in result.error.lower()

    def test_postcondition_failure(self, tmp_path):
        from cli_anything.macrocli.core.registry import MacroRegistry
        from cli_anything.macrocli.core.runtime import MacroRuntime

        yaml_content = textwrap.dedent("""\
            name: postcond_macro
            steps:
              - id: s1
                backend: native_api
                action: run_command
                params:
                  command: [echo, ok]
            postconditions:
              - file_exists: /nonexistent_output_xyz
        """)
        write_macro(tmp_path, "postcond_macro", yaml_content)
        reg = MacroRegistry(str(tmp_path))
        rt = MacroRuntime(registry=reg)
        result = rt.execute("postcond_macro", {})
        assert not result.success
        assert "postcondition" in result.error.lower()

    def test_dry_run(self, tmp_path):
        rt = self._make_runtime(tmp_path)
        result = rt.execute("echo_macro", {}, dry_run=True)
        assert result.success
        assert result.telemetry["dry_run"] is True

    def test_session_records_run(self, tmp_path):
        rt = self._make_runtime(tmp_path)
        rt.execute("echo_macro", {})
        last = rt.session.last()
        assert last is not None
        assert last.macro_name == "echo_macro"

    def test_validate_macro(self, tmp_path):
        rt = self._make_runtime(tmp_path)
        errors = rt.validate_macro("echo_macro")
        assert errors == []

    def test_on_failure_skip(self, tmp_path):
        from cli_anything.macrocli.core.registry import MacroRegistry
        from cli_anything.macrocli.core.runtime import MacroRuntime

        yaml_content = textwrap.dedent("""\
            name: skip_macro
            steps:
              - id: bad_step
                backend: native_api
                action: run_command
                params:
                  command: [false]
                on_failure: skip
              - id: good_step
                backend: native_api
                action: run_command
                params:
                  command: [echo, reached]
        """)
        write_macro(tmp_path, "skip_macro", yaml_content)
        reg = MacroRegistry(str(tmp_path))
        rt = MacroRuntime(registry=reg)
        result = rt.execute("skip_macro", {})
        # Should succeed because bad step was skipped
        assert result.success
        assert result.telemetry["steps_run"] == 2
