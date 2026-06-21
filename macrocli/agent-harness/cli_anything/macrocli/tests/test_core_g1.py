# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestMacroRegistry:
    def test_load_macro(self, tmp_path):
        from cli_anything.macrocli.core.registry import MacroRegistry

        write_macro(tmp_path, "test_macro", SIMPLE_MACRO_YAML)
        reg = MacroRegistry(str(tmp_path))
        m = reg.load("test_macro")
        assert m.name == "test_macro"

    def test_load_missing_raises(self, tmp_path):
        from cli_anything.macrocli.core.registry import MacroRegistry

        reg = MacroRegistry(str(tmp_path))
        with pytest.raises(KeyError):
            reg.load("nonexistent_macro")

    def test_list_all(self, tmp_path):
        from cli_anything.macrocli.core.registry import MacroRegistry

        write_macro(tmp_path, "test_macro", SIMPLE_MACRO_YAML)
        write_macro(
            tmp_path, "another", SIMPLE_MACRO_YAML.replace("test_macro", "another")
        )
        reg = MacroRegistry(str(tmp_path))
        names = reg.list_names()
        assert "test_macro" in names
        assert "another" in names

    def test_manifest_index(self, tmp_path):
        from cli_anything.macrocli.core.registry import MacroRegistry

        sub = tmp_path / "sub"
        sub.mkdir()
        write_macro(sub, "alpha", SIMPLE_MACRO_YAML.replace("test_macro", "alpha"))
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text("macros:\n  - name: alpha\n    path: sub/alpha.yaml\n")
        reg = MacroRegistry(str(tmp_path))
        m = reg.load("alpha")
        assert m.name == "alpha"

    def test_register_programmatic(self):
        from cli_anything.macrocli.core.registry import MacroRegistry
        from cli_anything.macrocli.core.macro_model import MacroDefinition, MacroStep

        reg = MacroRegistry("/nonexistent")
        macro = MacroDefinition(
            name="inline_macro",
            steps=[MacroStep(backend="native_api", action="run_command")],
        )
        reg.register(macro)
        assert reg.load("inline_macro").name == "inline_macro"

    def test_info(self, tmp_path):
        from cli_anything.macrocli.core.registry import MacroRegistry

        write_macro(tmp_path, "test_macro", SIMPLE_MACRO_YAML)
        reg = MacroRegistry(str(tmp_path))
        info = reg.info()
        assert info["total"] >= 1
        assert "macros_dir" in info
