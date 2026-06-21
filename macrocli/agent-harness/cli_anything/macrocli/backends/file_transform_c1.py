# ruff: noqa: F403, F405, E501
from .file_transform_base import *  # noqa: F403


class FileTransformBackendMixin1:
    def _text_replace(self, p: dict) -> dict:
        """Simple find-and-replace in a text file."""
        content = Path(p["input_file"]).read_text(encoding="utf-8")
        count = content.count(p["find"])
        content = content.replace(p["find"], p["replace"])
        out = p.get("output_file", p["input_file"])
        Path(out).write_text(content, encoding="utf-8")
        return {"replacements": count}
    def _copy_file(self, p: dict) -> dict:
        """Copy a file from src to dst."""
        import shutil
        shutil.copy2(p["src"], p["dst"])
        size = os.path.getsize(p["dst"])
        return {"src": p["src"], "dst": p["dst"], "size": size}
    def _load_json(self, path: str) -> dict:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    def _save_json(self, path: str, data: dict) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    def _dotpath_get(self, data: dict, path: str):
        keys = path.split(".")
        cur = data
        for k in keys:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                return None
        return cur
    def _dotpath_set(self, data: dict, path: str, value) -> None:
        keys = path.split(".")
        cur = data
        for k in keys[:-1]:
            if k not in cur or not isinstance(cur[k], dict):
                cur[k] = {}
            cur = cur[k]
        cur[keys[-1]] = value
    def _dotpath_delete(self, data: dict, path: str) -> None:
        keys = path.split(".")
        cur = data
        for k in keys[:-1]:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                return
        if isinstance(cur, dict) and keys[-1] in cur:
            del cur[keys[-1]]
