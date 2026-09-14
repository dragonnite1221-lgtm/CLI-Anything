"""Regression test: concurrent installer state read-modify-write must not
lose updates.

`install_cli`/`uninstall_cli`/`update_cli` each load installed.json, mutate
their own in-memory copy, and write the whole file back. With no locking
around that sequence, two CLI-Hub invocations running at the same time (e.g.
a user installing two CLIs at once, or an automation script fanning out
installs) can both load the same snapshot; whichever process saves last wins
and silently discards the other process's change.
"""

from __future__ import annotations

import json
import threading
import time
from unittest.mock import MagicMock, patch

from cli_hub import installer
from cli_hub.installer import install_cli

CLI_A = {
    "name": "cli-a",
    "display_name": "CLI A",
    "version": "1.0.0",
    "entry_point": "cli-a",
    "_source": "harness",
    "install_cmd": "pip install cli-a",
}

CLI_B = {
    "name": "cli-b",
    "display_name": "CLI B",
    "version": "1.0.0",
    "entry_point": "cli-b",
    "_source": "harness",
    "install_cmd": "pip install cli-b",
}


def _fake_get_cli(name, force_refresh=False):
    return CLI_A if name == "cli-a" else CLI_B


def test_concurrent_installs_do_not_lose_state(tmp_path):
    """Two installs racing on the same installed.json must both survive.

    _save_installed is patched to sleep briefly before writing so that,
    without a lock around the whole load-mutate-save sequence, both threads
    are guaranteed to load the pre-race snapshot before either one's write
    lands -- deterministically reproducing the lost-update race rather than
    depending on incidental thread-scheduling luck.
    """

    installed_file = tmp_path / "installed.json"
    real_save = installer._save_installed

    def _slow_save(data):
        time.sleep(0.2)
        real_save(data)

    with patch.object(installer, "INSTALLED_FILE", installed_file), \
            patch.object(installer, "get_cli", side_effect=_fake_get_cli), \
            patch.object(installer.subprocess, "run", return_value=MagicMock(returncode=0, stdout="", stderr="")), \
            patch.object(installer, "_save_installed", side_effect=_slow_save):

        results = {}

        def worker(name):
            results[name] = install_cli(name)

        t1 = threading.Thread(target=worker, args=("cli-a",))
        t2 = threading.Thread(target=worker, args=("cli-b",))
        t1.start()
        t2.start()
        t1.join(timeout=10)
        t2.join(timeout=10)

        assert not t1.is_alive() and not t2.is_alive(), "installs did not complete in time"
        assert results["cli-a"][0] is True
        assert results["cli-b"][0] is True

        final_state = json.loads(installed_file.read_text())

    assert set(final_state.keys()) == {"cli-a", "cli-b"}, (
        "concurrent installs lost an update to installed.json: "
        f"expected both cli-a and cli-b, got {sorted(final_state.keys())}"
    )
