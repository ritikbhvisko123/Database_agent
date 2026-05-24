"""Schema discovery tools exposed to Claude through MCP."""

from __future__ import annotations

import re
from typing import Any

import mcp

from core.connection_engine import fetch_all
from duckduckgo_search import DDGS


_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_table_name(table_name: str) -> str:
    normalized = table_name.strip()
    if not _IDENTIFIER_RE.fullmatch(normalized):
        raise ValueError("Table name must be a simple PostgreSQL identifier.")
    return normalized


def register_discovery_tools(mcp: Any) -> None:
    @mcp.tool()
    def list_database_tables() -> str:
        """List tables available in the public PostgreSQL schema."""
        rows = fetch_all(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
            """
        )

        if not rows:
            return "No public tables were found in the connected database."

        table_names = [row["table_name"] for row in rows]
        return "Public tables:\n" + "\n".join(f"- {name}" for name in table_names)

    @mcp.tool()
    def inspect_table_schema(table_name: str) -> str:
        """Inspect columns, data types, nullability, and key metadata for a table."""
        safe_table_name = _validate_table_name(table_name)

        rows = fetch_all(
            """
            SELECT
                c.ordinal_position,
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.column_default,
                CASE WHEN tc.constraint_type = 'PRIMARY KEY' THEN 'YES' ELSE 'NO' END
                    AS is_primary_key
            FROM information_schema.columns c
            LEFT JOIN information_schema.key_column_usage kcu
                ON c.table_schema = kcu.table_schema
               AND c.table_name = kcu.table_name
               AND c.column_name = kcu.column_name
            LEFT JOIN information_schema.table_constraints tc
                ON kcu.constraint_schema = tc.constraint_schema
               AND kcu.constraint_name = tc.constraint_name
               AND tc.constraint_type = 'PRIMARY KEY'
            WHERE c.table_schema = 'public'
              AND c.table_name = %s
            ORDER BY c.ordinal_position;
            """,
            (safe_table_name,),
        )

        if not rows:
            return f"No table named '{safe_table_name}' was found in the public schema."

        lines = [f"Schema for public.{safe_table_name}:"]
        for row in rows:
            nullable = "nullable" if row["is_nullable"] == "YES" else "not nullable"
            primary_key = " primary key" if row["is_primary_key"] == "YES" else ""
            default = f" default={row['column_default']}" if row["column_default"] else ""
            lines.append(
                f"- {row['column_name']}: {row['data_type']}, {nullable}{primary_key}{default}"
            )

        return "\n".join(lines)



    @mcp.tool()
    def web_search(query: str, max_results: int = 5) -> str:
        """Execute a live web search using DuckDuckGo to fetch up-to-date information or answers."""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            
            if not results:
                return f"No search results found for query: '{query}'"
            
            lines = [f"Search results for: '{query}':"]
            for idx, result in enumerate(results, start=1):
                title = result.get("title", "No Title")
                href = result.get("href", "No URL")
                body = result.get("body", "No Description")
                lines.append(f"\n{idx}. {title}\n   URL: {href}\n   Snippet: {body}")
                
            return "\n".join(lines)
            
        except Exception as e:
            return f"An error occurred while executing the web search: {str(e)}"
        


    @mcp.tool()
    def open_local_media_file(file_path: str) -> str:
        """Open a local image, video, or audio file using the default Windows system application.
        
        Provide the absolute, full path to the file (e.g., 'C:\\Users\\Username\\Videos\\edit_clip.mp4').
        """
        import os
        import platform

        # Clear any accidental enclosing quotes the LLM or user might pass
        clean_path = file_path.strip("'\"")

        # Basic validation: Check if the file exists on your local drive
        if not os.path.exists(clean_path):
            return f"Error: The system could not find the file at path: '{clean_path}'. Please check the path and try again."

        # Verify the file isn't a directory
        if os.path.isdir(clean_path):
            return f"Error: The path '{clean_path}' is a folder directory, not a specific media file."

        try:
            # Check for Windows system environment
            if platform.system() == "Windows":
                # os.startfile acts exactly like double-clicking the file in Windows File Explorer
                os.startfile(clean_path)
                return f"Successfully sent open signal. Windows is opening the file: '{os.path.basename(clean_path)}'"
            
            # Fallbacks for macOS and Linux just in case you switch environments later
            elif platform.system() == "Darwin":  # macOS
                os.system(f"open '{clean_path}'")
                return f"Successfully opened file on macOS: '{os.path.basename(clean_path)}'"
            else:  # Linux distributions
                os.system(f"xdg-open '{clean_path}'")
                return f"Successfully opened file on Linux: '{os.path.basename(clean_path)}'"

        except Exception as e:
            return f"An operational error occurred while trying to open the file: {str(e)}"
