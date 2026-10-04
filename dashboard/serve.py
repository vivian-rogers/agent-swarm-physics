"""Serve the lab dashboard on localhost.

    uv run python dashboard/serve.py            # http://127.0.0.1:8765
    uv run python dashboard/serve.py --port 9000

Endpoints: /            the page (dashboard/index.html)
           /api/state   everything the page shows (collect.state(), cached with short TTLs)
           /api/file    read-only view of a repo text file (cards, period READMEs, code); never data/ or secrets
           /api/agent   a subagent's hand-back report (or latest text while running)
Binds to 127.0.0.1 only.
"""
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import collect  # noqa: E402

HERE = Path(__file__).resolve().parent
ALLOWED_SUFFIX = {".md", ".py", ".tex", ".txt", ".json", ".tikz"}
DENIED_PARTS = {"data", ".git", ".venv", "__pycache__"}


def safe_path(rel: str) -> Path | None:
    p = (collect.ROOT / rel).resolve()
    try:
        parts = p.relative_to(collect.ROOT).parts
    except ValueError:
        return None
    if not parts or parts[0] in DENIED_PARTS or p.name.startswith(".env") or p.suffix not in ALLOWED_SUFFIX:
        return None
    return p if p.is_file() else None


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, default=str).encode(), "application/json; charset=utf-8")

    def do_GET(self):  # noqa: N802
        u = urlparse(self.path)
        q = parse_qs(u.query)
        try:
            if u.path in ("/", "/index.html"):
                self._send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
            elif u.path == "/api/state":
                self._json(collect.state())
            elif u.path == "/api/file":
                p = safe_path(q.get("path", [""])[0])
                if p is None:
                    self._json({"error": "not allowed"}, 403)
                else:
                    self._json({"path": str(p.relative_to(collect.ROOT)), "text": p.read_text(errors="replace")})
            elif u.path == "/api/agent":
                self._json(collect.agent_report(q.get("id", [""])[0]))
            else:
                self._json({"error": "not found"}, 404)
        except Exception as e:  # keep serving; show the error in the page
            self._json({"error": f"{type(e).__name__}: {e}"}, 500)

    def log_message(self, fmt, *args):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"lab dashboard: http://127.0.0.1:{args.port}  (Ctrl-C to stop)", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
