#!/usr/bin/env python3
"""Education-only fictional railway crew scheduling portal.

The schedule name search intentionally contains one SQL injection weakness.
All records are synthetic and the database is recreated on every container start.
"""

from __future__ import annotations

import json
import mimetypes
import os
import re
import secrets
import sqlite3
from datetime import date
from http.cookies import SimpleCookie
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


APP_ROOT = Path(__file__).resolve().parent
STATIC_ROOT = APP_ROOT / "static"
DB_PATH = Path(os.environ.get("LAB_DB_PATH", "/tmp/lab-3101.db"))
PORT = int(os.environ.get("PORT", "8080"))
DEFAULT_DATE = "2026-11-05"
SESSION_TOKEN = secrets.token_urlsafe(32)


def initialize_database() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    connection = sqlite3.connect(DB_PATH)
    connection.executescript(
        """
        CREATE TABLE crew_members (
            id INTEGER PRIMARY KEY,
            employee_no TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            depot TEXT NOT NULL
        );

        CREATE TABLE schedules (
            id INTEGER PRIMARY KEY,
            crew_id INTEGER NOT NULL,
            duty_date TEXT NOT NULL,
            train_no TEXT NOT NULL,
            route TEXT NOT NULL,
            report_time TEXT NOT NULL,
            release_time TEXT NOT NULL,
            platform TEXT NOT NULL,
            duty_status TEXT NOT NULL,
            visible INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (crew_id) REFERENCES crew_members(id)
        );

        CREATE TABLE notices (
            id INTEGER PRIMARY KEY,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            posted_at TEXT NOT NULL,
            priority INTEGER NOT NULL DEFAULT 0
        );
        """
    )

    crew_rows = [
        (1, "CR-24017", "김도윤", "기관사", "서울승무사업소"),
        (2, "CR-23108", "박서현", "열차팀장", "서울승무사업소"),
        (3, "CR-25142", "이준호", "차장", "용산승무사업소"),
        (4, "CR-22881", "최유진", "기관사", "수서승무사업소"),
        (5, "CR-24773", "정하람", "객실승무원", "서울승무사업소"),
        (6, "CR-21904", "오민석", "열차팀장", "용산승무사업소"),
        (99, "SEC-000", "비공개 비상대응조", "보안교육 증거", "교육통제실"),
    ]
    connection.executemany(
        "INSERT INTO crew_members(id, employee_no, name, role, depot) VALUES (?, ?, ?, ?, ?)",
        crew_rows,
    )

    schedule_rows = [
        (101, 1, DEFAULT_DATE, "KTX 021", "서울 → 부산", "05:40", "09:18", "서울 8번", "운행확정", 1),
        (102, 2, DEFAULT_DATE, "KTX 105", "서울 → 동대구", "06:20", "09:05", "서울 11번", "운행확정", 1),
        (103, 3, DEFAULT_DATE, "ITX 2031", "용산 → 춘천", "07:10", "10:02", "용산 2번", "운행확정", 1),
        (104, 4, DEFAULT_DATE, "SRT 315", "수서 → 광주송정", "08:05", "11:21", "수서 5번", "대기", 1),
        (105, 5, DEFAULT_DATE, "KTX 127", "서울 → 대전", "09:15", "11:47", "서울 9번", "운행확정", 1),
        (106, 6, DEFAULT_DATE, "KTX 044", "부산 → 서울", "12:30", "16:18", "부산 6번", "변경검토", 1),
        (900, 99, "2026-11-06", "LAB-SQLI-EVIDENCE-RAIL-2026", "보안교육 증거 레코드", "00:00", "00:01", "비공개", "외부노출금지", 0),
    ]
    connection.executemany(
        """INSERT INTO schedules(
            id, crew_id, duty_date, train_no, route, report_time,
            release_time, platform, duty_status, visible
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        schedule_rows,
    )

    notice_rows = [
        (1, "운행", "동절기 운전취급 및 승무보고 기준 안내", "2026-11-05", 1),
        (2, "안전", "승강장 안전확인 체크리스트 개정", "2026-11-04", 1),
        (3, "일반", "11월 승무원 교육 일정 및 참석 확인", "2026-11-03", 0),
    ]
    connection.executemany(
        "INSERT INTO notices(id, category, title, posted_at, priority) VALUES (?, ?, ?, ?, ?)",
        notice_rows,
    )
    connection.commit()
    connection.close()


def database() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


class RailCrewHandler(BaseHTTPRequestHandler):
    server_version = "RailCrewTraining/1.0"

    def log_message(self, format_string: str, *args: object) -> None:
        print(f"{self.client_address[0]} - {format_string % args}", flush=True)

    def send_json(self, payload: object, status: int = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.end_headers()
        self.wfile.write(encoded)

    def serve_static(self, request_path: str) -> None:
        relative_path = "index.html" if request_path in ("", "/") else request_path.lstrip("/")
        candidate = (STATIC_ROOT / relative_path).resolve()
        if STATIC_ROOT not in candidate.parents and candidate != STATIC_ROOT:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not candidate.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        body = candidate.read_bytes()
        content_type, _ = mimetypes.guess_type(candidate.name)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type or 'application/octet-stream'}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if relative_path == "index.html":
            self.send_header(
                "Set-Cookie",
                f"rail_session={SESSION_TOKEN}; Path=/; HttpOnly; SameSite=Strict",
            )
        self.end_headers()
        self.wfile.write(body)

    def has_valid_session(self) -> bool:
        raw_cookie = self.headers.get("Cookie", "")
        cookie = SimpleCookie()
        try:
            cookie.load(raw_cookie)
        except Exception:
            return False
        session = cookie.get("rail_session")
        return bool(session and secrets.compare_digest(session.value, SESSION_TOKEN))

    def api_me(self) -> None:
        self.send_json(
            {
                "employeeNo": "EDU-2601",
                "name": "교육 운영자",
                "organization": "서울승무사업소",
                "role": "승무일정 조회",
                "lastLogin": "2026-11-05 08:42",
                "environment": "security-training",
            }
        )

    def api_summary(self) -> None:
        with database() as connection:
            summary = connection.execute(
                """SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN duty_status = '운행확정' THEN 1 ELSE 0 END) AS confirmed,
                    SUM(CASE WHEN duty_status = '대기' THEN 1 ELSE 0 END) AS standby,
                    SUM(CASE WHEN duty_status = '변경검토' THEN 1 ELSE 0 END) AS review
                FROM schedules
                WHERE visible = 1 AND duty_date = ?""",
                (DEFAULT_DATE,),
            ).fetchone()
        self.send_json(dict(summary))

    def api_notices(self) -> None:
        with database() as connection:
            rows = connection.execute(
                "SELECT category, title, posted_at, priority FROM notices ORDER BY priority DESC, posted_at DESC"
            ).fetchall()
        self.send_json({"items": [dict(row) for row in rows]})

    def api_schedules(self, query_string: str) -> None:
        params = parse_qs(query_string, keep_blank_values=True)
        search = unquote(params.get("query", [""])[0]).strip()
        duty_date = params.get("date", [DEFAULT_DATE])[0]

        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", duty_date):
            self.send_json({"error": "조회일자는 YYYY-MM-DD 형식이어야 합니다."}, HTTPStatus.BAD_REQUEST)
            return
        if len(search) > 180:
            self.send_json({"error": "검색어가 너무 깁니다."}, HTTPStatus.BAD_REQUEST)
            return

        # Intentionally vulnerable for this isolated CWE-89 training target.
        # The date stays parameterized; only the crew-name search is concatenated.
        sql = (
            "SELECT s.id AS schedule_id, c.employee_no, c.name, c.role, c.depot, "
            "s.duty_date, s.train_no, s.route, s.report_time, s.release_time, "
            "s.platform, s.duty_status "
            "FROM schedules s JOIN crew_members c ON c.id = s.crew_id "
            "WHERE s.duty_date = ? AND s.visible = 1 "
            f"AND c.name LIKE '%{search}%' "
            "ORDER BY s.report_time ASC"
        )

        try:
            with database() as connection:
                rows = connection.execute(sql, (duty_date,)).fetchall()
        except sqlite3.Error as error:
            self.send_json(
                {
                    "error": "일정 조회 처리 중 데이터베이스 오류가 발생했습니다.",
                    "reference": "SCH-QUERY-500",
                    "detail": str(error),
                },
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return

        self.send_json(
            {
                "date": duty_date,
                "query": search,
                "count": len(rows),
                "items": [dict(row) for row in rows],
            }
        )

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            self.send_json({"status": "ok", "service": "3101"})
        elif parsed.path.startswith("/api/") and not self.has_valid_session():
            self.send_json(
                {"error": "인증된 교육 세션이 필요합니다.", "code": "SESSION_REQUIRED"},
                HTTPStatus.UNAUTHORIZED,
            )
        elif parsed.path == "/api/schedules":
            self.api_schedules(parsed.query)
        else:
            self.serve_static(parsed.path)


if __name__ == "__main__":
    initialize_database()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), RailCrewHandler)
    print(f"Rail crew training portal listening on 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()
