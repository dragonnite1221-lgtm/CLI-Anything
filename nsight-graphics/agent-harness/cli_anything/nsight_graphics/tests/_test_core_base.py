# ruff: noqa: F403, F405, E501
"""Unit tests for cli-anything-nsight-graphics."""
from __future__ import annotations
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
import pytest
from cli_anything.nsight_graphics.core import cpp_capture, frame, gpu_trace, launch, replay
from cli_anything.nsight_graphics.utils import nsight_graphics_backend as backend
from cli_anything.nsight_graphics.utils.errors import handle_error
from cli_anything.nsight_graphics.utils.output import output_json


SAMPLE_HELP = """
NVIDIA Nsight Graphics [general_options] [activity_options]:

General Options:
  --hostname arg                        Host name of remote connection
  --project arg                         Nsight project file to load
  --output-dir arg                      Output folder to export/write data to
  --activity arg                        Target activity to use, should be one of:
                                          Graphics Capture
                                          OpenGL Frame Debugger
                                          Generate C++ Capture
                                          GPU Trace Profiler
  --platform arg                        Target platform to use, should be one of:
                                          Windows
  --launch-detached                     Run as a command line launcher
  --attach-pid arg                      PID to connect to
  --exe arg                             Executable path to be launched with the tool injected
  --dir arg                             Working directory of launched application
  --args arg                            Command-line arguments of launched application
  --env arg                             Environment variables of launched application

Graphics Capture activity options:
  --frame-count arg                     Capture N frames
  --hotkey-capture                      Wait for hotkey
  --frame-index arg                     Capture frame index
  --elapsed-time arg                    Wait in time (seconds) before capturing

OpenGL Frame Debugger activity options:
  --wait-frames arg                     Wait in frames before capturing a frame
  --wait-seconds arg                    Wait in time (seconds) before capturing a frame
  --wait-hotkey                         Wait for hotkey
  --export-frame-perf-metrics           Export metrics

Generate C++ Capture activity options:
  --wait-seconds arg                    Wait in time (seconds) before capturing a frame
  --wait-hotkey                         Wait for hotkey

GPU Trace Profiler activity options:
  --start-after-frames arg              Wait N frames before generating GPU trace
  --start-after-ms arg                  Wait N milliseconds before generating GPU trace
  --limit-to-frames arg                 Trace a maximum of N frames
  --auto-export                         Automatically export metrics data after generating GPU trace
  --architecture arg                    Selects which architecture the options configure
  --metric-set-id arg                   Metric set id
  --multi-pass-metrics                  Enable multi-pass metrics
  --real-time-shader-profiler           Enable shader profiler
"""


# fmt: off
__all__ = ['Path', 'SAMPLE_HELP', 'annotations', 'backend', 'cpp_capture', 'frame', 'gpu_trace', 'handle_error', 'io', 'json', 'launch', 'os', 'output_json', 'patch', 'pytest', 'replay', 'subprocess', 'sys']  # noqa: E501
# fmt: on
