# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestFileTransformE2E:
    def test_json_set_and_verify(self, tmp_path):
        """Write a JSON file, transform it, verify the result."""
        from cli_anything.macrocli.core.macro_model import (
            MacroDefinition,
            MacroStep,
            MacroCondition,
            MacroOutput,
        )
        from cli_anything.macrocli.core.registry import MacroRegistry
        from cli_anything.macrocli.core.runtime import MacroRuntime

        json_file = tmp_path / "settings.json"
        json_file.write_text('{"version": 1}', encoding="utf-8")

        yaml_content = textwrap.dedent(f"""\
            name: set_json_key
            parameters:
              file:
                type: string
                required: true
              key:
                type: string
                required: true
              value:
                type: string
                required: true
            preconditions:
              - file_exists: ${{file}}
            steps:
              - id: transform
                backend: file_transform
                action: json_set
                params:
                  input_file: ${{file}}
                  output_file: ${{file}}
                  path: ${{key}}
                  value: ${{value}}
            postconditions:
              - file_exists: ${{file}}
            outputs:
              - name: modified_file
                path: ${{file}}
        """)
        write_macro(tmp_path, "set_json_key", yaml_content)

        reg = MacroRegistry(str(tmp_path))
        rt = MacroRuntime(registry=reg)
        result = rt.execute(
            "set_json_key",
            {
                "file": str(json_file),
                "key": "config.theme",
                "value": "dark",
            },
        )

        assert result.success, f"Failed: {result.error}"
        data = json.loads(json_file.read_text())
        assert data["config"]["theme"] == "dark"
        print(f"\n  Modified JSON: {json_file} → {json.dumps(data)}")
