# ruff: noqa: F403, F405, E501
from .extract_tools_base import *  # noqa: F403

# fmt: off
from .extract_tools_p4 import _parse_tool_block  # noqa: E402,E501
# fmt: on


def extract_tools(source: str) -> list[dict]:
    """Scan the source for all server.tool(...) invocations and return their schemas."""
    tools: list[dict] = []
    idx = 0
    while True:
        start = source.find("server.tool(", idx)
        if start == -1:
            break
        tool = _parse_tool_block(source, start)
        if tool:
            tools.append(tool)
            idx = tool.pop("_end")
        else:
            idx = start + len("server.tool(")
    return tools


def _extract_pkg_version(index_js_path: Path) -> str:
    """Try to read version from sibling package.json."""
    pkg = index_js_path.parent / "package.json"
    if not pkg.is_file():
        return "unknown"
    try:
        data = json.loads(pkg.read_text())
        return data.get("version", "unknown")
    except Exception:
        return "unknown"


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "Usage: extract_tools.py <path/to/safari-mcp/index.js> [output.json]",
            file=sys.stderr,
        )
        return 2

    index_path = Path(sys.argv[1]).expanduser().resolve()
    if not index_path.is_file():
        print(f"Error: {index_path} not found", file=sys.stderr)
        return 1

    source = index_path.read_text()
    tools = extract_tools(source)

    out = {
        "source_version": _extract_pkg_version(index_path),
        "source_basename": index_path.name,  # no absolute path — privacy
        "tool_count": len(tools),
        "tools": tools,
    }

    if len(sys.argv) >= 3:
        out_path = Path(sys.argv[2]).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
        print(
            f"Extracted {len(tools)} tools from safari-mcp v{out['source_version']}",
            file=sys.stderr,
        )
        print(f"Wrote {out_path}", file=sys.stderr)
    else:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        print(
            f"Extracted {len(tools)} tools from safari-mcp v{out['source_version']}",
            file=sys.stderr,
        )

    return 0
