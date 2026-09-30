"""Filesystem paths used in HTML must be URL paths on every platform."""
import json
from pathlib import Path
from cli_hub.preview import _artifact_href, inspect_session, render_live_html
from tests._symlinks import symlink_to
from tests.test_cli_hub import _make_preview_session


def test_session_current_directory_symlink(tmp_path):
    import shutil

    session = _make_preview_session(tmp_path)
    current = session / "current"
    shutil.rmtree(current)
    symlink_to(current, tmp_path / "preview-bundle", target_is_directory=True)
    assert current.is_symlink()
    assert current.resolve() == (tmp_path / "preview-bundle").resolve()
    inspected = inspect_session(str(session))
    assert inspected["current_bundle"]["manifest"]["bundle_id"] == "20260419T104530Z_deadbeef_quick"
    output = render_live_html(str(session), str(session / "live.html"))
    content = Path(output).read_text(encoding="utf-8")
    # Live HTML polls the manifest through current; artifact labels are not
    # embedded in the generated shell as they are in a static bundle preview.
    assert 'const CURRENT_LINK = "current";' in content
    assert 'manifest = await fetchJson(`${CURRENT_LINK}/manifest.json`);' in content
    manifest = json.loads((current / "manifest.json").read_text(encoding="utf-8"))
    hero = next(artifact for artifact in manifest["artifacts"] if artifact["artifact_id"] == "hero")
    assert hero["label"] == "Midpoint frame"
    assert (current / hero["path"]).read_bytes() == (tmp_path / "preview-bundle" / hero["path"]).read_bytes()


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
