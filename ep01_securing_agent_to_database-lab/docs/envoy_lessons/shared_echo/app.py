"""Minimal HTTP echo server for Envoy lessons (prints received headers as JSON)."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class EchoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self._respond()

    def do_POST(self) -> None:
        self._respond()

    def _respond(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="replace") if length else ""
        payload = {
            "method": self.command,
            "path": self.path,
            "headers_received": {k.lower(): v for k, v in self.headers.items()},
            "body": body,
        }
        raw = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, format: str, *args) -> None:
        return


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), EchoHandler).serve_forever()
