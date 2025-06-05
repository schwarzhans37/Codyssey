#!/usr/bin/env python3
# mars_weather_summary.py
"""
CSV → MySQL 적재 + 요약 통계 출력 스크립트
MySQLHelper 클래스로 DB 연결·쿼리 로직을 캡슐화
(Pep 8 준수 · 외부 라이브러리 최소화)
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any
from mysql_helper import MySQLHelper   # 같은 디렉터리에 있어야 import 가능

# ───── 설정 ──────────────────────────────────────────────────────────────
CSV_PATH = Path("mars_weathers_data.csv")
DB_CONF: dict[str, Any] = {
    "host": "localhost",
    "user": "root",
    "password": "deschamps9197",   # 실제 운영 시에는 환경 변수로 분리 권장
    "database": "mars_db",
}

# ───── CSV → DB 적재용 변환 함수 ────────────────────────────────────────
def row_transform(row: dict[str, str]) -> tuple[Any, ...]:
    """
    csv.DictReader 한 행(dict) → INSERT VALUES 파라미터 tuple.
    - temp : 소수점 반올림 후 int
    - storm : 'storm' 열 오타(stom) 자동 보정
    """
    mars_date = row["mars_date"]
    try:
        temp_val = round(float(row["temp"])) if row["temp"] else None
    except ValueError:
        print(f"[WARN] 잘못된 temp 값 '{row['temp']}' → NULL 처리")
        temp_val = None

    storm_raw = row.get("storm") or row.get("stom") or "0"
    try:
        storm_val = int(storm_raw)
    except ValueError:
        print(f"[WARN] 잘못된 storm 값 '{storm_raw}' → 0 처리")
        storm_val = 0

    return mars_date, temp_val, storm_val

# ───── 메인 로직 ────────────────────────────────────────────────────────
def main() -> None:
    # ── CSV 파일 존재 여부 체크 ──
    if not CSV_PATH.exists():
        print(f"[ERROR] CSV 파일을 찾을 수 없습니다: {CSV_PATH.resolve()}")
        sys.exit(1)

    with MySQLHelper(**DB_CONF) as db:
        # 1) CSV → DB 일괄 삽입
        try:
            inserted = db.bulk_insert_csv(
                CSV_PATH,
                table="mars_weather",
                columns=["mars_date", "temp", "storm"],
                transform=row_transform,
            )
        except FileNotFoundError:
            # bulk_insert_csv 내에서 CSV 경로 재확인하므로 이중 방어
            print(f"[ERROR] CSV 파일이 없습니다: {CSV_PATH.resolve()}")
            sys.exit(1)
        except Exception as exc:   # MySQL 에러 등
            print(f"[ERROR] CSV 적재 중 예외 발생: {exc}")
            sys.exit(1)

        print(f"[INFO] CSV 적재 완료 — {inserted} 행 삽입")

        # 2) 통계 조회
        db.execute(
            "SELECT COUNT(*), AVG(temp), SUM(storm) "
            "FROM mars_weather"
        )
        total_rows, avg_temp, storm_days = db.fetchone()

        print(
            "[INFO] 적재 후 통계 ─ "
            f"총 행: {total_rows}, 평균 온도: {avg_temp:.2f}, 폭풍일: {storm_days}"
        )

    # with 블록을 벗어나면 commit/rollback·close 자동 실행
    print("[DONE] 모든 작업이 정상적으로 완료되었습니다.")


if __name__ == "__main__":
    main()
