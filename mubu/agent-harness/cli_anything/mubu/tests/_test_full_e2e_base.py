# ruff: noqa: F403, F405, E501
"""Full end-to-end tests for cli-anything-mubu.

These tests invoke the CLI against real local Mubu desktop data.
They require the Mubu desktop app to have been used on this machine
so that backup, storage, and log directories exist.

Tests are skipped automatically when local data directories are missing.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


sys.path.insert(0, str(REPO_ROOT / "agent-harness"))


try:
    from mubu_probe import (
        DEFAULT_BACKUP_ROOT,
        DEFAULT_LOG_ROOT,
        DEFAULT_STORAGE_ROOT,
        build_folder_indexes,
        choose_current_daily_document,
        load_document_metas,
        load_folders,
    )
finally:
    sys.path.pop(0)


HAS_LOCAL_DATA = (
    DEFAULT_BACKUP_ROOT.is_dir()
    and DEFAULT_STORAGE_ROOT.is_dir()
)


def detect_daily_folder_ref() -> str | None:
    if not HAS_LOCAL_DATA:
        return None

    metas = load_document_metas(DEFAULT_STORAGE_ROOT)
    folders = load_folders(DEFAULT_STORAGE_ROOT)
    _, folder_paths = build_folder_indexes(folders)
    docs_by_folder: dict[str, list[dict[str, object]]] = {}
    for meta in metas:
        folder_id = meta.get("folder_id")
        if isinstance(folder_id, str):
            docs_by_folder.setdefault(folder_id, []).append(meta)

    best_path: str | None = None
    best_score = -1
    for folder in folders:
        folder_id = folder.get("folder_id")
        if not isinstance(folder_id, str):
            continue
        _, candidates = choose_current_daily_document(docs_by_folder.get(folder_id, []))
        if not candidates:
            continue
        folder_path = folder_paths.get(folder_id, "")
        if not folder_path:
            continue
        score = max(
            max(item.get("updated_at") or 0, item.get("created_at") or 0)
            for item in candidates
        )
        if score > best_score:
            best_score = score
            best_path = folder_path
    return best_path


DETECTED_DAILY_FOLDER_REF = detect_daily_folder_ref()


HAS_DAILY_FOLDER = HAS_LOCAL_DATA and DETECTED_DAILY_FOLDER_REF is not None


SKIP_REASON = "Mubu local data or a daily-style folder was not found"


LIVE_API_SKIP_MARKERS = (
    "CERTIFICATE_VERIFY_FAILED",
    "SSLCertVerificationError",
    "Hostname mismatch",
    "request failed for https://api2.mubu.com",
    "urlopen error",
)


def assert_cli_success_or_skip(testcase: unittest.TestCase, result: subprocess.CompletedProcess) -> None:
    if result.returncode == 0:
        return
    details = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    if any(marker in details for marker in LIVE_API_SKIP_MARKERS):
        testcase.skipTest(f"live Mubu API unavailable in this environment: {details.splitlines()[-1]}")
    testcase.fail(details or f"CLI exited with status {result.returncode}")


def resolve_cli() -> list[str]:
    installed = shutil.which("cli-anything-mubu")
    if installed:
        return [installed]
    return [sys.executable, "-m", "cli_anything.mubu"]


# fmt: off
__all__ = ['DETECTED_DAILY_FOLDER_REF', 'HAS_DAILY_FOLDER', 'HAS_LOCAL_DATA', 'LIVE_API_SKIP_MARKERS', 'Path', 'REPO_ROOT', 'SKIP_REASON', 'assert_cli_success_or_skip', 'detect_daily_folder_ref', 'json', 'os', 'resolve_cli', 'shutil', 'subprocess', 'sys', 'tempfile', 'unittest']  # noqa: E501
# fmt: on
