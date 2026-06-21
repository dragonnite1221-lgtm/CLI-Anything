# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _artifact_path, _assert_jpeg, test_video  # noqa: F401,E501


class _TestCLISubprocessMixin2:
    def test_cli_preview_capture(self, test_video):
        with tempfile.TemporaryDirectory() as tmp_dir:
            proj_path = os.path.join(tmp_dir, "preview.openscreen")

            result = self._run(
                ["project", "new", "-v", test_video, "-o", proj_path],
                check=False,
                timeout=60,
            )
            assert result.returncode == 0

            self._run(
                [
                    "--project",
                    proj_path,
                    "zoom",
                    "add",
                    "--start",
                    "700",
                    "--end",
                    "2200",
                    "--depth",
                    "2",
                ],
                check=False,
                timeout=60,
            )

            result = self._run(
                [
                    "--json",
                    "--project",
                    proj_path,
                    "preview",
                    "capture",
                    "--root-dir",
                    tmp_dir,
                ],
                check=False,
                timeout=180,
            )
            assert result.returncode == 0, result.stderr

            manifest = json.loads(result.stdout)
            assert manifest["software"] == "openscreen"
            clip_path = _artifact_path(manifest, "clip")
            hero_path = _artifact_path(manifest, "frame_03")
            assert os.path.isfile(clip_path)
            _assert_jpeg(hero_path)

            latest = self._run(
                [
                    "--json",
                    "preview",
                    "latest",
                    "--recipe",
                    "quick",
                    "--root-dir",
                    tmp_dir,
                ],
                check=False,
                timeout=60,
            )
            assert latest.returncode == 0, latest.stderr
            latest_manifest = json.loads(latest.stdout)
            assert latest_manifest["bundle_id"] == manifest["bundle_id"]

            print(f"\n  Openscreen preview bundle: {manifest['_bundle_dir']}")
            print(f"  Openscreen preview clip: {clip_path}")
            print(f"  Openscreen preview hero: {hero_path}")
