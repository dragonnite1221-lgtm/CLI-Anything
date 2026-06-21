# ruff: noqa: F403, F405, E501
from .odf_utils_base import *  # noqa: F403

# fmt: off
from .odf_utils_p1 import _ns, _nsattr, _register_namespaces  # noqa: E402,E501
from .odf_utils_p4 import _xml_to_string  # noqa: E402,E501
from .odf_utils_p5 import create_content_xml, create_styles_xml  # noqa: E402,E501
# fmt: on


def create_meta_xml(project: Dict[str, Any]) -> str:
    """Create meta.xml for an ODF document."""
    _register_namespaces()

    root = ET.Element(_ns("office", "document-meta"))
    root.set(_nsattr("office", "version"), "1.2")

    meta = ET.SubElement(root, _ns("office", "meta"))
    metadata = project.get("metadata", {})

    # Title
    title = ET.SubElement(meta, _ns("dc", "title"))
    title.text = metadata.get("title", project.get("name", ""))

    # Author / creator
    creator = ET.SubElement(meta, _ns("meta", "initial-creator"))
    creator.text = metadata.get("author", "libreoffice-cli")

    # Description
    desc = ET.SubElement(meta, _ns("dc", "description"))
    desc.text = metadata.get("description", "")

    # Subject
    subject = ET.SubElement(meta, _ns("dc", "subject"))
    subject.text = metadata.get("subject", "")

    # Creation date
    creation = ET.SubElement(meta, _ns("meta", "creation-date"))
    creation.text = metadata.get("created", datetime.now().isoformat())

    # Generator
    gen = ET.SubElement(meta, _ns("meta", "generator"))
    gen.text = "libreoffice-cli/1.0"

    return _xml_to_string(root)


def create_manifest_xml(doc_type: str) -> str:
    """Create META-INF/manifest.xml."""
    _register_namespaces()

    root = ET.Element(_ns("manifest", "manifest"))
    # Namespace is set automatically by _register_namespaces()
    root.set(_nsattr("manifest", "version"), "1.2")

    mimetype = ODF_MIMETYPES.get(doc_type, ODF_MIMETYPES["writer"])

    # Root entry
    entry = ET.SubElement(root, _ns("manifest", "file-entry"))
    entry.set(_nsattr("manifest", "full-path"), "/")
    entry.set(_nsattr("manifest", "version"), "1.2")
    entry.set(_nsattr("manifest", "media-type"), mimetype)

    # content.xml
    entry = ET.SubElement(root, _ns("manifest", "file-entry"))
    entry.set(_nsattr("manifest", "full-path"), "content.xml")
    entry.set(_nsattr("manifest", "media-type"), "text/xml")

    # styles.xml
    entry = ET.SubElement(root, _ns("manifest", "file-entry"))
    entry.set(_nsattr("manifest", "full-path"), "styles.xml")
    entry.set(_nsattr("manifest", "media-type"), "text/xml")

    # meta.xml
    entry = ET.SubElement(root, _ns("manifest", "file-entry"))
    entry.set(_nsattr("manifest", "full-path"), "meta.xml")
    entry.set(_nsattr("manifest", "media-type"), "text/xml")

    return _xml_to_string(root)


def write_odf(path: str, doc_type: str, project: Dict[str, Any]) -> str:
    """Write a complete ODF file (ZIP archive) from a project dict.

    The mimetype entry must be stored uncompressed as the first entry
    in the ZIP (ODF specification requirement).
    """
    mimetype = ODF_MIMETYPES.get(doc_type, ODF_MIMETYPES["writer"])
    content_xml = create_content_xml(doc_type, project)
    styles_xml = create_styles_xml(doc_type, project)
    meta_xml = create_meta_xml(project)
    manifest_xml = create_manifest_xml(doc_type)

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        # mimetype MUST be first and MUST be stored uncompressed
        zf.writestr(
            zipfile.ZipInfo("mimetype", date_time=(2024, 1, 1, 0, 0, 0)),
            mimetype,
            compress_type=zipfile.ZIP_STORED,
        )
        zf.writestr("content.xml", content_xml)
        zf.writestr("styles.xml", styles_xml)
        zf.writestr("meta.xml", meta_xml)
        zf.writestr("META-INF/manifest.xml", manifest_xml)

    return os.path.abspath(path)
