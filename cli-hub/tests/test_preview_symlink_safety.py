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

import os

import pytest

from cli_hub._safe_output import _SUPPORTS_DIR_FD, open_safe_output, safe_output_file
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


def test_render_html_accepts_symlink_into_a_subdirectory(tmp_path):
    """A symlink whose target is nested *beneath* the intended directory
    (not just directly inside it) is still contained, not an escape."""
    bundle_dir = _make_preview_bundle(tmp_path)
    nested_dir = bundle_dir / "rendered"
    nested_dir.mkdir()
    real_output = nested_dir / "preview.html"
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


def test_open_safe_output_refuses_a_symlink_planted_after_the_check(tmp_path):
    """Closes the TOCTOU gap: safe_output_file() only sees a symlink that
    already exists at check time. HTML generation runs between that check
    and the actual write, so a symlink can be planted at the exact output
    path during that window. The write itself (open_safe_output, using
    O_NOFOLLOW) must still refuse to follow it rather than silently
    clobbering whatever it points to."""
    output_path = tmp_path / "preview.html"
    resolved = safe_output_file(str(output_path))  # nothing exists yet -> passes

    victim = tmp_path / "victim.txt"
    victim.write_text("do-not-overwrite")
    resolved.symlink_to(victim)  # attacker plants the symlink after the check

    with pytest.raises(ValueError, match="symlink"):
        with open_safe_output(resolved) as fh:
            fh.write("clobbered")

    assert victim.read_text() == "do-not-overwrite"


@pytest.mark.skipif(not _SUPPORTS_DIR_FD, reason="dir_fd not supported on this platform")
def test_open_safe_output_leaf_creation_is_pinned_to_the_opened_directory(tmp_path, monkeypatch):
    """A bare O_NOFOLLOW open only guards the final path component: another
    process could rename the containing directory elsewhere and put a
    symlink to a decoy directory at its old pathname. Once
    open_safe_output has opened the (real) directory by descriptor, the
    leaf must still be created relative to that originally-opened
    directory, unaffected by the pathname now pointing elsewhere --
    verified here by performing that exact rename-and-relink from inside a
    patched os.open, standing in for a concurrent attacker, timed to land
    right after the directory descriptor is obtained but before the leaf
    is created."""
    real_dir = tmp_path / "bundle"
    real_dir.mkdir()
    moved_dir = tmp_path / "moved-away"
    decoy_dir = tmp_path / "decoy"
    decoy_dir.mkdir()
    output_path = real_dir / "preview.html"
    resolved = safe_output_file(str(output_path))

    real_os_open = os.open

    def _relocate_directory_then_open(path, *args, **kwargs):
        if path == "preview.html" and "dir_fd" in kwargs:
            real_dir.rename(moved_dir)
            real_dir.symlink_to(decoy_dir)
        return real_os_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", _relocate_directory_then_open)

    with open_safe_output(resolved) as fh:
        fh.write("hello")

    assert (moved_dir / "preview.html").read_text() == "hello"
    assert not (decoy_dir / "preview.html").exists()
