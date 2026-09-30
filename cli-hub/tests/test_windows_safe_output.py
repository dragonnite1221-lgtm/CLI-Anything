"""Real Windows handle tests; no symlink privilege or account changes."""
import os
from pathlib import Path
import subprocess
import pytest
from cli_hub._safe_output import open_safe_output, safe_output_file

pytestmark = pytest.mark.skipif(os.name != 'nt', reason='Native Windows handle APIs')


def junction(link, target):
    result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(target)],
                            capture_output=True)
    assert result.returncode == 0, result.stderr


def test_native_create_overwrite_utf8(tmp_path):
    directory = tmp_path / '\ud55c\uae00-\U0001f600'
    directory.mkdir()
    path = directory / 'preview.html'
    for text in ('long original contents', '\ud55c\uae00'):
        with open_safe_output(path) as output:
            output.write(text)
        assert path.read_text(encoding='utf-8') == text


def test_native_rejects_parent_junction_planted_after_check(tmp_path):
    parent, moved, decoy = (tmp_path / name for name in ('bundle', 'moved', 'decoy'))
    parent.mkdir()
    decoy.mkdir()
    victim = decoy / 'preview.html'
    victim.write_text('preserve')
    checked = safe_output_file(str(parent / 'preview.html'))
    parent.rename(moved)
    junction(parent, decoy)
    try:
        with pytest.raises(ValueError, match='reparse'):
            open_safe_output(checked)
        assert victim.read_text() == 'preserve'
    finally:
        parent.rmdir()  # Remove junction entry only, never recurse into target.


def test_native_open_parent_blocks_rename_before_leaf(tmp_path, monkeypatch):
    from cli_hub import _win_file_api as api
    parent = tmp_path / 'bundle'
    parent.mkdir()
    real_open = api.open_relative
    blocked = []

    def attempt_rename(handle, name, *, leaf=False):
        if leaf:
            with pytest.raises(OSError) as error:
                parent.rename(tmp_path / 'moved')
            assert error.value.winerror == 32
            blocked.append(True)
        return real_open(handle, name, leaf=leaf)

    monkeypatch.setattr(api, 'open_relative', attempt_rename)
    with open_safe_output(parent / 'preview.html') as output:
        output.write('safe')
    assert blocked == [True]
    assert (parent / 'preview.html').read_text() == 'safe'


def test_native_rejects_hardlink_planted_before_leaf_open(tmp_path, monkeypatch):
    from cli_hub import _win_file_api as api
    victim = tmp_path / 'victim.txt'
    victim.write_text('preserve')
    output = tmp_path / 'preview.html'
    real_open = api.open_relative

    def plant_link(handle, name, *, leaf=False):
        if leaf:
            os.link(victim, output)
        return real_open(handle, name, leaf=leaf)

    monkeypatch.setattr(api, 'open_relative', plant_link)
    with pytest.raises(ValueError, match='multiply-linked'):
        open_safe_output(output)
    assert victim.read_text() == 'preserve'


def test_native_open_leaf_blocks_replacement_before_validation(tmp_path, monkeypatch):
    from cli_hub import _win_file_api as api
    path = tmp_path / 'preview.html'
    path.write_text('original')
    real_verify = api.verify
    blocked = []

    def attempt_replace(handle, *, leaf=False):
        if leaf:
            with pytest.raises(OSError) as error:
                path.rename(tmp_path / 'moved.html')
            assert error.value.winerror == 32
            blocked.append(True)
        real_verify(handle, leaf=leaf)

    monkeypatch.setattr(api, 'verify', attempt_replace)
    with open_safe_output(path) as output:
        output.write('safe')
    assert blocked == [True]
    assert path.read_text() == 'safe'


@pytest.mark.parametrize('name', ['preview.html:stream', 'preview.html.', 'preview.html '])
def test_native_rejects_ambiguous_leaf_names(tmp_path, name):
    with pytest.raises(ValueError, match='Ambiguous'):
        open_safe_output(tmp_path / name)


def test_native_failed_validation_releases_leaf_and_parents(tmp_path, monkeypatch):
    from cli_hub import _win_file_api as api
    parent = tmp_path / 'bundle'
    parent.mkdir()
    path = parent / 'preview.html'
    path.write_text('preserve')
    real_verify = api.verify

    def refuse(handle, *, leaf=False):
        if leaf:
            raise ValueError('synthetic validation failure')
        real_verify(handle, leaf=leaf)

    monkeypatch.setattr(api, 'verify', refuse)
    with pytest.raises(ValueError, match='synthetic'):
        open_safe_output(path)
    assert path.read_text() == 'preserve'
    path.rename(parent / 'moved.html')
    parent.rename(tmp_path / 'moved-directory')


@pytest.mark.parametrize('stage', ['transfer', 'truncate'])
def test_native_failed_descriptor_setup_releases_handle(tmp_path, monkeypatch, stage):
    from cli_hub import _win_safe_output as writer
    path = tmp_path / 'preview.html'
    path.write_text('preserve')

    def fail(*args):
        raise OSError('synthetic descriptor failure')

    if stage == 'transfer':
        monkeypatch.setattr(writer.msvcrt, 'open_osfhandle', fail)
    else:
        monkeypatch.setattr(writer.os, 'ftruncate', fail)
    with pytest.raises(OSError, match='synthetic'):
        open_safe_output(path)
    assert path.read_text() == 'preserve'
    path.rename(tmp_path / 'moved.html')


def test_native_rejects_parent_converted_to_junction_while_held(tmp_path, monkeypatch):
    from cli_hub import _win_file_api as api
    from tests._windows_reparse import junction_in_place
    parent, decoy = tmp_path / 'bundle', tmp_path / 'decoy'
    parent.mkdir()
    decoy.mkdir()
    victim = decoy / 'preview.html'
    victim.write_text('preserve')
    real_open = api.open_relative

    def convert_parent(handle, name, *, leaf=False):
        if leaf:
            with junction_in_place(parent, decoy):
                return real_open(handle, name, leaf=True)
        return real_open(handle, name, leaf=False)

    monkeypatch.setattr(api, 'open_relative', convert_parent)
    with pytest.raises(OSError) as error:
        open_safe_output(parent / 'preview.html')
    assert error.value.winerror == 1921  # ERROR_CANT_RESOLVE_FILENAME, fail closed.
    assert victim.read_text() == 'preserve'
    assert list(parent.iterdir()) == []


def test_native_descriptor_is_explicitly_noninheritable(tmp_path, monkeypatch):
    from cli_hub import _win_safe_output as writer
    transfer = writer.msvcrt.open_osfhandle
    flags_seen = []

    def record_transfer(handle, flags):
        flags_seen.append(flags)
        return transfer(handle, flags)

    monkeypatch.setattr(writer.msvcrt, 'open_osfhandle', record_transfer)
    with open_safe_output(tmp_path / 'preview.html') as output:
        assert not os.get_inheritable(output.fileno())
        output.write('safe')
    assert len(flags_seen) == 1 and flags_seen[0] & os.O_NOINHERIT
