# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestMacroModel:
    def test_load_from_yaml(self, tmp_path):
        from cli_anything.macrocli.core.macro_model import load_from_yaml

        p = write_macro(tmp_path, "test_macro", SIMPLE_MACRO_YAML)
        m = load_from_yaml(str(p))
        assert m.name == "test_macro"
        assert m.version == "1.0"
        assert "output" in m.parameters
        assert len(m.steps) == 1
        assert m.steps[0].backend == "native_api"

    def test_load_missing_file(self):
        from cli_anything.macrocli.core.macro_model import load_from_yaml

        with pytest.raises(FileNotFoundError):
            load_from_yaml("/nonexistent/path.yaml")

    def test_validate_params_required(self, tmp_path):
        from cli_anything.macrocli.core.macro_model import load_from_yaml

        p = write_macro(tmp_path, "test_macro", SIMPLE_MACRO_YAML)
        m = load_from_yaml(str(p))
        errors = m.validate_params({})
        assert any("output" in e for e in errors)

    def test_validate_params_type_error(self, tmp_path):
        from cli_anything.macrocli.core.macro_model import load_from_yaml

        p = write_macro(tmp_path, "test_macro", SIMPLE_MACRO_YAML)
        m = load_from_yaml(str(p))
        errors = m.validate_params({"output": "/tmp/x", "count": "not_an_int"})
        assert any("count" in e for e in errors)

    def test_validate_params_range(self, tmp_path):
        from cli_anything.macrocli.core.macro_model import load_from_yaml

        p = write_macro(tmp_path, "test_macro", SIMPLE_MACRO_YAML)
        m = load_from_yaml(str(p))
        errors = m.validate_params({"output": "/tmp/x", "count": 200})
        assert any("count" in e for e in errors)

    def test_validate_params_ok(self, tmp_path):
        from cli_anything.macrocli.core.macro_model import load_from_yaml

        p = write_macro(tmp_path, "test_macro", SIMPLE_MACRO_YAML)
        m = load_from_yaml(str(p))
        errors = m.validate_params({"output": "/tmp/x"})
        assert errors == []

    def test_resolve_params_defaults(self, tmp_path):
        from cli_anything.macrocli.core.macro_model import load_from_yaml

        p = write_macro(tmp_path, "test_macro", SIMPLE_MACRO_YAML)
        m = load_from_yaml(str(p))
        resolved = m.resolve_params({"output": "/tmp/x"})
        assert resolved["count"] == 1

    def test_structural_validation_no_steps(self, tmp_path):
        from cli_anything.macrocli.core.macro_model import load_from_yaml

        yaml_content = "name: bad\nsteps: []\n"
        p = write_macro(tmp_path, "bad", yaml_content)
        m = load_from_yaml(str(p))
        errors = m.validate()
        assert any("steps" in e for e in errors)

    def test_structural_validation_bad_backend(self, tmp_path):
        from cli_anything.macrocli.core.macro_model import load_from_yaml

        yaml_content = textwrap.dedent("""\
            name: bad
            steps:
              - id: x
                backend: fake_backend
                action: do_thing
        """)
        p = write_macro(tmp_path, "bad_backend", yaml_content)
        m = load_from_yaml(str(p))
        errors = m.validate()
        assert any("fake_backend" in e for e in errors)

    def test_to_dict(self, tmp_path):
        from cli_anything.macrocli.core.macro_model import load_from_yaml

        p = write_macro(tmp_path, "test_macro", SIMPLE_MACRO_YAML)
        m = load_from_yaml(str(p))
        d = m.to_dict()
        assert d["name"] == "test_macro"
        assert "parameters" in d
        assert "steps" in d


class TestSubstitute:
    def test_string_substitution(self):
        from cli_anything.macrocli.core.macro_model import substitute

        result = substitute("hello ${name}", {"name": "world"})
        assert result == "hello world"

    def test_nested_list(self):
        from cli_anything.macrocli.core.macro_model import substitute

        result = substitute(["echo", "${output}"], {"output": "/tmp/x"})
        assert result == ["echo", "/tmp/x"]

    def test_nested_dict(self):
        from cli_anything.macrocli.core.macro_model import substitute

        result = substitute({"path": "${output}", "other": 42}, {"output": "/out"})
        assert result["path"] == "/out"
        assert result["other"] == 42

    def test_missing_key_left_as_is(self):
        from cli_anything.macrocli.core.macro_model import substitute

        result = substitute("${missing}", {})
        assert result == "${missing}"
