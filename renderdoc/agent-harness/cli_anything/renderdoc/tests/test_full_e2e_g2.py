# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


@skip_no_rd
@skip_no_cap
class TestPreviewCLIE2E:
    def test_cli_preview_capture(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = _run_cli("preview", "capture", "--root-dir", tmpdir)
            assert manifest["software"] == "renderdoc"
            summary_path = _artifact_path(manifest, "action_summary")
            assert os.path.isfile(summary_path)

            latest = _run_cli(
                "preview",
                "latest",
                "--recipe",
                "quick",
                "--bundle-kind",
                "capture",
                "--root-dir",
                tmpdir,
            )
            assert latest["bundle_id"] == manifest["bundle_id"]

            print(f"\n  RenderDoc preview bundle: {manifest['_bundle_dir']}")
            print(f"  RenderDoc action summary: {summary_path}")

    def test_cli_preview_diff(self):
        draws = _run_cli("actions", "list", "--draws-only")
        if not draws:
            pytest.skip("No draw calls in capture")

        event_a = int(draws[0]["eventId"])
        event_b = int(draws[-1]["eventId"])

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = _run_cli(
                "preview",
                "diff",
                str(event_a),
                str(event_b),
                "--root-dir",
                tmpdir,
            )
            assert manifest["software"] == "renderdoc"
            assert manifest["bundle_kind"] == "diff"
            diff_path = _artifact_path(manifest, "pipeline_diff")
            assert os.path.isfile(diff_path)

            latest = _run_cli(
                "preview",
                "latest",
                "--recipe",
                "diff",
                "--bundle-kind",
                "diff",
                "--root-dir",
                tmpdir,
            )
            assert latest["bundle_id"] == manifest["bundle_id"]

            print(f"\n  RenderDoc diff bundle: {manifest['_bundle_dir']}")
            print(f"  RenderDoc pipeline diff: {diff_path}")
