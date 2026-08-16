from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlencode

import pytest

from scut_senior_api.adapters.github import UrllibHttpTransport
from scut_senior_api.adapters.openrouter import UrllibJsonHttpClient
from scut_senior_api.adapters.openrouter_health import UrllibJsonHttpReadClient


class RecordingServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, *, status_code: int, location: str | None = None):
        super().__init__(("127.0.0.1", 0), RecordingHandler)
        self.status_code = status_code
        self.location = location
        self.requests: list[dict[str, object]] = []

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server_address[1]}/redirect-target"


class RecordingHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self._respond()

    def do_POST(self) -> None:
        self._respond()

    def _respond(self) -> None:
        server = self.server
        assert isinstance(server, RecordingServer)
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length) if content_length else b""
        server.requests.append(
            {
                "method": self.command,
                "headers": dict(self.headers.items()),
                "body": body,
            }
        )
        self.send_response(server.status_code)
        if server.location is not None:
            self.send_header("Location", server.location)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, *_: object) -> None:
        return


@contextmanager
def running_server(
    *, status_code: int = 200, location: str | None = None
) -> Iterator[RecordingServer]:
    server = RecordingServer(status_code=status_code, location=location)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.parametrize("redirect_status", [301, 302, 303, 307, 308])
def test_model_post_transport_never_follows_redirect_with_authorization(
    redirect_status: int,
) -> None:
    secret = "model-redirect-secret"
    with running_server() as sink:
        with running_server(status_code=redirect_status, location=sink.url) as origin:
            response = UrllibJsonHttpClient().post_json(
                origin.url,
                headers={"Authorization": f"Bearer {secret}"},
                payload={"model": "fixed-model"},
                timeout_seconds=2,
            )

    assert response.status_code == redirect_status
    assert len(origin.requests) == 1
    assert origin.requests[0]["headers"]["Authorization"] == f"Bearer {secret}"
    assert sink.requests == []


def test_health_get_transport_never_follows_redirect_with_authorization() -> None:
    secret = "health-redirect-secret"
    with running_server() as sink:
        with running_server(status_code=302, location=sink.url) as origin:
            response = UrllibJsonHttpReadClient().get_json(
                origin.url,
                headers={"Authorization": f"Bearer {secret}"},
                timeout_seconds=2,
            )

    assert response.status_code == 302
    assert len(origin.requests) == 1
    assert origin.requests[0]["headers"]["Authorization"] == f"Bearer {secret}"
    assert sink.requests == []


def test_github_get_transport_never_follows_redirect_with_authorization() -> None:
    secret = "github-access-redirect-secret"
    with running_server() as sink:
        with running_server(status_code=302, location=sink.url) as origin:
            response = UrllibHttpTransport().request(
                "GET",
                origin.url,
                headers={"Authorization": f"Bearer {secret}"},
                body=None,
                timeout_seconds=2,
            )

    assert response.status_code == 302
    assert len(origin.requests) == 1
    assert origin.requests[0]["headers"]["Authorization"] == f"Bearer {secret}"
    assert sink.requests == []


def test_github_post_transport_never_redirects_client_secret_body() -> None:
    secret = "github-client-redirect-secret"
    body = urlencode({"client_id": "client", "client_secret": secret}).encode()
    with running_server() as sink:
        with running_server(status_code=302, location=sink.url) as origin:
            response = UrllibHttpTransport().request(
                "POST",
                origin.url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                body=body,
                timeout_seconds=2,
            )

    assert response.status_code == 302
    assert len(origin.requests) == 1
    assert secret.encode() in origin.requests[0]["body"]
    assert sink.requests == []
