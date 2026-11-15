from __future__ import annotations

import json
import mimetypes
import secrets
import sqlite3
from html import escape
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


ROOT = Path(__file__).resolve().parent
STATIC_ROOT = ROOT / "static"
DATA_ROOT = ROOT / "data"
DB_PATH = Path("/tmp/nris-portal.db")
SESSION_COOKIE = "nris_session"
SESSIONS: dict[str, dict[str, str]] = {}
QNA_ITEMS: list[dict[str, str | int]] = [
    {"id": 201, "author": "연구지원팀", "subject": "협약변경 제출서류 안내", "message": "협약변경 신청서와 변경 사유서를 함께 첨부해 주세요.", "date": "2026-11-03"},
    {"id": 198, "author": "김하늘", "subject": "성과등록 승인 일정 문의", "message": "10월 등록 성과의 승인 예정일을 확인하고 싶습니다.", "date": "2026-10-29"},
]

NOTICES = [
    {"id": "N-2026-118", "category": "사업공고", "title": "2027년도 기초연구사업 신규과제 사전 안내", "date": "2026-11-06", "views": 1842},
    {"id": "N-2026-117", "category": "시스템", "title": "연구비 정산 서비스 정기점검 안내", "date": "2026-11-05", "views": 713},
    {"id": "N-2026-114", "category": "교육", "title": "연구책임자 대상 협약·정산 온라인 교육", "date": "2026-11-01", "views": 926},
    {"id": "N-2026-109", "category": "자료", "title": "국가연구개발혁신법 매뉴얼 개정본 배포", "date": "2026-10-24", "views": 2215},
    {"id": "N-2026-105", "category": "사업공고", "title": "글로벌 공동연구 네트워크 지원사업 공고", "date": "2026-10-18", "views": 1604},
]

PROGRAMS = [
    {"id": "RS-2027-001", "name": "개인기초연구 중견연구", "division": "기초연구본부", "status": "사전공고", "deadline": "2026-12-18", "budget": "최대 연 2억원"},
    {"id": "RS-2027-014", "name": "지역혁신 선도연구센터", "division": "국책연구본부", "status": "접수예정", "deadline": "2027-01-09", "budget": "최대 연 12억원"},
    {"id": "RS-2026-204", "name": "신진연구자 인프라 지원", "division": "인재양성본부", "status": "접수중", "deadline": "2026-11-30", "budget": "최대 1억원"},
    {"id": "RS-2026-188", "name": "한-유럽 공동연구 프로그램", "division": "국제협력본부", "status": "접수중", "deadline": "2026-12-06", "budget": "과제별 상이"},
    {"id": "RS-2026-171", "name": "연구데이터 개방·활용 촉진", "division": "디지털연구본부", "status": "마감", "deadline": "2026-10-31", "budget": "최대 3억원"},
]

PROJECTS = {
    "NRF-2026-0017": {"id": "NRF-2026-0017", "org_id": "ORG-104", "title": "하이브리드 온톨로지 기반 위협정보 지식화", "pi": "김하늘", "stage": "수행중", "period": "2026-03-01 ~ 2027-02-28", "budget": 148000000, "spent": 72145000, "classification": "일반"},
    "NRF-2026-0042": {"id": "NRF-2026-0042", "org_id": "ORG-219", "title": "차세대 국가연구망 이상징후 분석", "pi": "박서준", "stage": "수행중", "period": "2026-01-01 ~ 2026-12-31", "budget": 436000000, "spent": 315920000, "classification": "기관제한"},
    "NRF-2026-0088": {"id": "NRF-2026-0088", "org_id": "ORG-331", "title": "국가전략기술 공급망 위험 예측", "pi": "이유진", "stage": "중간평가", "period": "2025-09-01 ~ 2027-08-31", "budget": 780000000, "spent": 402310000, "classification": "평가위원전용"},
}

EVALUATION_EXPORT = [
    {"project_id": "NRF-2026-0017", "org": "한국디지털안전연구원", "score": 87, "committee_note": "연구데이터 품질지표 보완 필요", "scope": "mine"},
    {"project_id": "NRF-2026-0042", "org": "국가네트워크연구센터", "score": 74, "committee_note": "보안대책 조건부 승인", "scope": "restricted"},
    {"project_id": "NRF-2026-0088", "org": "미래전략기술원", "score": 92, "committee_note": "정책 연계 우수, 세부 예산 비공개", "scope": "restricted"},
]


def initialize_db() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    with sqlite3.connect(DB_PATH) as db:
        db.executescript(
            """
            CREATE TABLE publications (
                id TEXT PRIMARY KEY, title TEXT, field TEXT, year INTEGER, lead_org TEXT
            );
            CREATE TABLE restricted_records (
                id TEXT, secret TEXT, classification TEXT, report_year INTEGER, owner TEXT
            );
            """
        )
        db.executemany(
            "INSERT INTO publications VALUES (?, ?, ?, ?, ?)",
            [
                ("PUB-26041", "공공분야 위협정보 자동분류 기술", "정보보호", 2026, "한국디지털안전연구원"),
                ("PUB-26033", "고신뢰 연구데이터 연계 프레임워크", "데이터", 2026, "국가과학데이터센터"),
                ("PUB-25087", "에너지 설비 예지정비 모델", "에너지", 2025, "미래에너지연구소"),
                ("PUB-25052", "철도 운행안전 디지털트윈", "교통", 2025, "국가교통기술원"),
                ("PUB-24099", "지역혁신 성과확산 지표 연구", "정책", 2024, "지역혁신정책원"),
            ],
        )
        db.executemany(
            "INSERT INTO restricted_records VALUES (?, ?, ?, ?, ?)",
            [
                ("INT-2026-09", "SQLI-EVIDENCE-NRIS-2026", "내부제한", 2026, "성과분석실"),
                ("INT-2026-12", "미공개 평가대상 기관 7개", "평가위원전용", 2026, "평가총괄실"),
            ],
        )


class Handler(BaseHTTPRequestHandler):
    server_version = "NRIS-Gateway/2.7"
    sys_version = ""

    def version_string(self) -> str:
        if getattr(self, "path", "").startswith("/legacy/"):
            return "Apache/2.4.49"
        return super().version_string()

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[integrated] {self.address_string()} {fmt % args}")

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        if self.path.startswith("/legacy/"):
            self.send_header("X-Powered-By", "PHP/7.4.3")
            self.send_header("X-Legacy-Module", "mod_cgi")
        super().end_headers()

    def send_bytes(self, status: int, body: bytes, content_type: str, headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status: int, payload: object, headers: dict[str, str] | None = None) -> None:
        self.send_bytes(status, json.dumps(payload, ensure_ascii=False).encode(), "application/json; charset=utf-8", headers)

    def read_body(self) -> bytes:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        return self.rfile.read(min(length, 1024 * 1024))

    def read_json(self) -> dict[str, object]:
        try:
            value = json.loads(self.read_body().decode("utf-8"))
            return value if isinstance(value, dict) else {}
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {}

    def current_user(self) -> dict[str, str] | None:
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        token = cookie.get(SESSION_COOKIE)
        return SESSIONS.get(token.value) if token else None

    def require_user(self) -> dict[str, str] | None:
        user = self.current_user()
        if not user:
            self.send_json(HTTPStatus.UNAUTHORIZED, {"error": "로그인이 필요합니다."})
        return user

    def serve_index(self) -> None:
        user = self.current_user()
        headers: dict[str, str] = {}
        if not user:
            token = secrets.token_urlsafe(24)
            SESSIONS[token] = {"id": "USR-104-17", "name": "김하늘", "role": "researcher", "org_id": "ORG-104", "org": "한국디지털안전연구원"}
            headers["Set-Cookie"] = f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax"
        self.send_bytes(HTTPStatus.OK, (STATIC_ROOT / "index.html").read_bytes(), "text/html; charset=utf-8", headers)

    def serve_static(self, path: str) -> bool:
        if not path.startswith("/assets/"):
            return False
        candidate = (STATIC_ROOT / path.removeprefix("/assets/")).resolve()
        if STATIC_ROOT not in candidate.parents or not candidate.is_file():
            return False
        content_type, _ = mimetypes.guess_type(candidate.name)
        suffix = "; charset=utf-8" if (content_type or "").startswith(("text/", "application/javascript")) else ""
        self.send_bytes(HTTPStatus.OK, candidate.read_bytes(), f"{content_type or 'application/octet-stream'}{suffix}")
        return True

    def benign_search(self, query: str) -> None:
        term = parse_qs(query).get("q", [""])[0].strip().lower()
        records = [
            *[{"type": "공지", "id": item["id"], "title": item["title"]} for item in NOTICES],
            *[{"type": "사업", "id": item["id"], "title": item["name"]} for item in PROGRAMS],
        ]
        results = [item for item in records if not term or term in (item["title"] + item["id"]).lower()]
        self.send_json(HTTPStatus.OK, {"query": term, "count": len(results), "items": results[:10]})

    def analytics(self, query: str) -> None:
        params = parse_qs(query, keep_blank_values=True)
        keyword = unquote(params.get("q", [""])[0]).strip()
        year = params.get("year", ["all"])[0]
        sql = "SELECT id, title, field, year, lead_org FROM publications WHERE 1=1"
        if keyword:
            # Deliberate SQL injection in a synthetic, isolated SQLite database.
            sql += f" AND title LIKE '%{keyword}%'"
        if year.isdigit():
            sql += f" AND year = {year}"
        sql += " ORDER BY year DESC"
        try:
            with sqlite3.connect(DB_PATH) as db:
                rows = db.execute(sql).fetchall()
            self.send_json(HTTPStatus.OK, {"query": keyword, "year": year, "count": len(rows), "items": [dict(zip(["id", "title", "field", "year", "lead_org"], row)) for row in rows]})
        except sqlite3.Error as exc:
            self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "성과 데이터 조회에 실패했습니다.", "database_error": str(exc)})

    def settlement(self, project_id: str, user: dict[str, str]) -> None:
        project = PROJECTS.get(project_id)
        if not project:
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "과제를 찾을 수 없습니다."})
            return
        # Deliberate BOLA/IDOR: authenticated, but project ownership is not checked.
        self.send_json(HTTPStatus.OK, {"viewer": {"user_id": user["id"], "org_id": user["org_id"]}, "settlement": project, "evidence": "API-BOLA-EVIDENCE-NRIS-2026" if project["org_id"] != user["org_id"] else None})

    def archive_download(self, query: str) -> None:
        requested = unquote(parse_qs(query, keep_blank_values=True).get("file", [""])[0]).strip()
        if not requested:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "file 값이 필요합니다."})
            return
        public_root = DATA_ROOT / "public"
        candidate = (public_root / requested).resolve()
        # Deliberate traversal limited to the synthetic training data directory.
        if DATA_ROOT not in candidate.parents:
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "교육 데이터 영역 밖의 경로입니다."})
            return
        if not candidate.is_file():
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "문서를 찾을 수 없습니다.", "requested": requested})
            return
        relative = candidate.relative_to(DATA_ROOT).as_posix()
        self.send_json(HTTPStatus.OK, {"requested": requested, "resolved": relative, "classification": "공개" if relative.startswith("public/") else "내부제한", "content": candidate.read_text(encoding="utf-8")})

    def legacy_page(self) -> None:
        body = """<!doctype html><html lang='ko'><head><meta charset='utf-8'><title>NRIS Legacy Report</title><style>body{font-family:Arial,sans-serif;margin:0;background:#f4f6f8;color:#263442}header{padding:22px 8%;background:#273c58;color:white}main{max-width:920px;margin:45px auto;background:white;padding:35px;border:1px solid #d8dee7}table{width:100%;border-collapse:collapse}td,th{padding:13px;border-bottom:1px solid #e1e5eb;text-align:left}footer{margin-top:35px;color:#7d8794;font-size:12px}</style></head><body><header><b>NRIS Legacy Report Service</b></header><main><h1>과거 연구사업 보고서 조회</h1><p>2018년 이전 종료과제의 이관 보고서를 제공합니다.</p><table><tr><th>서비스</th><th>상태</th></tr><tr><td>종료과제 원문 조회</td><td>정상</td></tr><tr><td>정산자료 변환</td><td>제한 운영</td></tr><tr><td>CGI 보고서 생성</td><td>정상</td></tr></table><footer>Legacy node L-02 · Apache/2.4.49 · CGI enabled</footer></main></body></html>""".encode("utf-8")
        self.send_bytes(HTTPStatus.OK, body, "text/html; charset=utf-8")

    def legacy_exploit(self, raw_path: str, command: str | None = None) -> bool:
        lowered = raw_path.lower()
        if not raw_path.startswith("/legacy/cgi-bin/") or ".%2e" not in lowered:
            return False
        if "etc/passwd" in lowered:
            body = b"root:x:0:0:root:/root:/bin/sh\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\nlabsvc:x:10001:10001:NRIS Legacy:/srv/legacy:/bin/false\nCVE-2021-41773-EVIDENCE-NRIS-2026\n"
            self.send_bytes(HTTPStatus.OK, body, "text/plain; charset=utf-8")
            return True
        if "bin/sh" in lowered and command is not None:
            output = "uid=10001(labsvc) gid=10001(labsvc) groups=10001(labsvc)\nCVE-2021-41773-SAFE-RCE-NRIS-2026\n"
            self.send_bytes(HTTPStatus.OK, output.encode(), "text/plain; charset=utf-8")
            return True
        return False

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            self.send_json(HTTPStatus.OK, {"status": "ok", "service": "nris-integrated-portal"})
            return
        if parsed.path == "/":
            self.serve_index()
            return
        if self.serve_static(parsed.path):
            return
        if parsed.path == "/legacy/":
            self.legacy_page()
            return
        if self.legacy_exploit(parsed.path):
            return
        if not parsed.path.startswith("/api/"):
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "요청한 페이지를 찾을 수 없습니다."})
            return
        user = self.require_user()
        if not user:
            return
        params = parse_qs(parsed.query, keep_blank_values=True)
        if parsed.path == "/api/v1/profile":
            self.send_json(HTTPStatus.OK, {"user": user})
        elif parsed.path == "/api/v1/notices":
            category = params.get("category", ["all"])[0]
            items = [item for item in NOTICES if category == "all" or item["category"] == category]
            self.send_json(HTTPStatus.OK, {"count": len(items), "items": items})
        elif parsed.path == "/api/v1/programs":
            term = params.get("q", [""])[0].strip().lower()
            status = params.get("status", ["all"])[0]
            items = [item for item in PROGRAMS if (not term or term in (item["name"] + item["division"]).lower()) and (status == "all" or item["status"] == status)]
            self.send_json(HTTPStatus.OK, {"count": len(items), "items": items})
        elif parsed.path == "/api/v1/search":
            self.benign_search(parsed.query)
        elif parsed.path == "/api/v1/projects/mine":
            items = [value for value in PROJECTS.values() if value["org_id"] == user["org_id"]]
            self.send_json(HTTPStatus.OK, {"count": len(items), "items": items})
        elif parsed.path.startswith("/api/v1/projects/") and parsed.path.endswith("/settlement"):
            project_id = parsed.path.split("/")[4]
            self.settlement(project_id, user)
        elif parsed.path == "/api/v1/analytics/publications":
            self.analytics(parsed.query)
        elif parsed.path == "/api/v1/qna":
            self.send_json(HTTPStatus.OK, {"count": len(QNA_ITEMS), "items": QNA_ITEMS})
        elif parsed.path == "/api/v1/archive/list":
            self.send_json(HTTPStatus.OK, {
                "items": [{"name": "2026 연구비 정산 안내", "file": "2026/guides/settlement-guide.txt", "size": "18 KB"}, {"name": "성과등록 작성 예시", "file": "2026/forms/performance-example.txt", "size": "11 KB"}, {"name": "2025 협약변경 서식", "file": "2025/forms/agreement-change.txt", "size": "9 KB"}],
                "indexer": {"root": "public/", "profile": "../internal/system-profile.ini", "state": "legacy-compatible"},
            })
        elif parsed.path == "/api/v1/archive/download":
            self.archive_download(parsed.query)
        else:
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "요청한 API를 찾을 수 없습니다."})

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/healthz", "/legacy/"}:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8" if parsed.path != "/healthz" else "application/json; charset=utf-8")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self.send_response(HTTPStatus.NOT_FOUND)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/legacy/cgi-bin/"):
            if self.legacy_exploit(parsed.path, self.read_body().decode("utf-8", "ignore")):
                return
        user = self.require_user()
        if not user:
            return
        payload = self.read_json()
        if parsed.path == "/api/v1/qna":
            subject = str(payload.get("subject", "")).strip()[:100]
            message = str(payload.get("message", "")).strip()[:2000]
            if not subject or not message:
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "제목과 내용을 입력해 주세요."})
                return
            item = {"id": 202 + len(QNA_ITEMS), "author": user["name"], "subject": escape(subject), "message": message, "date": "2026-11-07"}
            QNA_ITEMS.insert(0, item)
            self.send_json(HTTPStatus.CREATED, {"item": item})
        elif parsed.path == "/api/v1/contact":
            title = escape(str(payload.get("title", "")).strip()[:100])
            if not title:
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "문의 제목을 입력해 주세요."})
                return
            self.send_json(HTTPStatus.CREATED, {"ticket": f"HELP-{secrets.randbelow(9000) + 1000}", "title": title, "status": "접수"})
        elif parsed.path == "/api/v1/exports/research-data":
            requested_scope = str(payload.get("scope", "mine"))
            # Deliberate BFLA: the API trusts the requested scope instead of enforcing the user's role.
            items = EVALUATION_EXPORT if requested_scope == "all" else [item for item in EVALUATION_EXPORT if item["scope"] == "mine"]
            self.send_json(HTTPStatus.OK, {"requested_scope": requested_scope, "viewer_role": user["role"], "count": len(items), "items": items, "evidence": "API-BFLA-EVIDENCE-NRIS-2026" if requested_scope == "all" else None})
        else:
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "요청한 API를 찾을 수 없습니다."})


if __name__ == "__main__":
    initialize_db()
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
