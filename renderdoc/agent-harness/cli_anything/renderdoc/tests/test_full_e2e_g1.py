# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


@skip_no_rd
@skip_no_cap
class TestPreviewAPIE2E:
    def test_preview_capture_bundle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open_capture(TEST_CAPTURE) as handle:
                manifest = preview_mod.capture(
                    handle,
                    TEST_CAPTURE,
                    root_dir=tmpdir,
                    force=True,
                )

            assert manifest["software"] == "renderdoc"
            assert manifest["bundle_kind"] == "capture"
            assert manifest["status"] in ("ok", "partial")

            artifact_ids = {
                artifact["artifact_id"] for artifact in manifest["artifacts"]
            }
            assert "action_summary" in artifact_ids
            summary_path = _artifact_path(manifest, "action_summary")
            assert os.path.isfile(summary_path)

            latest = preview_mod.latest(
                project_path=TEST_CAPTURE,
                recipe="quick",
                bundle_kind="capture",
                root_dir=tmpdir,
            )
            assert latest["bundle_id"] == manifest["bundle_id"]

            print(f"\n  RenderDoc preview bundle: {manifest['_bundle_dir']}")
            print(f"  RenderDoc action summary: {summary_path}")

    def test_preview_diff_bundle(self):
        draws = _run_cli("actions", "list", "--draws-only")
        if not draws:
            pytest.skip("No draw calls in capture")

        event_a = int(draws[0]["eventId"])
        event_b = int(draws[-1]["eventId"])

        with tempfile.TemporaryDirectory() as tmpdir:
            with (
                open_capture(TEST_CAPTURE) as handle_a,
                open_capture(TEST_CAPTURE) as handle_b,
            ):
                manifest = preview_mod.diff(
                    handle_a,
                    TEST_CAPTURE,
                    event_a,
                    handle_b,
                    TEST_CAPTURE,
                    event_b,
                    root_dir=tmpdir,
                    force=True,
                )

            assert manifest["software"] == "renderdoc"
            assert manifest["bundle_kind"] == "diff"
            diff_path = _artifact_path(manifest, "pipeline_diff")
            assert os.path.isfile(diff_path)
            with open(diff_path, "r", encoding="utf-8") as fh:
                diff_data = json.load(fh)
            assert isinstance(diff_data, dict)

            latest = preview_mod.latest(
                project_path=TEST_CAPTURE,
                recipe="diff",
                bundle_kind="diff",
                root_dir=tmpdir,
            )
            assert latest["bundle_id"] == manifest["bundle_id"]

            print(f"\n  RenderDoc diff bundle: {manifest['_bundle_dir']}")
            print(f"  RenderDoc pipeline diff: {diff_path}")
