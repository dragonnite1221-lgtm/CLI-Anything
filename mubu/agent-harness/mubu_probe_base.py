# ruff: noqa: E501
#!/usr/bin/env python3

from __future__ import annotations

import argparse
import copy
import gzip
import html
import json
import os
import re
import secrets
import string
import sys
from datetime import datetime, timezone
from json import JSONDecoder
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

__all__ = ['Any', 'HTTPError', 'Iterable', 'JSONDecoder', 'Mapping', 'Path', 'Request', 'URLError', 'annotations', 'argparse', 'copy', 'datetime', 'gzip', 'html', 'json', 'os', 're', 'secrets', 'string', 'sys', 'timezone', 'urlopen']
