"""Create real symlinks, skipping only missing Windows privileges."""
import os

import pytest


def symlink_to(link, target, *, target_is_directory=False):
    try:
        link.symlink_to(target, target_is_directory=target_is_directory)
    except OSError as error:
        if os.name == "nt" and error.winerror == 1314:
            pytest.skip("Windows symlink creation requires privilege (WinError 1314)")
        raise
