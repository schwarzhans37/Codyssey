# mysql_helper.py
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable

import mysql.connector
from mysql.connector import Error, MySQLConnection


class MySQLHelper:
    """간단한 MySQL 헬퍼 클래스 (Pep 8 준수, 외부 라이브러리 불가)."""

    def __init__(self, **db_conf: Any) -> None:
        self._db_conf = db_conf
        self._conn: MySQLConnection | None = None
        self._cur = None

    # ---------- 내부 유틸 ----------
    def _ensure_cursor(self) -> None:
        if self._conn is None or not self._conn.is_connected():
            self._conn = mysql.connector.connect(**self._db_conf)
        if self._cur is None or self._cur.close:
            self._cur = self._conn.cursor()

    # ---------- Context Manager ----------
    def __enter__(self) -> "MySQLHelper":
        self._ensure_cursor()
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        """예외가 발생하면 롤백, 아니면 커밋.  꼭 False 반환해 예외를 상위로 전달."""
        if exc:
            self._conn.rollback()
        else:
            self._conn.commit()
        self.close()
        return False  # 예외를 무시하지 않음

    # ---------- Core API ----------
    def execute(self, sql: str, params: Iterable[Any] | None = None) -> None:
        self._ensure_cursor()
        try:
            self._cur.execute(sql, params)
        except Error as e:
            print(f"[DB-ERROR] {e.msg}")
            raise

    def executemany(self, sql: str, seq_params: list[tuple[Any, ...]]) -> None:
        self._ensure_cursor()
        try:
            self._cur.executemany(sql, seq_params)
        except Error as e:
            print(f"[DB-ERROR] {e.msg}")
            raise

    # ---------- Fetch ----------
    def fetchone(self) -> tuple[Any, ...] | None:
        return self._cur.fetchone() if self._cur else None

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self._cur.fetchall() if self._cur else []

    def fetchall_dict(self) -> list[dict[str, Any]]:
        if not self._cur:
            return []
        cols = [d[0] for d in self._cur.description]
        return [dict(zip(cols, row)) for row in self._cur.fetchall()]

    # ---------- Bulk CSV ----------
    def bulk_insert_csv(
        self,
        csv_path: Path,
        table: str,
        columns: list[str],
        transform: callable | None = None,
    ) -> int:
        """
        CSV 파일을 읽어 INSERT … VALUES (%s, …) 형태로 일괄 삽입.
        transform(row_dict) -> tuple 를 넘기면 값 가공 가능.
        반환값: 삽입된 행 수
        """
        if not csv_path.exists():
            raise FileNotFoundError(csv_path)

        ph = ", ".join(["%s"] * len(columns))
        col_clause = ", ".join(columns)
        sql = f"INSERT INTO {table} ({col_clause}) VALUES ({ph})"

        with csv_path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            params = []
            for row in reader:
                params.append(transform(row) if transform else tuple(row[c] for c in columns))

        self.executemany(sql, params)
        return len(params)

    # ---------- 마무리 ----------
    def commit(self) -> None:
        if self._conn:
            self._conn.commit()

    def rollback(self) -> None:
        if self._conn:
            self._conn.rollback()

    def close(self) -> None:
        if self._cur and not self._cur.close:
            self._cur.close()
        if self._conn and self._conn.is_connected():
            self._conn.close()
