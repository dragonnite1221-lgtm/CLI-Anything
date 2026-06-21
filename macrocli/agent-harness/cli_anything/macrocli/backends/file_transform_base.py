# ruff: noqa: F403, F405, E501
"""FileTransformBackend — read, transform, and write project files.

Supports XML (ElementTree), JSON, and plain text transformations.

Example macro step:

    - backend: file_transform
      action: json_set
      params:
        input_file: ${project_file}
        output_file: ${project_file}
        path: settings.grid_size
        value: 20

    - backend: file_transform
      action: xml_set_attr
      params:
        input_file: diagram.drawio
        output_file: diagram.drawio
        xpath: .//mxCell[@id='1']
        attr: style
        value: rounded=1;

    - backend: file_transform
      action: text_replace
      params:
        input_file: config.ini
        output_file: config.ini
        find: "theme=default"
        replace: "theme=dark"
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path
from cli_anything.macrocli.backends.base import Backend, BackendContext, StepResult
from cli_anything.macrocli.core.macro_model import MacroStep, substitute


# fmt: off
__all__ = ['Backend', 'BackendContext', 'MacroStep', 'Path', 'StepResult', 'annotations', 'json', 'os', 'substitute', 'time']  # noqa: E501
# fmt: on
