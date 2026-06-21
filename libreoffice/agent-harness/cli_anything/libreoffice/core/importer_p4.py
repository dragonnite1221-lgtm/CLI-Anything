# ruff: noqa: F403, F405, E402, F401, E501
from .importer_base import *
from .importer_p1 import ODF_EXTENSION_TYPES, OFFICE_EXTENSION_CONVERSIONS, SUPPORTED_IMPORT_EXTENSIONS, _apply_metadata, _doc_type_from_mimetype
from .importer_p2 import _parse_writer_content
from .importer_p3 import _parse_calc_content, _parse_impress_content

from . import importer_base as _coupbase  # noqa: E402
def import_odf(path: str, doc_type: Optional[str]=None, name: Optional[str]=None) -> Dict[str, Any]:
    """Import an ODF file into a CLI project dict."""
    try:
        parsed = parse_odf(path)
    except zipfile.BadZipFile as e:
        raise ValueError(f'Invalid ODF file: {path}') from e
    inferred_type = doc_type or _doc_type_from_mimetype(parsed.get('mimetype', ''))
    if inferred_type not in ('writer', 'calc', 'impress'):
        raise ValueError(f'Unsupported ODF document type: {inferred_type}')
    project_name = name or os.path.splitext(os.path.basename(path))[0]
    project = create_document(doc_type=inferred_type, name=project_name)
    _apply_metadata(project, parsed.get('meta_xml', ''), path)
    content_xml = parsed.get('content_xml')
    if not content_xml:
        return project
    try:
        root = ET.fromstring(content_xml)
    except ET.ParseError as e:
        raise ValueError(f'Invalid ODF content.xml in: {path}') from e
    if inferred_type == 'writer':
        project['content'] = _parse_writer_content(root)
    elif inferred_type == 'calc':
        project['sheets'] = _parse_calc_content(root)
        if not project['sheets']:
            project['sheets'] = [{'name': 'Sheet1', 'cells': {}}]
    elif inferred_type == 'impress':
        project['slides'] = _parse_impress_content(root)
    return project

def import_document(path: str, name: Optional[str]=None) -> Dict[str, Any]:
    """Import an existing Office/ODF file into a CLI project dict.

    ODF files are parsed directly. Microsoft Office, legacy Office, CSV, RTF,
    HTML, and text inputs are first converted to ODF with LibreOffice headless,
    then parsed into the harness state model.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f'Document file not found: {path}')
    ext = os.path.splitext(path)[1].lower()
    if ext in ODF_EXTENSION_TYPES:
        doc_type = ODF_EXTENSION_TYPES[ext]
        project = import_odf(path, doc_type=doc_type, name=name)
        project['metadata']['import_method'] = 'native-odf'
        return project
    if ext not in OFFICE_EXTENSION_CONVERSIONS:
        raise ValueError(f"Unsupported import format: {ext or '(none)'}. Supported: {', '.join(SUPPORTED_IMPORT_EXTENSIONS)}")
    doc_type, odf_format = OFFICE_EXTENSION_CONVERSIONS[ext]
    with tempfile.TemporaryDirectory() as tmpdir:
        odf_path = _coupbase._COUP_GLOBALS['convert'](path, odf_format, output_dir=tmpdir)
        project = import_odf(odf_path, doc_type=doc_type, name=name)
    project['metadata']['import_method'] = 'libreoffice-headless'
    project['metadata']['original_format'] = ext.lstrip('.')
    project['metadata']['source_path'] = os.path.abspath(path)
    return project
