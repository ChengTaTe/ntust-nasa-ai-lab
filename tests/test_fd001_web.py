from __future__ import annotations

import json
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from web.server import create_server


ROOT = Path(__file__).resolve().parents[1]


class FD001WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_server(port=0, project_root=ROOT)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, path: str, method: str = "GET") -> tuple[int, bytes, dict]:
        request = Request(self.base + path, method=method)
        try:
            with urlopen(request, timeout=10) as response:
                return response.status, response.read(), dict(response.headers)
        except HTTPError as exc:
            try:
                return exc.code, exc.read(), dict(exc.headers)
            finally:
                exc.close()

    def test_static_allowlist_and_security_headers(self) -> None:
        for path, marker in (("/", b"FD001 Health Analytics"), ("/styles.css", b":root"), ("/app.js", b"beginTransition")):
            status, body, headers = self.request(path)
            self.assertEqual(status, 200)
            self.assertIn(marker, body)
            self.assertIn("default-src 'self'", headers["Content-Security-Policy"])
        status, body, _ = self.request("/../AGENTS.md")
        self.assertEqual(status, 404)
        self.assertNotIn(b"AI Team Governance", body)
        status, _, _ = self.request("/%2e%2e/AGENTS.md")
        self.assertEqual(status, 404)

    def test_api_envelope_and_no_private_path(self) -> None:
        status, body, _ = self.request("/api/v1/status")
        self.assertEqual(status, 200)
        payload = json.loads(body)
        self.assertEqual(set(payload), {"ok", "data", "error"})
        self.assertNotIn(str(ROOT).encode(), body)

    def test_method_not_allowed(self) -> None:
        status, body, _ = self.request("/api/v1/status", method="POST")
        self.assertEqual(status, 405)
        self.assertEqual(json.loads(body)["error"]["code"], "METHOD_NOT_ALLOWED")

    def test_malformed_query_and_arbitrary_file_rejected(self) -> None:
        status, body, _ = self.request("/api/v1/units?split")
        self.assertEqual(status, 400)
        self.assertEqual(json.loads(body)["error"]["code"], "INVALID_REQUEST")
        status, _, _ = self.request("/AGENTS.md")
        self.assertEqual(status, 404)

    def test_default_public_binding_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            create_server(host="0.0.0.0", port=0, project_root=ROOT)


if __name__ == "__main__":
    unittest.main()
