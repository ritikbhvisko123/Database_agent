# PostgreSQL Database Navigator MCP Server

This MCP server gives Claude Desktop read-only access to the local PostgreSQL
database `company_ai`.

## Tools

- `list_database_tables`: lists public tables in the connected database.
- `inspect_table_schema`: describes columns, data types, nullability, defaults,
  and primary-key markers for one table.
- `execute_read_only_query`: executes a validated `SELECT` or `WITH` query and
  returns at most 150 rows.

## Setup

```powershell
cd C:\Users\HP\Desktop\learning\mcp_claude\mcp-postgres-navigator
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

The database connection is stored in `configuration/environment.env`:

```text
DATABASE_URL=postgresql://postgres:Vitm%400858@localhost:5432/company_ai
```

## Claude Desktop Configuration

Edit:

```text
%APPDATA%\Claude\claude_desktop_config.json
```

Use this server entry:

```json
{
  "mcpServers": {
    "postgres-company-navigator": {
      "command": "C:\\Users\\HP\\Desktop\\learning\\mcp_claude\\mcp-postgres-navigator\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\HP\\Desktop\\learning\\mcp_claude\\mcp-postgres-navigator\\main.py"
      ],
      "env": {
        "DATABASE_URL": "postgresql://postgres:abc%40123@localhost:5432/company_ai"
      }
    }
  }
}
```

After saving, fully quit Claude Desktop from the system tray and reopen it.
