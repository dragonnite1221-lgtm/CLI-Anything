# ruff: noqa: F403, F405, E501
"""Core function contract tests for mubu_probe.

Pure logic tests — no I/O, no network, no live Mubu API.
Covers utility and transformation functions not already exercised by test_mubu_probe.py.
"""
import json
import tempfile
import unittest
from pathlib import Path
from mubu_probe import (
    ambiguous_error_message,
    build_folder_indexes,
    candidate_appdata_roots,
    dedupe_latest_records,
    default_mubu_data_root,
    enrich_document_meta,
    extract_plain_text,
    generate_node_id,
    infer_title,
    iter_nodes,
    looks_like_daily_title,
    maybe_plain_text_to_html,
    node_path_to_api_path,
    normalize_document_meta_record,
    normalize_folder_record,
    normalized_lookup_key,
    numeric_values,
    parse_child_refs,
    parse_event_timestamp_ms,
    parse_revision_generation,
    plain_text_to_html,
    resolve_node_at_path,
    rich_text_to_html,
    serialize_node,
    timestamp_ms_to_iso,
)


# fmt: off
__all__ = ['Path', 'ambiguous_error_message', 'build_folder_indexes', 'candidate_appdata_roots', 'dedupe_latest_records', 'default_mubu_data_root', 'enrich_document_meta', 'extract_plain_text', 'generate_node_id', 'infer_title', 'iter_nodes', 'json', 'looks_like_daily_title', 'maybe_plain_text_to_html', 'node_path_to_api_path', 'normalize_document_meta_record', 'normalize_folder_record', 'normalized_lookup_key', 'numeric_values', 'parse_child_refs', 'parse_event_timestamp_ms', 'parse_revision_generation', 'plain_text_to_html', 'resolve_node_at_path', 'rich_text_to_html', 'serialize_node', 'tempfile', 'timestamp_ms_to_iso', 'unittest']  # noqa: E501
# fmt: on
