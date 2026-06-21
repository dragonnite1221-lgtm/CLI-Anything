# ruff: noqa: F403, F405, E501
"""Unit tests for ComfyUI CLI harness — no ComfyUI installation required.

Tests cover:
- Workflow load/save/list/validate
- Queue operations (prompt, status, clear, history, interrupt)
- Model listing (checkpoints, LoRAs, VAEs, ControlNets, node info)
- Image listing and downloading
- CLI command parsing and output
- Error handling and edge cases

Run with:
    python -m pytest comfyui/tests/test_core.py
    python -m pytest comfyui/tests/test_core.py -v
"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from click.testing import CliRunner
from cli_anything.comfyui.comfyui_cli import cli
from cli_anything.comfyui.core import workflows as workflow_mod
from cli_anything.comfyui.core import queue as queue_mod
from cli_anything.comfyui.core import models as models_mod
from cli_anything.comfyui.core import images as images_mod


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_workflow():
    """Minimal valid ComfyUI workflow (API format)."""
    return {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "v1-5-pruned-emaonly.ckpt"},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "a photo of a cat", "clip": ["4", 1]},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "bad quality", "clip": ["4", 1]},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": 512, "width": 512},
        },
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 7,
                "denoise": 1,
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "latent_image": ["5", 0],
                "sampler_name": "euler",
                "scheduler": "normal",
                "seed": 42,
                "steps": 20,
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "ComfyUI", "images": ["8", 0]},
        },
    }


@pytest.fixture
def workflow_file(tmp_path, sample_workflow):
    """Write sample workflow to a temp file and return the path."""
    p = tmp_path / "test_workflow.json"
    p.write_text(json.dumps(sample_workflow))
    return str(p)


__all__ = [
    "CliRunner",
    "MagicMock",
    "Path",
    "cli",
    "images_mod",
    "json",
    "models_mod",
    "patch",
    "pytest",
    "queue_mod",
    "runner",
    "sample_workflow",
    "workflow_file",
    "workflow_mod",
]
