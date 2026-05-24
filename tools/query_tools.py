"""Read-only PostgreSQL query execution tool."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from core.connection_engine import fetch_all


MAX_ROWS = 150
_READ_ONLY_START_RE = re.compile(r"^\s*(select|with)\b", re.IGNORECASE | re.DOTALL)
_FORBIDDEN_RE = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|merge|call|"
    r"execute|copy|vacuum|analyze|refresh|reindex|lock|set|reset)\b",
    re.IGNORECASE,
)


def _json_default(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return str(value)


def _validate_read_only_sql(sql: str) -> str:
    cleaned = sql.strip()
    if not cleaned:
        raise ValueError("SQL query cannot be empty.")

    if not _READ_ONLY_START_RE.match(cleaned):
        raise ValueError("Only SELECT or WITH read-only queries are allowed.")

    without_trailing_semicolon = cleaned[:-1].strip() if cleaned.endswith(";") else cleaned
    if ";" in without_trailing_semicolon:
        raise ValueError("Only one SQL statement is allowed.")

    if _FORBIDDEN_RE.search(cleaned):
        raise ValueError("Query contains a keyword that is not allowed in read-only mode.")

    return without_trailing_semicolon


def register_query_tools(mcp: Any) -> None:
    @mcp.tool()
    def execute_read_only_query(sql: str) -> str:
        """Execute a read-only SELECT query and return up to 150 rows as JSON."""
        try:
            safe_sql = _validate_read_only_sql(sql)
            limited_sql = f"SELECT * FROM ({safe_sql}) AS mcp_read_only_query LIMIT %s"
            rows = fetch_all(limited_sql, (MAX_ROWS,))
        except Exception as exc:
            return f"Query error: {exc}"

        payload = {
            "row_count": len(rows),
            "max_rows": MAX_ROWS,
            "rows": rows,
        }
        return json.dumps(payload, default=_json_default, indent=2)
