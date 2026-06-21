# ruff: noqa: F403, F405, E501
from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import unittest
import uuid
from pathlib import Path
from cli_anything.zotero.core import discovery
from cli_anything.zotero.tests._helpers import sample_pdf_bytes
from cli_anything.zotero.utils import zotero_paths, zotero_sqlite


REPO_ROOT = Path(__file__).resolve().parents[4]


ENVIRONMENT = zotero_paths.build_environment()


HAS_LOCAL_DATA = ENVIRONMENT.sqlite_exists


SAMPLE_ITEM = choose_regular_item()


ATTACHMENT_SAMPLE_ITEM = choose_item_with_attachment()


NOTE_SAMPLE_ITEM = choose_item_with_note()


SAMPLE_COLLECTION = choose_collection()


SAMPLE_TAG = choose_tag_name()


SEARCHES = zotero_sqlite.fetch_saved_searches(ENVIRONMENT.sqlite_path, library_id=zotero_sqlite.default_library_id(ENVIRONMENT.sqlite_path)) if HAS_LOCAL_DATA else []


SAMPLE_SEARCH = SEARCHES[0] if SEARCHES else None


# fmt: off
__all__ = ['ATTACHMENT_SAMPLE_ITEM', 'ENVIRONMENT', 'HAS_LOCAL_DATA', 'NOTE_SAMPLE_ITEM', 'Path', 'REPO_ROOT', 'SAMPLE_COLLECTION', 'SAMPLE_ITEM', 'SAMPLE_SEARCH', 'SAMPLE_TAG', 'SEARCHES', 'annotations', 'discovery', 'json', 'os', 'sample_pdf_bytes', 'shutil', 'subprocess', 'sys', 'sysconfig', 'tempfile', 'unittest', 'uuid', 'zotero_paths', 'zotero_sqlite']  # noqa: E501
# fmt: on
