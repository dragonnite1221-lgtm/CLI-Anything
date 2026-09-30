"""Root argument shape tests, not evidence of real SMB/UNC behavior."""
import os
import pytest

pytestmark = pytest.mark.skipif(os.name != 'nt', reason='Windows API binding shape')


@pytest.mark.parametrize(('anchor', 'expected'), [
    ('C:\\', 'C:\\'),
    ('\\\\server\\share\\', '\\\\server\\share'),
    ('\\\\server\\\ud55c\uae00-share\\', '\\\\server\\\ud55c\uae00-share'),
])
def test_root_anchor_argument_preserves_drive_and_normalizes_unc(monkeypatch, anchor, expected):
    from cli_hub import _win_file_api as api
    seen = []

    def capture(path, access, sharing, security, disposition, flags, template):
        seen.append((path, sharing, disposition, flags))
        return 12345  # No network request or real OS handle in this shape test.

    monkeypatch.setattr(api.kernel, 'CreateFileW', capture)
    monkeypatch.setattr(api, 'verify', lambda handle: None)
    assert api.open_root(anchor) == 12345
    assert seen == [(expected, api.SHARE_READ_WRITE, 3, 0x02000000 | api.OPEN_REPARSE_POINT)]
