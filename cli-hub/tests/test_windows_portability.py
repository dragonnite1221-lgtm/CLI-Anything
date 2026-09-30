"""Filesystem paths used in HTML must be URL paths on every platform."""
from cli_hub.preview import _artifact_href, inspect_session, render_live_html
from tests._symlinks import symlink_to
from tests.test_cli_hub import _make_preview_session


def test_session_current_directory_symlink(tmp_path):
    import shutil

    session = _make_preview_session(tmp_path)
    current = session / "current"
    shutil.rmtree(current)
    symlink_to(current, tmp_path / "preview-bundle", target_is_directory=True)
    inspected = inspect_session(str(session))
    assert inspected["current_bundle"]["manifest"]["bundle_id"] == "20260419T104530Z_deadbeef_quick"
    output = render_live_html(str(session), str(session / "live.html"))
    assert "Midpoint frame" in open(output, encoding="utf-8").read()


def test_artifact_href_uses_url_separators(tmp_path):
    bundle = tmp_path / "bundle"
    artifact = bundle / "artifacts" / "hero.png"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"image")
    assert _artifact_href(tmp_path, bundle, "artifacts/hero.png") == "bundle/artifacts/hero.png"


def test_artifact_href_from_sibling_output_directory(tmp_path):
    bundle = tmp_path / "bundle"
    output = tmp_path / "pages"
    output.mkdir()
    assert _artifact_href(output, bundle, "artifacts/hero.png") == "../bundle/artifacts/hero.png"
