from __future__ import annotations

import json
import mimetypes
import os
import secrets
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


ROOT = Path(__file__).resolve().parent
STATIC_ROOT = ROOT / "static"
DATA_ROOT = ROOT / "data"
MODE = os.environ.get("LAB_MODE", "xss")
VALID_MODES = {"xss", "idor", "traversal"}
if MODE not in VALID_MODES:
    raise SystemExit(f"unsupported LAB_MODE: {MODE}")

SESSIONS: set[str] = set()
SESSION_COOKIE_NAME = f"lab_session_{MODE}"

RESEARCH_ITEMS = [
    {"id": "RS-2026-1042", "title": "지역혁신 기반 공공기술 실증지원", "agency": "지역혁신본부", "deadline": "2026-11-28", "status": "접수중"},
    {"id": "RS-2026-1038", "title": "탄소중립 핵심원천기술 공동연구", "agency": "전략기술본부", "deadline": "2026-11-21", "status": "접수중"},
    {"id": "RS-2026-1027", "title": "연구데이터 개방·활용 촉진사업", "agency": "디지털연구본부", "deadline": "2026-11-14", "status": "마감임박"},
    {"id": "RS-2026-0994", "title": "신진연구자 성장지원 프로그램", "agency": "인재양성본부", "deadline": "2026-12-05", "status": "공고"},
]

WORK_ORDERS = {
    "WO-2026-41021": {
        "id": "WO-2026-41021", "title": "공급관리소 정압설비 정기점검", "site": "중부 제3공급관리소",
        "division": "중부정비사업소", "assignee": "박지훈", "window": "2026-11-05 13:00–16:00",
        "risk": "보통", "status": "작업승인", "scope": "필터 차압 확인, 조정기 작동시험, 누설검지",
        "classification": "일반업무", "evidence": "",
    },
    "WO-2026-41022": {
        "id": "WO-2026-41022", "title": "중앙통제 원격차단밸브 비상점검", "site": "수도권 중앙통제기지",
        "division": "중앙통제기술팀", "assignee": "보안제한 담당", "window": "2026-11-05 22:00–23:30",
        "risk": "높음", "status": "제한열람", "scope": "비상차단 시나리오 및 원격제어 경로 검증",
        "classification": "내부제한", "evidence": "IDOR-EVIDENCE-GAS-2026",
    },
    "WO-2026-41023": {
        "id": "WO-2026-41023", "title": "계량설비 통신상태 확인", "site": "남부 제1공급관리소",
        "division": "남부정비사업소", "assignee": "이서준", "window": "2026-11-06 09:00–11:00",
        "risk": "낮음", "status": "배정완료", "scope": "통신모뎀 상태 및 원격검침 데이터 확인",
        "classification": "타부서", "evidence": "",
    },
}


class Handler(BaseHTTPRequestHandler):
    server_version = "PublicSectorTraining/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[{MODE}] {self.address_string()} {fmt % args}")

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        super().end_headers()

    def send_bytes(self, status: int, body: bytes, content_type: str, extra_headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status: int, payload: object, extra_headers: dict[str, str] | None = None) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_bytes(status, body, "application/json; charset=utf-8", extra_headers)

    def session(self) -> tuple[bool, str | None]:
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        morsel = cookie.get(SESSION_COOKIE_NAME)
        token = morsel.value if morsel else None
        return token in SESSIONS, token

    def require_session(self) -> bool:
        ok, _ = self.session()
        if not ok:
            self.send_json(HTTPStatus.UNAUTHORIZED, {"error": "세션이 필요합니다."})
            return False
        return True

    def serve_index(self) -> None:
        ok, _ = self.session()
        headers: dict[str, str] = {}
        if not ok:
            token = secrets.token_urlsafe(32)
            SESSIONS.add(token)
            headers["Set-Cookie"] = f"{SESSION_COOKIE_NAME}={token}; Path=/; HttpOnly; SameSite=Strict"
        body = (STATIC_ROOT / MODE / "index.html").read_bytes()
        self.send_bytes(HTTPStatus.OK, body, "text/html; charset=utf-8", headers)

    def serve_static(self, path: str) -> bool:
        if path == "/common.css":
            candidate = STATIC_ROOT / "common.css"
        elif path in {"/app.js", "/theme.css", "/responsive.css", "/nrf-logo.svg"}:
            candidate = STATIC_ROOT / MODE / path.lstrip("/")
        else:
            return False
        if not candidate.is_file():
            return False
        content_type, _ = mimetypes.guess_type(candidate.name)
        self.send_bytes(HTTPStatus.OK, candidate.read_bytes(), f"{content_type or 'application/octet-stream'}; charset=utf-8")
        return True

    def api_research(self, query: str) -> None:
        params = parse_qs(query, keep_blank_values=True)
        term = unquote(params.get("q", [""])[0]).strip()
        folded = term.lower()
        items = [item for item in RESEARCH_ITEMS if not term or folded in (item["title"] + item["agency"] + item["id"]).lower()]
        # Deliberately returns the raw term. The client places it into an HTML summary.
        self.send_json(HTTPStatus.OK, {"query": term, "count": len(items), "items": items})

    def api_work_order(self, query: str) -> None:
        params = parse_qs(query, keep_blank_values=True)
        order_id = unquote(params.get("id", [""])[0]).strip().upper()
        order = WORK_ORDERS.get(order_id)
        if not order:
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "작업지시서를 찾을 수 없습니다.", "id": order_id})
            return
        # Deliberate IDOR: session is checked, but object ownership/division is not.
        self.send_json(HTTPStatus.OK, {"viewer_division": "중부정비사업소", "work_order": order})

    def api_document(self, query: str) -> None:
        params = parse_qs(query, keep_blank_values=True)
        requested = unquote(params.get("file", [""])[0]).strip()
        if not requested:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "file 값이 필요합니다."})
            return
        public_root = DATA_ROOT / "public"
        candidate = (public_root / requested).resolve()
        # Deliberately flawed boundary: traversal inside the synthetic data root is allowed.
        if DATA_ROOT not in candidate.parents:
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "교육 데이터 영역 밖의 경로입니다."})
            return
        if not candidate.is_file():
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "자료를 찾을 수 없습니다.", "requested": requested})
            return
        relative = candidate.relative_to(DATA_ROOT).as_posix()
        classification = "공개업무" if relative.startswith("public/") else "내부제한"
        self.send_json(HTTPStatus.OK, {
            "requested": requested,
            "resolved_archive_path": relative,
            "classification": classification,
            "content": candidate.read_text(encoding="utf-8"),
        })

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            self.send_json(HTTPStatus.OK, {"status": "ok", "mode": MODE})
            return
        if parsed.path == "/":
            self.serve_index()
            return
        if self.serve_static(parsed.path):
            return
        if parsed.path.startswith("/api/") and not self.require_session():
            return
        if MODE == "xss" and parsed.path == "/api/research/search":
            self.api_research(parsed.query)
            return
        if MODE == "idor" and parsed.path == "/api/work-orders":
            self.api_work_order(parsed.query)
            return
        if MODE == "traversal" and parsed.path == "/api/document":
            self.api_document(parsed.query)
            return
        self.send_json(HTTPStatus.NOT_FOUND, {"error": "요청한 기능을 찾을 수 없습니다."})


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
