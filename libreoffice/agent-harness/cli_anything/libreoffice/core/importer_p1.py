# ruff: noqa: F403, F405, E501
from .importer_base import *  # noqa: F403


ODF_EXTENSION_TYPES = {
    ".odt": "writer",
    ".ott": "writer",
    ".ods": "calc",
    ".ots": "calc",
    ".odp": "impress",
    ".otp": "impress",
}
OFFICE_EXTENSION_CONVERSIONS = {
    ".doc": ("writer", "odt"),
    ".docx": ("writer", "odt"),
    ".docm": ("writer", "odt"),
    ".rtf": ("writer", "odt"),
    ".txt": ("writer", "odt"),
    ".html": ("writer", "odt"),
    ".htm": ("writer", "odt"),
    ".xls": ("calc", "ods"),
    ".xlsx": ("calc", "ods"),
    ".xlsm": ("calc", "ods"),
    ".csv": ("calc", "ods"),
    ".ppt": ("impress", "odp"),
    ".pptx": ("impress", "odp"),
    ".pptm": ("impress", "odp"),
}
SUPPORTED_IMPORT_EXTENSIONS = tuple(
    sorted(set(ODF_EXTENSION_TYPES) | set(OFFICE_EXTENSION_CONVERSIONS))
)
def can_import(path: str) -> bool:
    """Return True if the path extension is supported by the import pipeline."""
    return os.path.splitext(path)[1].lower() in SUPPORTED_IMPORT_EXTENSIONS
def list_import_formats() -> List[Dict[str, str]]:
    """List importable document extensions."""
    formats = []
    for ext, doc_type in sorted(ODF_EXTENSION_TYPES.items()):
        formats.append({
            "extension": ext,
            "type": doc_type,
            "method": "native-odf",
        })
    for ext, (doc_type, odf_format) in sorted(OFFICE_EXTENSION_CONVERSIONS.items()):
        formats.append({
            "extension": ext,
            "type": doc_type,
            "method": "libreoffice-headless",
            "intermediate": odf_format,
        })
    return formats
def _doc_type_from_mimetype(mimetype: str) -> str:
    for doc_type, expected in ODF_MIMETYPES.items():
        if mimetype == expected:
            return doc_type
    raise ValueError(f"Unsupported or missing ODF mimetype: {mimetype}")
def _q(prefix: str, local: str) -> str:
    return f"{{{ODF_NS[prefix]}}}{local}"
def _apply_metadata(project: Dict[str, Any], meta_xml: str, source_path: str) -> None:
    metadata = project.setdefault("metadata", {})
    metadata.update({
        "source_path": os.path.abspath(source_path),
        "imported_at": datetime.now().isoformat(),
    })
    if not meta_xml:
        return

    try:
        root = ET.fromstring(meta_xml)
    except ET.ParseError as e:
        raise ValueError(f"Invalid ODF meta.xml in: {source_path}") from e

    mappings = {
        "title": ("dc", "title"),
        "author": ("dc", "creator"),
        "description": ("dc", "description"),
        "subject": ("dc", "subject"),
        "created": ("meta", "creation-date"),
        "modified": ("dc", "date"),
    }
    for key, (prefix, local) in mappings.items():
        elem = root.find(f".//{_q(prefix, local)}")
        if elem is not None and elem.text:
            metadata[key] = elem.text
def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag
def _children_by_local(elem: ET.Element, local_name: str) -> List[ET.Element]:
    return [child for child in list(elem) if _local_name(child.tag) == local_name]
def _text_content(elem: ET.Element) -> str:
    return "".join(elem.itertext()).strip()
def _parse_list_items(list_elem: ET.Element) -> List[str]:
    items = []
    for item_elem in _children_by_local(list_elem, "list-item"):
        text = _text_content(item_elem)
        if text:
            items.append(text)
    return items
def _attr(elem: ET.Element, prefix: str, local: str) -> Optional[str]:
    return elem.get(_q(prefix, local))
def _int_attr(elem: ET.Element, prefix: str, local: str, default: int = 1) -> int:
    value = _attr(elem, prefix, local)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default
