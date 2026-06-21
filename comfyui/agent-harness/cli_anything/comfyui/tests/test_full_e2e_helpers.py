# ruff: noqa: F403, F405, E501
"""Full end-to-end tests for ComfyUI CLI harness.

These tests simulate a complete generation workflow using mocked HTTP responses.
They do NOT require ComfyUI to be installed or running.

Run with:
    python -m pytest comfyui/tests/test_full_e2e.py -v
"""

import json
from pathlib import Path
from unittest.mock import patch
import pytest
from click.testing import CliRunner
from cli_anything.comfyui.comfyui_cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_workflow():
    return {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "v1-5-pruned-emaonly.ckpt"},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "a beautiful landscape", "clip": ["4", 1]},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "ugly, bad", "clip": ["4", 1]},
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
                "seed": 12345,
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
    p = tmp_path / "landscape.json"
    p.write_text(json.dumps(sample_workflow))
    return str(p)


__all__ = [
    "CliRunner",
    "Path",
    "cli",
    "json",
    "patch",
    "pytest",
    "runner",
    "sample_workflow",
    "workflow_file",
]
