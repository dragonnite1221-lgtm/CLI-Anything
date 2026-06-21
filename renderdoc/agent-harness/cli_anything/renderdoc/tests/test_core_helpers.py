# ruff: noqa: F403, F405, E501
"""
Unit tests for RenderDoc CLI core modules.

These tests use mocks and synthetic data — no renderdoc dependency needed.
Run with: pytest test_core.py -v
"""

from __future__ import annotations
import json
import os
import struct
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
import pytest


class MockActionFlags:
    Clear = 0x0001
    Drawcall = 0x0002
    Dispatch = 0x0004
    CmdList = 0x0008
    SetMarker = 0x0010
    PushMarker = 0x0020
    PopMarker = 0x0040
    Present = 0x0080
    MultiAction = 0x0100
    Copy = 0x0200
    Resolve = 0x0400
    GenMips = 0x0800
    PassBoundary = 0x1000
    Indexed = 0x2000
    Instanced = 0x4000
    Auto = 0x8000
    Indirect = 0x10000
    ClearColor = 0x20000
    ClearDepthStencil = 0x40000
    BeginPass = 0x80000
    EndPass = 0x100000


def _make_mock_action(event_id, name, flags=0x0002, num_indices=100, children=None):
    action = MagicMock()
    action.eventId = event_id
    action.actionId = event_id
    action.customName = name
    action.GetName = MagicMock(return_value=name)
    action.flags = flags
    action.numIndices = num_indices
    action.numInstances = 1
    action.indexOffset = 0
    action.baseVertex = 0
    action.vertexOffset = 0
    action.instanceOffset = 0
    action.outputs = []
    action.depthOut = MagicMock()
    action.depthOut.__str__ = lambda s: "0"
    action.children = children or []
    action.next = None
    return action


__all__ = [
    "MagicMock",
    "MockActionFlags",
    "Path",
    "PropertyMock",
    "_make_mock_action",
    "annotations",
    "json",
    "os",
    "patch",
    "pytest",
    "struct",
    "sys",
]
