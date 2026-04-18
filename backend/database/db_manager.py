from __future__ import annotations

import json
import os
import sqlite3
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import psycopg2
    import psycopg2.extras
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


@dataclass(slots=True)
class Migration:
    version: str
    sql_path: Path


class DBManager:
    def __init__(self, db_path: Path | str, migrations_dir: Path | str) -> None:
        self.db_path = Path(db_path)
        self.migrations_dir = Path(migrations_dir)
        self.database_url = os.environ.get("DATABASE_URL")
        self.is_postgres = bool(self.database_url and self.database_url.startswith("postgres"))
        
        if self.is_postgres and not HAS_PSYCOPG2:
            raise RuntimeError("DATABASE_URL is set for Postgres but psycopg2-binary is not installed")
            
        if not self.is_postgres:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        self.migrate()

    @contextmanager
    def get_connection(self):
        if self.is_postgres:
            conn = psycopg2.connect(self.database_url)
            try:
                yield conn
            finally:
                conn.close()
        else:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()

    @contextmanager
    def get_cursor(self):
        with self.get_connection() as conn:
            if self.is_postgres:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                try:
                    yield conn, cur
                finally:
                    cur.close()
            else:
                cur = conn.cursor()
                try:
                    yield conn, cur
                finally:
                    cur.close()

    def _normalize_sql(self, sql: str) -> str:
        if self.is_postgres:
            return sql.replace("?", "%s")
        return sql

    def execute(self, sql: str, params: Iterable[Any] = ()) -> None:
        sql = self._normalize_sql(sql)
        with self.get_cursor() as (conn, cur):
            cur.execute(sql, tuple(params))
            conn.commit()

    def insert_returning_id(self, sql: str, params: Iterable[Any] = ()) -> int:
        sql = self._normalize_sql(sql)
        with self.get_cursor() as (conn, cur):
            if self.is_postgres:
                if "RETURNING id" not in sql.upper():
                    sql = sql.rstrip("; ") + " RETURNING id"
                cur.execute(sql, tuple(params))
                res = cur.fetchone()
                conn.commit()
                return res["id"] if res else 0
            else:
                cur.execute(sql, tuple(params))
                last_id = cur.lastrowid
                conn.commit()
                return last_id

    def executemany(self, sql: str, params: Iterable[Iterable[Any]]) -> None:
        sql = self._normalize_sql(sql)
        with self.get_cursor() as (conn, cur):
            cur.executemany(sql, [tuple(row) for row in params])
            conn.commit()

    def fetch_one(self, sql: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
        sql = self._normalize_sql(sql)
        with self.get_cursor() as (conn, cur):
            cur.execute(sql, tuple(params))
            row = cur.fetchone()
            return dict(row) if row else None

    def fetch_all(self, sql: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
        sql = self._normalize_sql(sql)
        with self.get_cursor() as (conn, cur):
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            return [dict(row) for row in rows]

    def migrate(self) -> None:
        with self.get_cursor() as (conn, cur):
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
                """
            )
            conn.commit()
            
            cur.execute("SELECT version FROM schema_migrations")
            applied = {row["version"] for row in cur.fetchall()}
            
            for migration in self._discover_migrations():
                if migration.version in applied:
                    continue
                    
                script = migration.sql_path.read_text(encoding="utf-8")
                
                # Dynamic translation of AUTOINCREMENT for Postgres
                if self.is_postgres:
                    script = script.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
                
                if self.is_postgres:
                    # Postgres doesn't easily support executescript within a transaction block if it has multiple statements separated by semicolon out of the box in one cur.execute(), but psycopg2 ignores multiple statements inside strings if delimited correctly. Actually, cur.execute works fine for multi-statement scripts in psycopg2.
                    cur.execute(script)
                else:
                    conn.executescript(script)
                    
                cur.execute(
                    self._normalize_sql("INSERT INTO schema_migrations(version, applied_at) VALUES(?, ?)"),
                    (migration.version, datetime.now(timezone.utc).isoformat()),
                )
            conn.commit()

    def _discover_migrations(self) -> list[Migration]:
        migrations: list[Migration] = []
        for path in sorted(self.migrations_dir.glob("*.sql")):
            migrations.append(Migration(version=path.stem, sql_path=path))
        return migrations

    def upsert_metric(self, name: str, value: dict[str, Any]) -> None:
        sql = """
            INSERT INTO metrics(name, payload, updated_at)
            VALUES(?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                payload=excluded.payload,
                updated_at=excluded.updated_at
        """
        self.execute(sql, (name, json.dumps(value, default=str), datetime.now(timezone.utc).isoformat()))

    def get_metric(self, name: str) -> dict[str, Any]:
        row = self.fetch_one("SELECT payload FROM metrics WHERE name = ?", (name,))
        if not row:
            return {}
        return json.loads(row["payload"])

    def snapshot_before_prune(self) -> None:
        """Saves a lightweight analytics snapshot of trades before data is truncated."""
        try:
            total_trades = self.fetch_one("SELECT COUNT(*) as count FROM trades")["count"]
            win_loss = self.fetch_all("SELECT realized_pnl FROM trades")
            
            wins = sum(1 for row in win_loss if row["realized_pnl"] > 0)
            losses = sum(1 for row in win_loss if row["realized_pnl"] < 0)
            avg_pnl = sum(row["realized_pnl"] for row in win_loss) / max(total_trades, 1)
            
            summary = {
                "total_trades": total_trades,
                "wins": wins,
                "losses": losses,
                "win_rate": round(wins / max(total_trades, 1), 4),
                "avg_pnl": round(avg_pnl, 4),
                "snapshot_time": datetime.now(timezone.utc).isoformat()
            }
            self.upsert_metric("pruning_snapshot", summary)
            logging.getLogger("aurora").info(f"Database pre-prune snapshot saved: {summary}")
        except Exception as e:
            logging.getLogger("aurora").error(f"Failed to snapshot state before pruning: {e}")

    def prune_database(self) -> None:
        """Truncates heavy telemetry tables to prevent cloud database bloat."""
        tables_to_prune = [
            "market_data",
            "features",
            "decisions",
            "intents",
            "trades",
            "orders"
        ]
        
        logging.getLogger("aurora").info(f"Starting scheduled database truncation for {len(tables_to_prune)} tables...")
        with self.get_cursor() as (conn, cur):
            for table in tables_to_prune:
                try:
                    if self.is_postgres:
                        cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
                    else:
                        cur.execute(f"DELETE FROM {table};")
                except Exception as e:
                    logging.getLogger("aurora").warning(f"Error pruning table {table}: {e}")
            conn.commit()
            
        if not self.is_postgres:
            self.execute("VACUUM;")

