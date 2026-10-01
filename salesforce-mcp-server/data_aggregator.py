"""
Data Aggregation Table and Local Cache.
Aggregates DocupletionForms submissions, Salesforce Leads, and Contacts
into an ultra-fast local SQLite database. 
Prevents hitting Salesforce API rate limits and provides lightning-fast querying for AI agents.
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
import config

logger = logging.getLogger(__name__)

class DataAggregator:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DB_PATH
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes the aggregation and cache tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Consolidated Aggregation Table for Leads & Docupletion Form Submissions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aggregated_records (
                    id TEXT PRIMARY KEY,
                    source_type TEXT NOT NULL,          -- 'Salesforce_Lead', 'Salesforce_Contact', 'Docupletion_Form'
                    external_id TEXT,                   -- Salesforce ID or Docupletion Submission ID
                    name TEXT,
                    email TEXT,
                    company TEXT,
                    status TEXT,
                    form_name TEXT,
                    raw_payload TEXT,                   -- JSON payload of all fields
                    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)

            # Query cache table for reducing Salesforce API usage
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_cache (
                    query_hash TEXT PRIMARY KEY,
                    soql TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Metadata and Sync Metrics Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sync_type TEXT NOT NULL,
                    records_ingested INTEGER,
                    status TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info("Data Aggregator Database initialized at %s", self.db_path)

    def upsert_record(self, source_type: str, external_id: str, name: str = None,
                      email: str = None, company: str = None, status: str = None,
                      form_name: str = None, payload: Dict[str, Any] = None,
                      created_at: str = None) -> str:
        """Inserts or updates a record in the aggregated table."""
        rec_id = f"{source_type}_{external_id}"
        payload_str = json.dumps(payload or {}, ensure_ascii=False)
        now = datetime.utcnow().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO aggregated_records 
                (id, source_type, external_id, name, email, company, status, form_name, raw_payload, last_synced_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    email = excluded.email,
                    company = excluded.company,
                    status = excluded.status,
                    form_name = excluded.form_name,
                    raw_payload = excluded.raw_payload,
                    last_synced_at = excluded.last_synced_at
            """, (rec_id, source_type, external_id, name, email, company, status, form_name, payload_str, now, created_at or now))
            conn.commit()
        return rec_id

    def bulk_ingest_salesforce_records(self, object_type: str, records: List[Dict[str, Any]]) -> int:
        """Ingests a list of Salesforce records into the aggregation table."""
        count = 0
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            for r in records:
                sf_id = r.get("Id")
                if not sf_id:
                    continue
                rec_id = f"Salesforce_{object_type}_{sf_id}"
                name = r.get("Name") or f"{r.get('FirstName', '')} {r.get('LastName', '')}".strip()
                email = r.get("Email")
                company = r.get("Company") or r.get("Account", {}).get("Name") if isinstance(r.get("Account"), dict) else None
                status = r.get("Status") or r.get("LeadStatus") or "Active"
                created_at = r.get("CreatedDate") or now
                payload_str = json.dumps(r, ensure_ascii=False)

                cursor.execute("""
                    INSERT INTO aggregated_records 
                    (id, source_type, external_id, name, email, company, status, form_name, raw_payload, last_synced_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name = excluded.name,
                        email = excluded.email,
                        company = excluded.company,
                        status = excluded.status,
                        raw_payload = excluded.raw_payload,
                        last_synced_at = excluded.last_synced_at
                """, (rec_id, f"Salesforce_{object_type}", sf_id, name, email, company, status, object_type, payload_str, now, created_at))
                count += 1
            
            # Log sync metric
            cursor.execute("""
                INSERT INTO sync_metrics (sync_type, records_ingested, status, details)
                VALUES (?, ?, ?, ?)
            """, (f"Sync_{object_type}", count, "SUCCESS", f"Ingested {count} {object_type} records"))
            conn.commit()
        logger.info("Bulk ingested %d records for %s", count, object_type)
        return count

    def query_records(self, source_type: str = None, status: str = None, 
                      search_term: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Queries the aggregated table with flexible filters."""
        query = "SELECT id, source_type, external_id, name, email, company, status, form_name, last_synced_at, created_at FROM aggregated_records WHERE is_active = 1"
        params = []

        if source_type:
            query += " AND source_type LIKE ?"
            params.append(f"%{source_type}%")
        if status:
            query += " AND status = ?"
            params.append(status)
        if search_term:
            query += " AND (name LIKE ? OR email LIKE ? OR company LIKE ?)"
            term = f"%{search_term}%"
            params.extend([term, term, term])

        query += " ORDER BY last_synced_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_aggregation_summary(self) -> Dict[str, Any]:
        """Returns consolidated KPI metrics for the aggregated dataset."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM aggregated_records WHERE is_active = 1")
            total_records = cursor.fetchone()[0]

            cursor.execute("SELECT source_type, COUNT(*) as cnt FROM aggregated_records WHERE is_active = 1 GROUP BY source_type")
            by_source = {row["source_type"]: row["cnt"] for row in cursor.fetchall()}

            cursor.execute("SELECT status, COUNT(*) as cnt FROM aggregated_records WHERE is_active = 1 GROUP BY status")
            by_status = {row["status"]: row["cnt"] for row in cursor.fetchall()}

            cursor.execute("SELECT MAX(last_synced_at) FROM aggregated_records")
            last_sync = cursor.fetchone()[0]

            return {
                "total_records": total_records,
                "by_source": by_source,
                "by_status": by_status,
                "last_sync": last_sync
            }
