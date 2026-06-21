# ruff: noqa: F403, F405, E501
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from cli_anything.mubu.mubu_cli import (
    dispatch,
    expand_repl_aliases_with_state,
    repl_help_text,
    session_state_dir,
)
from mubu_probe import (
    DEFAULT_BACKUP_ROOT,
    DEFAULT_STORAGE_ROOT,
    build_folder_indexes,
    choose_current_daily_document,
    load_document_metas,
    load_folders,
)


REPO_ROOT = Path(__file__).resolve().parents[4]


SAMPLE_DOC_REF = "workspace/reference docs/sample-doc"


SAMPLE_NODE_ID = "node-sample-1"


HAS_LOCAL_DATA = DEFAULT_BACKUP_ROOT.is_dir() and DEFAULT_STORAGE_ROOT.is_dir()


DETECTED_DAILY_FOLDER_REF = detect_daily_folder_ref()


HAS_DAILY_FOLDER = HAS_LOCAL_DATA and DETECTED_DAILY_FOLDER_REF is not None


# fmt: off
__all__ = ['DEFAULT_BACKUP_ROOT', 'DEFAULT_STORAGE_ROOT', 'DETECTED_DAILY_FOLDER_REF', 'HAS_DAILY_FOLDER', 'HAS_LOCAL_DATA', 'Path', 'REPO_ROOT', 'SAMPLE_DOC_REF', 'SAMPLE_NODE_ID', 'build_folder_indexes', 'choose_current_daily_document', 'contextlib', 'dispatch', 'expand_repl_aliases_with_state', 'io', 'load_document_metas', 'load_folders', 'mock', 'os', 'repl_help_text', 'session_state_dir', 'shutil', 'subprocess', 'sys', 'tempfile', 'unittest']  # noqa: E501
# fmt: on
