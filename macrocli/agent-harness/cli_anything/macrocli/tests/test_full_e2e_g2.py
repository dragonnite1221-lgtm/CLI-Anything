# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestPostconditionE2E:
    def test_postcondition_file_exists_passes(self, tmp_path):
        from cli_anything.macrocli.core.registry import MacroRegistry
        from cli_anything.macrocli.core.runtime import MacroRuntime

        output_file = tmp_path / "output.txt"
        yaml_content = textwrap.dedent(f"""\
            name: write_and_verify
            parameters:
              output:
                type: string
                required: true
            steps:
              - id: write
                backend: file_transform
                action: text_replace
                params:
                  input_file: /dev/null
                  output_file: ${{output}}
                  find: ""
                  replace: ""
            postconditions:
              - file_exists: ${{output}}
        """)
        write_macro(tmp_path, "write_and_verify", yaml_content)
        reg = MacroRegistry(str(tmp_path))
        rt = MacroRuntime(registry=reg)
        result = rt.execute("write_and_verify", {"output": str(output_file)})
        assert result.success, f"Failed: {result.error}"
        print(f"\n  Output file: {output_file} ({output_file.stat().st_size} bytes)")

    def test_postcondition_file_size_gt(self, tmp_path):
        from cli_anything.macrocli.core.registry import MacroRegistry
        from cli_anything.macrocli.core.runtime import MacroRuntime

        output_file = tmp_path / "output.txt"
        output_file.write_text("x" * 200, encoding="utf-8")

        yaml_content = textwrap.dedent(f"""\
            name: size_check
            parameters:
              output:
                type: string
                required: true
            steps:
              - id: noop
                backend: native_api
                action: run_command
                params:
                  command: [echo, noop]
            postconditions:
              - file_size_gt:
                  - ${{output}}
                  - 100
        """)
        write_macro(tmp_path, "size_check", yaml_content)
        reg = MacroRegistry(str(tmp_path))
        rt = MacroRuntime(registry=reg)
        result = rt.execute("size_check", {"output": str(output_file)})
        assert result.success, f"Failed: {result.error}"
        print(f"\n  File size: {output_file.stat().st_size} bytes")
