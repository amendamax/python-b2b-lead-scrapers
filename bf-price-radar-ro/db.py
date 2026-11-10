"""
db.py
Manager SQLite pentru istoricul de preturi, stocuri, benchmark-uri eMAG Marketplace si profilurile tehnice ale magazinelor.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class RadarDatabase:
    def __init__(self, db_path: str | Path = "radar_history.db") -> None:
        self.db_path = Path(db_path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    notes TEXT
                );

                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    store_domain TEXT NOT NULL,
                    normalized_sku TEXT NOT NULL,
                    brand TEXT NOT NULL,
                    category TEXT DEFAULT 'Echipament PV',
                    raw_title TEXT NOT NULL,
                    store_internal_sku TEXT NOT NULL,
                    current_price_ron REAL NOT NULL,
                    old_price_ron REAL,
                    in_stock INTEGER NOT NULL,
                    stock_label TEXT DEFAULT 'În stoc',
                    product_url TEXT NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                );

                CREATE INDEX IF NOT EXISTS idx_ph_run_store_sku
                    ON price_history(run_id, store_domain, normalized_sku);
                CREATE INDEX IF NOT EXISTS idx_ph_sku
                    ON price_history(normalized_sku);

                CREATE TABLE IF NOT EXISTS emag_benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    normalized_sku TEXT NOT NULL,
                    brand TEXT NOT NULL,
                    emag_lowest_price_ron REAL,
                    emag_buybox_seller TEXT NOT NULL,
                    emag_offers_count INTEGER NOT NULL DEFAULT 0,
                    emag_url TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                );

                CREATE INDEX IF NOT EXISTS idx_emag_run_sku
                    ON emag_benchmarks(run_id, normalized_sku);

                CREATE TABLE IF NOT EXISTS store_profiles (
                    store_domain TEXT PRIMARY KEY,
                    store_name TEXT,
                    detected_platform TEXT,
                    company_name TEXT,
                    cui TEXT,
                    reg_com TEXT,
                    phone TEXT,
                    email TEXT,
                    updated_at TEXT
                );
                """
            )

    def create_run(self, notes: str = "") -> int:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO runs (started_at, notes) VALUES (?, ?)",
                (now, notes),
            )
            return int(cur.lastrowid)

    def finish_run(self, run_id: int) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                "UPDATE runs SET finished_at = ? WHERE run_id = ?",
                (now, run_id),
            )

    def upsert_store_profile(self, profile: Dict[str, Any]) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO store_profiles (
                    store_domain, store_name, detected_platform,
                    company_name, cui, reg_com, phone, email, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(store_domain) DO UPDATE SET
                    store_name = excluded.store_name,
                    detected_platform = excluded.detected_platform,
                    company_name = excluded.company_name,
                    cui = excluded.cui,
                    reg_com = excluded.reg_com,
                    phone = excluded.phone,
                    email = excluded.email,
                    updated_at = excluded.updated_at
                """,
                (
                    profile.get("domain"),
                    profile.get("store_name"),
                    profile.get("detected_platform", "Custom"),
                    profile.get("company_name"),
                    profile.get("cui"),
                    profile.get("reg_com"),
                    profile.get("phone"),
                    profile.get("email"),
                    now,
                ),
            )

    def insert_price_records(self, run_id: int, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        now = datetime.now().isoformat(timespec="seconds")
        rows = []
        for r in records:
            rows.append(
                (
                    run_id,
                    r.get("timestamp", now),
                    r["store_domain"],
                    r["normalized_sku"],
                    r["brand"],
                    r.get("category", "Invertor / Baterie"),
                    r["raw_title"],
                    r.get("store_internal_sku") or f"SKU-{r['normalized_sku']}",
                    float(r["current_price_ron"]),
                    float(r["old_price_ron"]) if r.get("old_price_ron") else None,
                    1 if r.get("in_stock", True) else 0,
                    r.get("stock_label", "În stoc" if r.get("in_stock", True) else "Stoc Epuizat"),
                    r.get("product_url", ""),
                )
            )
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO price_history (
                    run_id, timestamp, store_domain, normalized_sku, brand,
                    category, raw_title, store_internal_sku, current_price_ron,
                    old_price_ron, in_stock, stock_label, product_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def insert_emag_benchmarks(self, run_id: int, benchmarks: List[Dict[str, Any]]) -> int:
        if not benchmarks:
            return 0
        now = datetime.now().isoformat(timespec="seconds")
        rows = [
            (
                run_id,
                b.get("timestamp", now),
                b["normalized_sku"],
                b["brand"],
                float(b["emag_lowest_price_ron"]) if b.get("emag_lowest_price_ron") is not None else None,
                b["emag_buybox_seller"],
                int(b.get("emag_offers_count", 0)),
                b.get("emag_url", ""),
            )
            for b in benchmarks
        ]
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO emag_benchmarks (
                    run_id, timestamp, normalized_sku, brand,
                    emag_lowest_price_ron, emag_buybox_seller,
                    emag_offers_count, emag_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def get_latest_run_id(self) -> Optional[int]:
        with self._connect() as conn:
            row = conn.execute("SELECT MAX(run_id) AS max_id FROM runs").fetchone()
            return int(row["max_id"]) if row and row["max_id"] is not None else None

    def get_previous_run_id(self, current_run_id: int) -> Optional[int]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT MAX(run_id) AS prev_id FROM runs WHERE run_id < ?",
                (current_run_id,),
            ).fetchone()
            return int(row["prev_id"]) if row and row["prev_id"] is not None else None

    def get_run_prices(self, run_id: int) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM price_history WHERE run_id = ?",
                (run_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_run_emag(self, run_id: int) -> Dict[str, Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM emag_benchmarks WHERE run_id = ?",
                (run_id,),
            ).fetchall()
            return {r["normalized_sku"]: dict(r) for r in rows}

    def get_store_profiles(self) -> Dict[str, Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM store_profiles").fetchall()
            return {r["store_domain"]: dict(r) for r in rows}
