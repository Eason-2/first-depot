from __future__ import annotations

import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from apps.api.ai_writer import handle_ai_writer_get, handle_ai_writer_post
from apps.api.blog_view import load_post_by_slug, render_blog_index, render_blog_post
from core.config import Settings
from core.storage import Storage
from workers.publishing.scheduler import AutopublishScheduler


def resolve_client_ip(client_ip: str, header_values: dict[str, str] | None = None) -> str:
    if not header_values:
        return client_ip

    cf_connecting_ip = header_values.get("CF-Connecting-IP", "").strip()
    if cf_connecting_ip:
        return cf_connecting_ip

    forwarded_for = header_values.get("X-Forwarded-For", "").strip()
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()

    real_ip = header_values.get("X-Real-IP", "").strip()
    if real_ip:
        return real_ip

    return client_ip


def is_run_once_authorized(client_ip: str, admin_token: str | None, provided_token: str) -> bool:
    if client_ip in {"127.0.0.1", "::1"}:
        return True
    if not admin_token:
        return False
    return provided_token == admin_token


class _Context:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.storage = Storage(settings.db_path)
        self.scheduler = AutopublishScheduler(settings)
        self.lock = threading.Lock()


class ApiHandler(BaseHTTPRequestHandler):
    context: _Context

    def _json_response(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _html_response(self, status: int, html: str) -> None:
        data = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if handle_ai_writer_get(path, self):
            return

        if path in {"/", "/blog"}:
            html = render_blog_index(self.context.settings.publish_dir)
            self._html_response(HTTPStatus.OK, html)
            return

        if path.startswith("/blog/"):
            slug = path[len("/blog/") :].strip()
            loaded = load_post_by_slug(self.context.settings.publish_dir, slug)
            if not loaded:
                self._html_response(HTTPStatus.NOT_FOUND, "<h1>404</h1><p>Post not found.</p>")
                return
            title, content = loaded
            self._html_response(HTTPStatus.OK, render_blog_post(title, content))
            return

        if path == "/health":
            self._json_response(HTTPStatus.OK, {"status": "ok"})
            return

        if path == "/latest-topics":
            topics = self.context.storage.fetch_latest_clusters(limit=20)
            self._json_response(HTTPStatus.OK, {"count": len(topics), "items": topics})
            return

        if path == "/latest-draft":
            draft = self.context.storage.fetch_latest_draft()
            self._json_response(HTTPStatus.OK, {"item": draft})
            return

        if path == "/last-run":
            path = self.context.settings.runtime_dir / "last_run.json"
            payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"status": "never_run"}
            self._json_response(HTTPStatus.OK, payload)
            return

        self._json_response(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        body_raw = self.rfile.read(content_length) if content_length > 0 else b""

        if handle_ai_writer_post(path, body_raw, self):
            return

        if path != "/run-once":
            self._json_response(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return

        if not self._is_run_once_authorized():
            self._json_response(HTTPStatus.FORBIDDEN, {"error": "forbidden"})
            return

        with self.context.lock:
            result = self.context.scheduler.run_cycle(max_items_per_source=10)
        self._json_response(HTTPStatus.OK, result)

    def _is_run_once_authorized(self) -> bool:
        client_ip = resolve_client_ip(
            client_ip=self.client_address[0],
            header_values={
                "CF-Connecting-IP": self.headers.get("CF-Connecting-IP", ""),
                "X-Forwarded-For": self.headers.get("X-Forwarded-For", ""),
                "X-Real-IP": self.headers.get("X-Real-IP", ""),
            },
        )
        token = self.context.settings.admin_token
        provided = self.headers.get("X-Admin-Token", "")
        return is_run_once_authorized(client_ip=client_ip, admin_token=token, provided_token=provided)

    def log_message(self, format: str, *args: object) -> None:
        return


def run_api_server(host: str | None = None, port: int | None = None) -> None:
    settings = Settings.from_env()
    context = _Context(settings)
    ApiHandler.context = context
    bind_host = host or settings.api_host
    bind_port = port or settings.api_port

    server = ThreadingHTTPServer((bind_host, bind_port), ApiHandler)
    try:
        print(f"API server listening on http://{bind_host}:{bind_port}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_api_server()
