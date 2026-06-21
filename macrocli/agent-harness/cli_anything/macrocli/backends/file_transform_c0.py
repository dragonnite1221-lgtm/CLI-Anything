# ruff: noqa: F403, F405, E501
from .file_transform_base import *  # noqa: F403


class FileTransformBackendMixin0:
    """Transform project files without invoking the target application."""
    name = "file_transform"
    priority = 70
    def execute(self, step: MacroStep, params: dict, context: BackendContext) -> StepResult:
        t0 = time.time()
        action = step.action
        step_params = substitute(step.params, params)

        if context.dry_run:
            return StepResult(
                success=True,
                output={"dry_run": True, "action": action},
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        dispatch = {
            "json_get": self._json_get,
            "json_set": self._json_set,
            "json_delete": self._json_delete,
            "xml_set_attr": self._xml_set_attr,
            "xml_get_attr": self._xml_get_attr,
            "text_replace": self._text_replace,
            "copy_file": self._copy_file,
        }

        handler = dispatch.get(action)
        if handler is None:
            return StepResult(
                success=False,
                error=f"FileTransformBackend: unknown action '{action}'.",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        try:
            output = handler(step_params)
            return StepResult(
                success=True,
                output=output or {},
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )
        except Exception as exc:
            return StepResult(
                success=False,
                error=f"FileTransformBackend.{action}: {exc}",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )
    def _json_get(self, p: dict) -> dict:
        """Read a value from a JSON file by dot-path."""
        data = self._load_json(p["input_file"])
        val = self._dotpath_get(data, p["path"])
        return {"value": val, "path": p["path"]}
    def _json_set(self, p: dict) -> dict:
        """Set a value in a JSON file by dot-path and write it back."""
        path = p.get("path", "")
        value = p["value"]
        data = self._load_json(p["input_file"]) if Path(p["input_file"]).is_file() else {}
        self._dotpath_set(data, path, value)
        self._save_json(p.get("output_file", p["input_file"]), data)
        return {"path": path, "value": value}
    def _json_delete(self, p: dict) -> dict:
        """Delete a key from a JSON file by dot-path."""
        data = self._load_json(p["input_file"])
        self._dotpath_delete(data, p["path"])
        self._save_json(p.get("output_file", p["input_file"]), data)
        return {"deleted": p["path"]}
    def _xml_set_attr(self, p: dict) -> dict:
        """Set an XML element attribute matched by XPath."""
        from xml.etree import ElementTree as ET
        tree = ET.parse(p["input_file"])
        root = tree.getroot()
        elements = root.findall(p["xpath"])
        if not elements:
            raise ValueError(f"XPath matched nothing: {p['xpath']}")
        for el in elements:
            el.set(p["attr"], str(p["value"]))
        tree.write(p.get("output_file", p["input_file"]), encoding="unicode", xml_declaration=True)
        return {"matched": len(elements), "attr": p["attr"]}
    def _xml_get_attr(self, p: dict) -> dict:
        """Get an XML element attribute matched by XPath."""
        from xml.etree import ElementTree as ET
        tree = ET.parse(p["input_file"])
        root = tree.getroot()
        elements = root.findall(p["xpath"])
        values = [el.get(p["attr"]) for el in elements]
        return {"values": values, "attr": p["attr"]}
