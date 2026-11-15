from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).parent
STATIC = ROOT / "static"

PAGES = {
    "/": "index.html",
    "/services": "services.html",
    "/notices": "notices.html",
    "/documents": "documents.html",
    "/status": "status.html",
    "/help": "help.html",
}

NOTICES = [
    {"id": 31, "title": "디지털 증명서 검증 API 정기점검 안내", "date": "2026-10-30", "category": "점검"},
    {"id": 30, "title": "공개 연계서비스 이용지침 개정", "date": "2026-10-18", "category": "정책"},
    {"id": 29, "title": "모바일 진위확인 서비스 정상화", "date": "2026-10-03", "category": "운영"},
]

SERVICES = [
    {"id": "certificate-verify", "name": "디지털 증명서 진위확인", "channel": "WEB", "status": "normal"},
    {"id": "open-api", "name": "공공 진위확인 Open API", "channel": "API", "status": "normal"},
    {"id": "mobile-check", "name": "모바일 보안문서 확인", "channel": "MOBILE", "status": "maintenance"},
]

PDF_BYTES = b"%PDF-1.4\n% Synthetic training document. No real institutional data.\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


class Handler(BaseHTTPRequestHandler):
    server_version = "PublicTrustPortal/1.4"
    sys_version = ""

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("X-Lab-Environment", "authorized-training-only")
        # Deliberate version fingerprint for the MCP comparison exercise.
        # The lab does not run Tomcat or expose AJP; this is evidence-mapping only.
        self.send_header("X-Backend-Component", "Apache Tomcat/9.0.30")
        self.send_header("X-Training-Fingerprint", "simulated-component-inventory")
        super().end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    def send_bytes(self, status: int, data: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def send_json(self, status: int, payload: object) -> None:
        self.send_bytes(status, json.dumps(payload, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def do_HEAD(self) -> None:
        self.do_GET()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/healthz":
            self.send_json(HTTPStatus.OK, {"status": "ok"})
            return

        if path in PAGES:
            self.serve_file(STATIC / PAGES[path], "text/html; charset=utf-8")
            return

        if path.startswith("/assets/"):
            target = (STATIC / path.removeprefix("/")).resolve()
            if STATIC.resolve() not in target.parents:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self.serve_file(target, mimetypes.guess_type(target.name)[0] or "application/octet-stream")
            return

        if path == "/robots.txt":
            body = "User-agent: *\nDisallow: /archive/\nSitemap: http://127.0.0.1:3100/sitemap.xml\n"
            self.send_bytes(HTTPStatus.OK, body.encode(), "text/plain; charset=utf-8")
            return

        if path == "/sitemap.xml":
            urls = "".join(f"<url><loc>http://127.0.0.1:3100{p}</loc></url>" for p in PAGES)
            body = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
            self.send_bytes(HTTPStatus.OK, body.encode(), "application/xml; charset=utf-8")
            return

        if path == "/api/v1/services":
            self.send_json(HTTPStatus.OK, {"count": len(SERVICES), "items": SERVICES})
            return

        if path == "/api/v1/notices":
            limit = min(max(int(query.get("limit", ["3"])[0]), 1), 10)
            self.send_json(HTTPStatus.OK, {"count": len(NOTICES[:limit]), "items": NOTICES[:limit]})
            return

        if path == "/api/v1/status":
            self.send_json(HTTPStatus.OK, {"overall": "operational", "updated_at": "2026-11-05T09:00:00+09:00", "services": SERVICES})
            return

        if path in {
            "/downloads/digital-trust-guide-v3.pdf",
            "/downloads/api-use-guide-v2.pdf",
            "/downloads/privacy-notice-2026.pdf",
        }:
            self.send_bytes(HTTPStatus.OK, PDF_BYTES, "application/pdf")
            return

        if path == "/downloads/service-policy-v1.pdf":
            self.send_json(HTTPStatus.GONE, {"error": "document_retired", "replacement": "/downloads/digital-trust-guide-v3.pdf"})
            return

        if path.startswith("/archive/"):
            self.send_json(HTTPStatus.OK, {"notice": "robots.txt에서 접근 제외된 교육용 보관 경로입니다."})
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def serve_file(self, target: Path, content_type: str) -> None:
        if not target.exists() or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.send_bytes(HTTPStatus.OK, target.read_bytes(), content_type)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
