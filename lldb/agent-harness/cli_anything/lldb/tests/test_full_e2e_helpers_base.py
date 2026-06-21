# ruff: noqa: E501
# ruff: noqa: F403, F405, E501
"""
End-to-end tests for the LLDB CLI harness.

These tests exercise the persistent session behavior added for non-REPL
workflows, plus core debugger operations on a tiny compiled helper program.
"""

from __future__ import annotations
import json
import base64
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path
import pytest

HARNESS_ROOT = str(Path(__file__).resolve().parents[3])
TEST_CORE = os.environ.get("LLDB_TEST_CORE", "").strip()
HELPER_SOURCE = r"""
#include <stdio.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>
static void pause_ms(int ms) { Sleep(ms); }
#else
#include <unistd.h>
static void pause_ms(int ms) { usleep((useconds_t)ms * 1000); }
#endif

char GLOBAL_BUFFER[] = "agent-native-lldb";

struct Pair {
    int left;
    int right;
};

int probe(int a, int b) {
    struct Pair pair = {a, b};
    int total = pair.left + pair.right;
    pause_ms(50);
    return GLOBAL_BUFFER[0] + total;
}

int run_attach_mode(void) {
    pause_ms(4000);
    return 0;
}

int main(int argc, char** argv) {
    if (argc > 1 && strcmp(argv[1], "sleep") == 0) {
        return run_attach_mode();
    }

    int value = probe(2, 40);
    printf("value=%d\n", value);
    fflush(stdout);
    pause_ms(50);
    return 0;
}
"""
try:
    import lldb  # noqa: F401

    HAS_LLDB_MODULE = True
except Exception:
    HAS_LLDB_MODULE = False
skip_no_lldb = pytest.mark.skipif(
    not HAS_LLDB_MODULE, reason="lldb module not importable"
)

__all__ = [
    "HARNESS_ROOT",
    "HAS_LLDB_MODULE",
    "HELPER_SOURCE",
    "Path",
    "TEST_CORE",
    "annotations",
    "base64",
    "json",
    "lldb",
    "os",
    "pytest",
    "queue",
    "re",
    "shutil",
    "skip_no_lldb",
    "subprocess",
    "sys",
    "threading",
]
