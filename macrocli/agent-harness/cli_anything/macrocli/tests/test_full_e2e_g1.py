# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestNativeAPIE2E:
    def test_run_real_command_and_capture(self, tmp_path):
        """Run a real shell command and capture its stdout."""
        from cli_anything.macrocli.core.macro_model import MacroDefinition
        from cli_anything.macrocli.core.registry import MacroRegistry
        from cli_anything.macrocli.core.runtime import MacroRuntime

        output_file = tmp_path / "result.txt"
        yaml_content = textwrap.dedent(f"""\
            name: capture_date
            parameters:
              output:
                type: string
                required: true
            steps:
              - id: run_date
                backend: native_api
                action: run_command
                params:
                  command: [date, "+%Y-%m-%d"]
                  capture_stdout: true
            postconditions: []
            outputs:
              - name: output_file
                path: ${{output}}
        """)
        write_macro(tmp_path, "capture_date", yaml_content)

        reg = MacroRegistry(str(tmp_path))
        rt = MacroRuntime(registry=reg)
        result = rt.execute("capture_date", {"output": str(output_file)})

        assert result.success, f"Failed: {result.error}"
        # Step output contains stdout
        steps_output = result.output.get("_steps", [])
        assert steps_output, "Expected _steps in output"
        stdout = steps_output[0].get("stdout", "")
        # Date format YYYY-MM-DD
        import re

        assert re.match(r"\d{4}-\d{2}-\d{2}", stdout.strip()), (
            f"Unexpected stdout: {stdout!r}"
        )
        print(f"\n  Captured date: {stdout.strip()}")

    def test_step_failure_aborts_macro(self, tmp_path):
        """A failing step with on_failure=fail should abort the macro."""
        from cli_anything.macrocli.core.registry import MacroRegistry
        from cli_anything.macrocli.core.runtime import MacroRuntime

        yaml_content = textwrap.dedent("""\
            name: fail_abort
            steps:
              - id: bad
                backend: native_api
                action: run_command
                params:
                  command: [false]
                on_failure: fail
              - id: good
                backend: native_api
                action: run_command
                params:
                  command: [echo, should_not_run]
        """)
        write_macro(tmp_path, "fail_abort", yaml_content)
        reg = MacroRegistry(str(tmp_path))
        rt = MacroRuntime(registry=reg)
        result = rt.execute("fail_abort", {})

        assert not result.success
        # Only the first step should have run
        assert result.telemetry["steps_run"] == 1
        print(f"\n  Correctly aborted after first step: {result.error}")

    def test_step_failure_skip_continues(self, tmp_path):
        """A failing step with on_failure=skip should allow the macro to continue."""
        from cli_anything.macrocli.core.registry import MacroRegistry
        from cli_anything.macrocli.core.runtime import MacroRuntime

        yaml_content = textwrap.dedent("""\
            name: fail_skip
            steps:
              - id: bad
                backend: native_api
                action: run_command
                params:
                  command: [false]
                on_failure: skip
              - id: good
                backend: native_api
                action: run_command
                params:
                  command: [echo, still_ran]
        """)
        write_macro(tmp_path, "fail_skip", yaml_content)
        reg = MacroRegistry(str(tmp_path))
        rt = MacroRuntime(registry=reg)
        result = rt.execute("fail_skip", {})

        assert result.success
        assert result.telemetry["steps_run"] == 2
        print(f"\n  Macro succeeded despite skipped step")
