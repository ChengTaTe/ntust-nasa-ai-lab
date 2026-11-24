"""Standard-library local HTTP server for FD001 Health Analytics."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from web.api import FD001API


STATIC_ROOT = Path(__file__).resolve().parent / "static"
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


def make_handler(api: FD001API):
    class FD001Handler(BaseHTTPRequestHandler):
        server_version = "FD001Local/1.0"

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'")
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
                # Browser-side AbortController intentionally cancels stale requests.
                pass

        def _json(self, status: int, payload: dict) -> None:
            try:
                body = json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
            except (TypeError, ValueError):
                status = 500
                body = b'{"ok":false,"data":null,"error":{"code":"INTERNAL_ERROR","message":"Response serialization failed."}}'
            self._send(status, body, "application/json; charset=utf-8")

        def do_GET(self) -> None:  # noqa: N802
            target = urlsplit(self.path)
            if target.path.startswith("/api/"):
                try:
                    params = parse_qs(target.query, keep_blank_values=True, strict_parsing=True)
                except ValueError:
                    self._json(400, {"ok": False, "data": None, "error": {"code": "INVALID_REQUEST", "message": "Malformed query string."}})
                    return
                status, payload = api.handle(target.path, params)
                self._json(status, payload)
                return
            static = STATIC_FILES.get(target.path)
            if target.path == "/favicon.ico" and not target.query:
                self._send(200, b"", "image/x-icon")
                return
            if static is None or target.query:
                self._json(404, {"ok": False, "data": None, "error": {"code": "NOT_FOUND", "message": "Resource not found."}})
                return
            filename, content_type = static
            self._send(200, (STATIC_ROOT / filename).read_bytes(), content_type)

        def _method_not_allowed(self) -> None:
            self._json(405, {"ok": False, "data": None, "error": {"code": "METHOD_NOT_ALLOWED", "message": "Only GET is supported."}})

        do_POST = do_PUT = do_PATCH = do_DELETE = _method_not_allowed

        def log_message(self, format: str, *args) -> None:
            print(f"{self.address_string()} - {format % args}")

    return FD001Handler


def create_server(host: str = "127.0.0.1", port: int = 8000, project_root: Path | str | None = None) -> ThreadingHTTPServer:
    if host != "127.0.0.1":
        raise ValueError("The FD001 server may bind only to 127.0.0.1.")
    api = FD001API(project_root)
    return ThreadingHTTPServer((host, port), make_handler(api))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local FD001 Health Analytics website.")
    parser.add_argument("--host", default="127.0.0.1", choices=["127.0.0.1"])
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()
    server = create_server(args.host, args.port)
    print(f"FD001 Health Analytics: http://{args.host}:{server.server_port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
