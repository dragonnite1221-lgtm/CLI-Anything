# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class PathDiscoveryTests(unittest.TestCase):
    def test_build_environment_uses_active_profile_and_data_dir_pref(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = create_sample_environment(Path(tmpdir))
            runtime_env = zotero_paths.build_environment(
                explicit_profile_dir=str(env["profile_root"]),
                explicit_executable=str(env["executable"]),
            )
            self.assertEqual(runtime_env.profile_dir, env["profile_dir"])
            self.assertEqual(runtime_env.data_dir, env["data_dir"])
            self.assertEqual(runtime_env.sqlite_path, env["sqlite_path"])
            self.assertEqual(runtime_env.version, "7.0.32")

    def test_build_environment_accepts_env_profile_dir_pointing_to_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = create_sample_environment(Path(tmpdir))
            with mock.patch.dict("os.environ", {"ZOTERO_PROFILE_DIR": str(env["profile_dir"])}, clear=False):
                runtime_env = zotero_paths.build_environment(
                    explicit_executable=str(env["executable"]),
                    explicit_data_dir=str(env["data_dir"]),
                )
            self.assertEqual(runtime_env.profile_dir, env["profile_dir"])

    def test_build_environment_falls_back_to_home_zotero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            profile_root = Path(tmpdir) / "AppData" / "Roaming" / "Zotero" / "Zotero"
            profile_dir = profile_root / "Profiles" / "test.default"
            profile_dir.mkdir(parents=True, exist_ok=True)
            (profile_root / "profiles.ini").write_text("[Profile0]\nName=default\nIsRelative=1\nPath=Profiles/test.default\nDefault=1\n", encoding="utf-8")
            (profile_dir / "prefs.js").write_text("", encoding="utf-8")
            home = Path(tmpdir) / "Home"
            (home / "Zotero").mkdir(parents=True, exist_ok=True)
            with mock.patch("cli_anything.zotero.utils.zotero_paths.Path.home", return_value=home):
                runtime_env = zotero_paths.build_environment(explicit_profile_dir=str(profile_root))
            self.assertEqual(runtime_env.data_dir, home / "Zotero")

    def test_ensure_local_api_enabled_writes_user_js(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = create_sample_environment(Path(tmpdir))
            path = zotero_paths.ensure_local_api_enabled(env["profile_dir"])
            self.assertIsNotNone(path)
            self.assertIn('extensions.zotero.httpServer.localAPI.enabled', path.read_text(encoding="utf-8"))

    def test_find_executable_returns_none_when_unresolved(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with mock.patch("cli_anything.zotero.utils.zotero_paths.shutil.which", return_value=None):
                with mock.patch("pathlib.Path.exists", return_value=False):
                    self.assertIsNone(zotero_paths.find_executable(env={}))
