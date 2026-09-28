"""The preview server permits its current bundle, not arbitrary outside links."""

import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

from cli_hub.preview import start_static_server


class PreviewHttpBoundaryTests(unittest.TestCase):
    def test_external_symlinks_are_denied_but_current_bundle_is_served(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            session = base / "session"
            bundle = base / "bundle"
            session.mkdir()
            bundle.mkdir()
            (session / "session.json").write_text("{}", encoding="utf-8")
            (bundle / "manifest.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
            outside = base / "private.txt"
            outside.write_text("private marker", encoding="utf-8")
            try:
                (session / "current").symlink_to(bundle, target_is_directory=True)
                (session / "leak.txt").symlink_to(outside)
                (bundle / "leak.txt").symlink_to(outside)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            server, url = start_static_server(str(session))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with urlopen(f"{url}/current/manifest.json") as response:
                    self.assertEqual(json.load(response), {"ok": True})
                for path in ("leak.txt", "current/leak.txt"):
                    with self.subTest(path=path):
                        with self.assertRaises(HTTPError) as error:
                            urlopen(f"{url}/{path}")
                        self.assertEqual(error.exception.code, 403)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
