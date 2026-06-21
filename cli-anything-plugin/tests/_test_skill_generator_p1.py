# ruff: noqa: F403, F405, E501
from ._test_skill_generator_base import *  # noqa: F403


class TestGenerateSkillMd:
    def _make_metadata(self, **overrides):
        defaults = dict(
            skill_name="cli-anything-testapp",
            skill_description="CLI for TestApp",
            software_name="testapp",
            skill_intro="A test application.",
            version="1.0.0",
            system_package=None,
            command_groups=[],
            examples=[],
        )
        defaults.update(overrides)
        return SkillMetadata(**defaults)

    def test_simple_output_has_yaml_frontmatter(self):
        metadata = self._make_metadata()
        content = generate_skill_md_simple(metadata)
        assert content.startswith("---")
        assert 'name: "cli-anything-testapp"' in content
        assert 'description: "CLI for TestApp"' in content

    def test_simple_output_has_installation_section(self):
        metadata = self._make_metadata()
        content = generate_skill_md_simple(metadata)
        assert "## Installation" in content
        assert "pip install cli-anything-testapp" in content

    def test_simple_output_includes_version(self):
        metadata = self._make_metadata(version="2.5.0")
        content = generate_skill_md_simple(metadata)
        assert "2.5.0" in content

    def test_simple_output_has_command_groups(self):
        groups = [
            CommandGroup(
                name="Export",
                description="Export commands",
                commands=[
                    CommandInfo(name="pdf", description="Export as PDF"),
                    CommandInfo(name="svg", description="Export as SVG"),
                ],
            )
        ]
        metadata = self._make_metadata(command_groups=groups)
        content = generate_skill_md_simple(metadata)
        assert "### Export" in content
        assert "`pdf`" in content
        assert "`svg`" in content

    def test_simple_output_has_examples(self):
        examples = [
            Example(
                title="Quick Start",
                description="Get started quickly",
                code="cli-anything-testapp --help",
            )
        ]
        metadata = self._make_metadata(examples=examples)
        content = generate_skill_md_simple(metadata)
        assert "### Quick Start" in content
        assert "cli-anything-testapp --help" in content

    def test_generate_skill_md_falls_back_to_simple(self):
        metadata = self._make_metadata()
        # Without a template file, should fall back to simple generation
        content = generate_skill_md(metadata, template_path="/nonexistent/template")
        assert "cli-anything-testapp" in content

    def test_generate_skill_md_with_no_template_arg(self):
        metadata = self._make_metadata()
        # Should work without template_path argument (uses default or falls back)
        content = generate_skill_md(metadata)
        assert isinstance(content, str)
        assert len(content) > 0


class TestGenerateSkillFile:
    def test_generates_file_at_default_path(self, harness_dir):
        output = generate_skill_file(str(harness_dir))
        assert Path(output).exists()
        content = Path(output).read_text()
        assert "cli-anything-testapp" in content

    def test_generates_file_at_custom_path(self, harness_dir, tmp_path):
        output_file = tmp_path / "custom" / "SKILL.md"
        output = generate_skill_file(str(harness_dir), str(output_file))
        assert Path(output).exists()
        content = Path(output).read_text()
        assert "testapp" in content.lower()

    def test_creates_parent_directories(self, harness_dir, tmp_path):
        output_file = tmp_path / "deep" / "nested" / "dir" / "SKILL.md"
        output = generate_skill_file(str(harness_dir), str(output_file))
        assert Path(output).exists()
