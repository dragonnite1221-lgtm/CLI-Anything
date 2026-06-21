# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestBackendDiscovery:
    def test_default_windows_install_dirs_prefers_higher_version(self):
        with patch("cli_anything.nsight_graphics.utils.nsight_graphics_backend._fixed_windows_drive_roots", return_value=["C:", "D:"]):
            result = backend._default_windows_install_dirs(
                lambda pattern: {
                    "C:/Program Files/NVIDIA Corporation/Nsight Graphics */host/windows-desktop-nomad-x64": [
                        "C:/Program Files/NVIDIA Corporation/Nsight Graphics 2023.3.2/host/windows-desktop-nomad-x64"
                    ],
                    "D:/Program Files/NVIDIA Corporation/Nsight Graphics */host/windows-desktop-nomad-x64": [
                        "D:/Program Files/NVIDIA Corporation/Nsight Graphics 2026.1.0/host/windows-desktop-nomad-x64"
                    ],
                    "C:/Program Files (x86)/NVIDIA Corporation/Nsight Graphics */host/windows-desktop-nomad-x64": [],
                    "D:/Program Files (x86)/NVIDIA Corporation/Nsight Graphics */host/windows-desktop-nomad-x64": [],
                }.get(pattern, [])
            )
        assert result[0].startswith("D:/Program Files")

    def test_discover_binaries_from_env_dir(self, tmp_path):
        (tmp_path / "ngfx.exe").write_text("", encoding="utf-8")
        (tmp_path / "ngfx-capture.exe").write_text("", encoding="utf-8")

        result = backend.discover_binaries(
            env={backend.ENV_VAR: str(tmp_path)},
            which=lambda _: None,
            glob_func=lambda _: [],
            platform_system="Windows",
        )

        assert result["binaries"]["ngfx"].endswith("ngfx.exe")
        assert result["binaries"]["ngfx_capture"].endswith("ngfx-capture.exe")
        assert result["effective_override"] == str(tmp_path)

    def test_discover_binaries_prefers_cli_override(self, tmp_path):
        (tmp_path / "ngfx.exe").write_text("", encoding="utf-8")
        result = backend.discover_binaries(
            env={backend.ENV_VAR: "C:/Ignored/FromEnv"},
            nsight_path=str(tmp_path),
            which=lambda _: None,
            glob_func=lambda _: [],
            platform_system="Windows",
        )
        assert result["cli_override"] == str(tmp_path)
        assert result["effective_override"] == str(tmp_path)
        assert result["binaries"]["ngfx"].endswith("ngfx.exe")

    def test_detect_tool_mode(self):
        assert backend.detect_tool_mode({"ngfx": "a", "ngfx_capture": None, "ngfx_replay": None}) == "unified"
        assert backend.detect_tool_mode({"ngfx": "a", "ngfx_capture": "b", "ngfx_replay": "c"}) == "unified+split"
        assert backend.detect_tool_mode({"ngfx": None, "ngfx_capture": "a", "ngfx_replay": None}) == "split"
        assert backend.detect_tool_mode({"ngfx": None, "ngfx_capture": None, "ngfx_replay": None}) == "missing"

    def test_prepare_output_dir_creates_missing_directory(self, tmp_path):
        output_dir = tmp_path / "new" / "capture-output"
        assert not output_dir.exists()
        resolved = backend.prepare_output_dir(str(output_dir))
        assert resolved == str(output_dir.resolve())
        assert output_dir.is_dir()

    def test_list_installations_reports_versions(self, tmp_path):
        install_dir = tmp_path / "Nsight Graphics 2025.1" / "host" / "windows-desktop-nomad-x64"
        install_dir.mkdir(parents=True)
        (install_dir / "ngfx.exe").write_text("", encoding="utf-8")
        (install_dir / "ngfx-ui.exe").write_text("", encoding="utf-8")

        with patch("cli_anything.nsight_graphics.utils.backend.discovery._read_registry_installations", return_value=[]):
            result = backend.list_installations(
                env={},
                nsight_path=str(install_dir),
                which=lambda _: None,
                glob_func=lambda _: [str(install_dir)],
                platform_system="Windows",
            )

        assert result["count"] == 1
        assert result["installations"][0]["version"] == "2025.1"
        assert result["installations"][0]["selected"] is True

    def test_list_installations_includes_registry_only_entries(self):
        registry_entries = [
            {
                "display_name": "NVIDIA Nsight Graphics 2026.1.0",
                "display_version": "26.1.26068.0509",
                "install_location": None,
                "install_source": "C:/Users/Test/Downloads",
                "uninstall_string": "msiexec /x ...",
                "publisher": "NVIDIA Corporation",
                "registry_key": r"HKLM\SOFTWARE\...\{ABC}",
            }
        ]
        with patch("cli_anything.nsight_graphics.utils.backend.discovery._read_registry_installations", return_value=registry_entries):
            result = backend.list_installations(
                env={},
                which=lambda _: None,
                glob_func=lambda _: [],
                platform_system="Windows",
            )

        assert result["count"] == 1
        assert result["registry_count"] == 1
        assert result["installations"][0]["version"] == "2026.1.0"
        assert result["installations"][0]["registered_only"] is True
        assert result["installations"][0]["tool_mode"] == "registered-only"

    def test_list_installations_merges_registry_metadata_into_filesystem_entry(self, tmp_path):
        install_root = tmp_path / "Nsight Graphics 2025.1"
        install_dir = install_root / "host" / "windows-desktop-nomad-x64"
        install_dir.mkdir(parents=True)
        (install_dir / "ngfx.exe").write_text("", encoding="utf-8")

        registry_entries = [
            {
                "display_name": "NVIDIA Nsight Graphics 2025.1",
                "display_version": "25.1.0",
                "install_location": str(install_root),
                "install_source": "C:/Installers",
                "uninstall_string": "msiexec /x ...",
                "publisher": "NVIDIA Corporation",
                "registry_key": r"HKLM\SOFTWARE\...\{DEF}",
            }
        ]
        with patch("cli_anything.nsight_graphics.utils.backend.discovery._read_registry_installations", return_value=registry_entries):
            result = backend.list_installations(
                env={},
                nsight_path=str(install_dir),
                which=lambda _: None,
                glob_func=lambda _: [str(install_dir)],
                platform_system="Windows",
            )

        assert result["count"] == 1
        assert result["registry_count"] == 1
        assert result["installations"][0]["registered_only"] is False
        assert result["installations"][0]["display_name"] == "NVIDIA Nsight Graphics 2025.1"
        assert "registry" in result["installations"][0]["discovery_sources"]

    def test_list_installations_promotes_newer_drive_install(self, tmp_path):
        c_dir = tmp_path / "CDrive" / "Nsight Graphics 2023.3.2" / "host" / "windows-desktop-nomad-x64"
        d_dir = tmp_path / "DDrive" / "Nsight Graphics 2026.1.0" / "host" / "windows-desktop-nomad-x64"
        c_dir.mkdir(parents=True)
        d_dir.mkdir(parents=True)
        (c_dir / "ngfx.exe").write_text("", encoding="utf-8")
        (d_dir / "ngfx.exe").write_text("", encoding="utf-8")

        with patch("cli_anything.nsight_graphics.utils.nsight_graphics_backend._fixed_windows_drive_roots", return_value=["C:", "D:"]), \
             patch("cli_anything.nsight_graphics.utils.nsight_graphics_backend._read_registry_installations", return_value=[]):
            result = backend.list_installations(
                env={},
                which=lambda _: None,
                glob_func=lambda pattern: {
                    "C:/Program Files/NVIDIA Corporation/Nsight Graphics */host/windows-desktop-nomad-x64": [str(c_dir).replace("\\", "/")],
                    "D:/Program Files/NVIDIA Corporation/Nsight Graphics */host/windows-desktop-nomad-x64": [str(d_dir).replace("\\", "/")],
                    "C:/Program Files (x86)/NVIDIA Corporation/Nsight Graphics */host/windows-desktop-nomad-x64": [],
                    "D:/Program Files (x86)/NVIDIA Corporation/Nsight Graphics */host/windows-desktop-nomad-x64": [],
                }.get(pattern, []),
                platform_system="Windows",
            )

        assert result["installations"][0]["version"] == "2026.1.0"
