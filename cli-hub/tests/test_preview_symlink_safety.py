"""Regression tests for CLI-Anything P2-3: the default preview output file
(preview.html / live.html) must not follow a symlink that escapes the
bundle/session directory.

Bundle and live-session directories can originate from untrusted input (a
shared bundle archive, an imported session). If one plants a symlink at the
well-known output filename, naively following it on write would let
`cli-hub previews html` / `cli-hub previews watch` clobber an arbitrary file
the current user can write, anywhere on disk.
"""

from __future__ import annotations

import pytest

from cli_hub.preview import render_html, render_live_html
from tests.test_cli_hub import _make_preview_bundle, _make_preview_session


def test_render_html_rejects_symlinked_output_escaping_directory(tmp_path):
    bundle_dir = _make_preview_bundle(tmp_path)
    victim = tmp_path / "outside" / "victim.txt"
    victim.parent.mkdir(parents=True)
    victim.write_text("do-not-overwrite")

    output_path = bundle_dir / "preview.html"
    output_path.symlink_to(victim)

    with pytest.raises(ValueError, match="symlink"):
        render_html(str(bundle_dir), str(output_path))

    assert victim.read_text() == "do-not-overwrite"


def test_render_html_still_follows_symlink_within_same_directory(tmp_path):
    """A symlink that stays inside the requested output directory is not an
    escape and should still resolve and render normally."""
    bundle_dir = _make_preview_bundle(tmp_path)
    real_output = bundle_dir / "actual-preview.html"
    symlinked_output = bundle_dir / "preview.html"
    real_output.touch()
    symlinked_output.symlink_to(real_output)

    rendered = render_html(str(bundle_dir), str(symlinked_output))

    assert rendered == str(real_output.resolve())
    assert real_output.read_text()


def test_render_live_html_rejects_symlinked_output_escaping_directory(tmp_path):
    session_dir = _make_preview_session(tmp_path)
    victim = tmp_path / "outside" / "victim.txt"
    victim.parent.mkdir(parents=True)
    victim.write_text("do-not-overwrite")

    output_path = session_dir / "live.html"
    output_path.symlink_to(victim)

    with pytest.raises(ValueError, match="symlink"):
        render_live_html(str(session_dir), str(output_path), poll_ms=800)

    assert victim.read_text() == "do-not-overwrite"
