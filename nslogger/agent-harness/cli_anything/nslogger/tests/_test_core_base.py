# ruff: noqa: F403, F405, E501
"""Unit tests for NSLogger CLI core modules (no external deps, synthetic data)."""
import io
import json
import struct
import tempfile
import os
import time
from datetime import datetime, timezone
from unittest.mock import patch
import pytest
from click.testing import CliRunner
import cli_anything.nslogger.nslogger_cli as nslogger_cli
from cli_anything.nslogger.core.message import (
    LogMessage, MSG_TYPE_LOG, MSG_TYPE_CLIENT_INFO, MSG_TYPE_BLOCK_START, MSG_TYPE_BLOCK_END,
    LEVEL_NAMES,
)
from cli_anything.nslogger.core.filter import filter_messages
from cli_anything.nslogger.core.stats import compute_stats
from cli_anything.nslogger.core.exporter import export_text, export_json, export_csv, export_messages
from cli_anything.nslogger.core.blocks import iter_block_tree, extract_clients, merge_files
from cli_anything.nslogger.core.listener import (
    NSLoggerListener, _bonjour_service_types, _dns_sd_txt_args, _looks_like_tls_client_hello,
    _classify_connection, _swift_helper_env,
)
from cli_anything.nslogger.nslogger_cli import (
    _format_live_output_message,
    _listen_waiting_message,
    _open_live_output_file,
)
from cli_anything.nslogger.utils.generate import encode_message, generate_sample_file
from cli_anything.nslogger.core.parser import _parse_message, parse_raw_file


# fmt: off
__all__ = ['CliRunner', 'LEVEL_NAMES', 'LogMessage', 'MSG_TYPE_BLOCK_END', 'MSG_TYPE_BLOCK_START', 'MSG_TYPE_CLIENT_INFO', 'MSG_TYPE_LOG', 'NSLoggerListener', '_bonjour_service_types', '_classify_connection', '_dns_sd_txt_args', '_format_live_output_message', '_listen_waiting_message', '_looks_like_tls_client_hello', '_open_live_output_file', '_parse_message', '_swift_helper_env', 'compute_stats', 'datetime', 'encode_message', 'export_csv', 'export_json', 'export_messages', 'export_text', 'extract_clients', 'filter_messages', 'generate_sample_file', 'io', 'iter_block_tree', 'json', 'merge_files', 'nslogger_cli', 'os', 'parse_raw_file', 'patch', 'pytest', 'struct', 'tempfile', 'time', 'timezone']  # noqa: E501
# fmt: on
