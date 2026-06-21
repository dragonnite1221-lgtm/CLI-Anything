# ruff: noqa: F403, F405, E501
from .odf_utils_base import *  # noqa: F403


def parse_odf(path: str) -> Dict[str, Any]:
    """Parse an ODF file and return a dict of its XML contents."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"ODF file not found: {path}")

    result = {}
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()
        result["files"] = names

        if "mimetype" in names:
            result["mimetype"] = zf.read("mimetype").decode("utf-8")

        if "content.xml" in names:
            result["content_xml"] = zf.read("content.xml").decode("utf-8")

        if "styles.xml" in names:
            result["styles_xml"] = zf.read("styles.xml").decode("utf-8")

        if "meta.xml" in names:
            result["meta_xml"] = zf.read("meta.xml").decode("utf-8")

        if "META-INF/manifest.xml" in names:
            result["manifest_xml"] = zf.read("META-INF/manifest.xml").decode("utf-8")

    return result


def validate_odf(path: str) -> Dict[str, Any]:
    """Validate an ODF file structure."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    errors = []
    warnings = []
    names = []

    try:
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()

            # Check mimetype
            if "mimetype" not in names:
                errors.append("Missing 'mimetype' entry")
            else:
                # Check mimetype is first entry
                if names[0] != "mimetype":
                    warnings.append("'mimetype' is not the first entry in ZIP")

                # Check mimetype is stored uncompressed
                info = zf.getinfo("mimetype")
                if info.compress_type != zipfile.ZIP_STORED:
                    warnings.append("'mimetype' entry is compressed (should be stored)")

                mimetype = zf.read("mimetype").decode("utf-8")
                if mimetype not in ODF_MIMETYPES.values():
                    warnings.append(f"Unknown mimetype: {mimetype}")

            # Check required files
            for required in ["content.xml", "META-INF/manifest.xml"]:
                if required not in names:
                    errors.append(f"Missing required file: {required}")

            # Validate XML in content.xml
            if "content.xml" in names:
                try:
                    ET.fromstring(zf.read("content.xml"))
                except ET.ParseError as e:
                    errors.append(f"Invalid XML in content.xml: {e}")

            # Validate XML in styles.xml
            if "styles.xml" in names:
                try:
                    ET.fromstring(zf.read("styles.xml"))
                except ET.ParseError as e:
                    errors.append(f"Invalid XML in styles.xml: {e}")

            # Validate XML in meta.xml
            if "meta.xml" in names:
                try:
                    ET.fromstring(zf.read("meta.xml"))
                except ET.ParseError as e:
                    errors.append(f"Invalid XML in meta.xml: {e}")

    except zipfile.BadZipFile:
        errors.append("Not a valid ZIP file")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "file_count": len(names) if not errors else 0,
    }
