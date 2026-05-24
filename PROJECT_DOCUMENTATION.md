# PostgreSQL Database Navigator MCP Server

## 1. What This Project Does

This project connects Claude Desktop to your local PostgreSQL database named
`company_ai`.

Normally, Claude cannot directly access your computer database. This project
solves that by creating a local MCP server. MCP means Model Context Protocol. It
is a standard way for Claude Desktop to use external tools.

With this project, Claude can:

- See which tables exist in your PostgreSQL database.
- Inspect the schema of a table before writing SQL.
- Run safe read-only SQL queries.
- Convert database rows into clear human answers.

The current target tables are:

- `employees`
- `students`

The server is designed for read-only database access. It does not allow Claude
to insert, update, delete, drop, or modify database data.

## 2. Project Location

The project folder is:

```text
C:\Users\HP\Desktop\learning\mcp_claude\mcp-postgres-navigator
```

The Claude Desktop configuration file is:

```text
C:\Users\HP\AppData\Roaming\Claude\claude_desktop_config.json
```

## 3. Folder Structure

```text
mcp-postgres-navigator/
│
├── venv/
│
├── configuration/
│   └── environment.env
│
├── core/
│   ├── __init__.py
│   ├── connection_engine.py
│   └── server_manifest.py
│
├── tools/
│   ├── __init__.py
│   ├── discovery_tools.py
│   └── query_tools.py
│
├── README.md
├── PROJECT_DOCUMENTATION.md
├── requirements.txt
└── main.py
```

## 4. File Usage

### `main.py`

This is the application entry point.

Claude Desktop starts this file when it loads the MCP server.

Its job is simple:

1. Import the MCP server object from `core/server_manifest.py`.
2. Start the MCP server loop with `mcp.run()`.

Claude Desktop communicates with this process through standard input/output.

### `requirements.txt`

This file lists the Python packages required by the project.

Current dependencies:

```text
fastmcp>=0.4.1
psycopg2-binary>=2.9.9
```

`fastmcp` is used to create the MCP server and expose tools to Claude.

`psycopg2-binary` is used to connect Python to PostgreSQL.

### `configuration/environment.env`

This file stores the PostgreSQL database connection string.

Current value:

```text
DATABASE_URL=postgresql://postgres:Vitm%400858@localhost:5432/company_ai
```

The password contains `@`, so it must be URL encoded as `%40`.

Plain password:

```text
abc@123
```

URL-safe password:

```text
abc%40123
```

### `core/__init__.py`

This file marks the `core` directory as a Python package.

It does not contain business logic.

### `core/connection_engine.py`

This file manages PostgreSQL connectivity.

Main responsibilities:

- Load `DATABASE_URL` from `configuration/environment.env`.
- Create a PostgreSQL connection pool.
- Provide a reusable `fetch_all()` function.
- Close the connection pool when needed.

Important functions:

```text
get_database_url()
```

Reads the database URL from the environment file or system environment.

```text
get_connection_pool()
```

Creates and reuses a PostgreSQL connection pool.

```text
fetch_all(sql, params)
```

Runs a SQL query and returns rows as Python dictionaries.

```text
close_connection_pool()
```

Closes all open database connections.

### `core/server_manifest.py`

This file creates the FastMCP server.

It registers all available tools:

- Discovery tools from `tools/discovery_tools.py`
- Query tools from `tools/query_tools.py`

The MCP server name is:

```text
postgres-company-navigator
```

Claude Desktop sees this server name when it loads the local MCP config.

### `tools/__init__.py`

This file marks the `tools` directory as a Python package.

It does not contain business logic.

### `tools/discovery_tools.py`

This file contains tools that help Claude understand the database structure.

It exposes two MCP tools.

#### Tool: `list_database_tables`

Purpose:

Lists all base tables in the PostgreSQL `public` schema.

Claude uses this first when it needs to know what tables exist.

Example result:

```text
Public tables:
- employees
- students
```

#### Tool: `inspect_table_schema`

Purpose:

Shows the columns and metadata for a selected table.

Input:

```text
table_name
```

Example:

```text
inspect_table_schema("employees")
```

It returns information like:

- Column name
- PostgreSQL data type
- Whether the column allows null values
- Default value
- Primary key marker, if available

This prevents Claude from guessing wrong column names.

### `tools/query_tools.py`

This file contains the safe query execution tool.

#### Tool: `execute_read_only_query`

Purpose:

Runs a read-only SQL query against PostgreSQL.

Input:

```text
sql
```

Example:

```sql
SELECT * FROM employees LIMIT 5;
```

Security behavior:

- Allows queries starting with `SELECT`.
- Allows queries starting with `WITH`.
- Blocks write/modification keywords.
- Blocks multiple SQL statements.
- Wraps the query and applies a maximum row limit.

Maximum returned rows:

```text
150
```

Blocked SQL examples:

```sql
DELETE FROM employees;
UPDATE employees SET salary = 1000;
DROP TABLE students;
CREATE TABLE test_table (...);
```

The tool returns JSON containing:

- `row_count`
- `max_rows`
- `rows`

## 5. Database Configuration

Database details:

```text
Database Engine: PostgreSQL
Host: localhost
Port: 5432
Database Name: company_ai
User: postgres
Password: Vitm@0858
```

Connection URL:

```text
postgresql://postgres:abc%40123@localhost:5432/company_ai
```

PostgreSQL must be running locally for this MCP server to work.

## 6. Claude Desktop Configuration

Claude Desktop reads local MCP servers from:

```text
C:\Users\HP\AppData\Roaming\Claude\claude_desktop_config.json
```

Your config includes:

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

Important:

- This works in Claude Desktop.
- This does not work in Claude browser chat by itself.
- Do not use "Add connectors" for this local MCP server.
- Local MCP tools are loaded from the JSON config when Claude Desktop starts.

## 7. Complete Workflow

### Step 1: Claude Desktop Starts

When Claude Desktop opens, it reads:

```text
claude_desktop_config.json
```

It finds the server named:

```text
postgres-company-navigator
```

Then it starts:

```text
C:\Users\HP\Desktop\learning\mcp_claude\mcp-postgres-navigator\venv\Scripts\python.exe
```

with this argument:

```text
C:\Users\HP\Desktop\learning\mcp_claude\mcp-postgres-navigator\main.py
```

### Step 2: Python Starts the MCP Server

`main.py` imports the server from:

```text
core/server_manifest.py
```

Then it runs:

```text
mcp.run()
```

### Step 3: Tools Are Registered

`server_manifest.py` registers tools from:

```text
tools/discovery_tools.py
tools/query_tools.py
```

Claude Desktop now knows these tools exist:

```text
list_database_tables
inspect_table_schema
execute_read_only_query
```

### Step 4: User Asks Claude a Question

Example user prompt:

```text
Show me the top 5 employees.
```

Claude decides that it needs database access.

### Step 5: Claude Checks Database Structure

Claude may call:

```text
list_database_tables
```

Then it may call:

```text
inspect_table_schema
```

This helps Claude understand which tables and columns are available.

### Step 6: Claude Builds SQL

Claude creates a read-only SQL query, for example:

```sql
SELECT * FROM employees LIMIT 5;
```

### Step 7: Query Tool Validates SQL

`execute_read_only_query` checks that the query is safe.

It rejects dangerous commands like:

- `INSERT`
- `UPDATE`
- `DELETE`
- `DROP`
- `ALTER`
- `CREATE`
- `TRUNCATE`

### Step 8: Query Runs Against PostgreSQL

The server uses the connection pool from:

```text
core/connection_engine.py
```

It sends the query to PostgreSQL and receives rows.

### Step 9: Rows Are Returned to Claude

The rows are returned as JSON.

Claude reads the JSON and explains the answer in natural language.

## 8. How to Test

### Test 1: Check Python Dependencies

Run this in PowerShell:

```powershell
cd C:\Users\HP\Desktop\learning\mcp_claude\mcp-postgres-navigator
.\venv\Scripts\python.exe -c "from core.server_manifest import mcp; print(type(mcp).__name__)"
```

Expected output:

```text
FastMCP
```

### Test 2: Check Database Connection

Run:

```powershell
cd C:\Users\HP\Desktop\learning\mcp_claude\mcp-postgres-navigator
.\venv\Scripts\python.exe -c "from core.connection_engine import fetch_all; print(fetch_all('SELECT table_name FROM information_schema.tables WHERE table_schema=%s ORDER BY table_name', ('public',)))"
```

Expected output should include:

```text
employees
students
```

### Test 3: Check Claude Desktop MCP Tools

Restart Claude Desktop completely.

Ask:

```text
List the MCP tools you have available.
```

Expected result should include:

```text
postgres-company-navigator
list_database_tables
inspect_table_schema
execute_read_only_query
```

### Test 4: Use Database Tools in Claude

Ask Claude:

```text
Use list_database_tables.
```

Then:

```text
Inspect the schema of the employees table.
```

Then:

```text
Run a read-only query: SELECT * FROM employees LIMIT 5;
```

## 9. Common Problems and Fixes

### Problem: Claude Searches Connectors Instead of Using MCP

Cause:

Claude is using the online connector registry, not the local MCP server.

Fix:

- Use Claude Desktop, not only browser Claude.
- Do not click "Add connectors".
- Restart Claude Desktop after editing config.
- Ask for MCP tools, not connector search.

Good prompt:

```text
List the MCP tools you have available.
```

Bad prompt:

```text
Search for postgres-company-navigator connector.
```

### Problem: Claude Does Not See `postgres-company-navigator`

Possible causes:

- Claude Desktop was not restarted after config changes.
- The JSON config file has a syntax problem.
- The JSON file has a hidden UTF-8 BOM character.
- The Python path is wrong.
- The server crashes during startup.

Fix:

Check the config file:

```text
C:\Users\HP\AppData\Roaming\Claude\claude_desktop_config.json
```

Check logs:

```text
C:\Users\HP\AppData\Roaming\Claude\logs\main.log
```

### Problem: `Unexpected token` in Claude Logs

Cause:

The config file may contain an invisible UTF-8 BOM character.

Fix:

Rewrite the JSON as UTF-8 without BOM.

This was already fixed once in this project.

### Problem: Database Connection Fails

Possible causes:

- PostgreSQL service is not running.
- Database `company_ai` does not exist.
- Password is wrong.
- Port `5432` is blocked or changed.
- Tables have not been created.

Check that PostgreSQL is running and that these tables exist:

```text
employees
students
```

### Problem: Query Is Rejected

Cause:

The query contains blocked write keywords or multiple statements.

Allowed:

```sql
SELECT * FROM employees LIMIT 5;
```

Rejected:

```sql
SELECT * FROM employees; SELECT * FROM students;
```

Rejected:

```sql
UPDATE employees SET salary = 1000;
```

## 10. Security Notes

This project intentionally limits Claude to read-only access.

The query tool blocks common write and administrative SQL commands.

Safety limits:

- Only `SELECT` and `WITH` queries are accepted.
- Multiple SQL statements are blocked.
- Maximum returned rows are capped at 150.
- Table inspection validates table names as simple identifiers.

Important:

This is a helpful safety layer, but do not expose this server publicly without
additional authentication, network controls, and SQL hardening.

## 11. Recommended Claude Prompts

List tables:

```text
Use list_database_tables.
```

Inspect employees:

```text
Inspect the schema of the employees table.
```

Inspect students:

```text
Inspect the schema of the students table.
```

Show sample employees:

```text
Run a read-only query: SELECT * FROM employees LIMIT 5;
```

Show sample students:

```text
Run a read-only query: SELECT * FROM students LIMIT 5;
```

Ask Claude to reason with schema first:

```text
Inspect the employees and students schemas, then write and run a safe read-only
query to summarize the data.
```

## 12. Maintenance Guidelines

### If Database Credentials Change

Update:

```text
mcp-postgres-navigator/configuration/environment.env
```

And also update the `env.DATABASE_URL` value in:

```text
C:\Users\HP\AppData\Roaming\Claude\claude_desktop_config.json
```

Then restart Claude Desktop.

### If Project Folder Moves

Update these paths in Claude config:

```text
command
args
```

Then restart Claude Desktop.

### If New Tables Are Added

No code change is needed.

Claude can call:

```text
list_database_tables
inspect_table_schema
```

to discover the new tables.

### If You Add New Tools

Create or update a file inside:

```text
tools/
```

Then register the tool in:

```text
core/server_manifest.py
```

Restart Claude Desktop after changing server code.

## 13. End-to-End Example

User asks Claude:

```text
Which employees are in the database? Show 5 examples.
```

Claude workflow:

1. Calls `list_database_tables`.
2. Finds `employees`.
3. Calls `inspect_table_schema("employees")`.
4. Builds SQL:

```sql
SELECT * FROM employees LIMIT 5;
```

5. Calls `execute_read_only_query`.
6. Receives JSON rows.
7. Responds with a readable summary.

## 14. Current Project Status

Completed:

- Project folder created.
- Python virtual environment created.
- Dependencies installed.
- PostgreSQL connection tested.
- `employees` and `students` tables detected.
- Claude Desktop config fixed.
- UTF-8 BOM issue fixed.
- Claude Desktop confirmed the MCP tools are loaded.

Available MCP tools:

```text
list_database_tables
inspect_table_schema
execute_read_only_query
```

The project is ready to use with Claude Desktop.
