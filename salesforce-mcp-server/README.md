# Salesforce MCP Server & Data Aggregation Table

**Milestone 2 Deliverable for DocupletionForms & James Polk**  
*Built by VasileDev Group (amendamax@gmail.com)*

A production-ready **Model Context Protocol (MCP)** server conforming to the **MCP 2.x** standard (`MCPServer`), enabling AI assistants (Claude Desktop, Cursor, Custom AI Agents) to interact directly with **Salesforce CRM** and **DocupletionForms** datasets, backed by a high-speed local **Data Aggregation Table**.

---

## Key Features

1. **Full Salesforce CRUD & Intelligence via 9 MCP Tools**:
   - `salesforce_status`: Check live connection status & aggregate telemetry.
   - `salesforce_query`: Execute arbitrary SOQL queries with lightning speed.
   - `salesforce_describe_object`: Inspect schema, metadata, custom fields (`Docupletion_Form__c`).
   - `salesforce_create_record`: Create Leads, Contacts, or custom submissions with instant cache indexing.
   - `salesforce_update_record`: Update records seamlessly and sync local cache.
   - `salesforce_search_sosl`: Full text search across all CRM objects in one shot.
   - `sync_salesforce_to_aggregation_table`: Pulls recent records into local cache to eliminate API limits.
   - `query_aggregation_table`: Query cached records offline with zero Salesforce API cost.
   - `get_aggregation_kpis`: Real-time KPI telemetry on lead status counts and submission volume.

2. **Consolidated High-Speed Data Aggregation Table**:
   - High-speed local SQLite table (`data_aggregation.db`).
   - Ingests and aggregates Salesforce Leads, Contacts, and Docupletion form submissions.
   - Eliminates Salesforce API limit bottlenecks by serving read queries in sub-millisecond time.

3. **Dual-Mode Reliability**:
   - **Live Production Mode**: Connects directly to `centineltrust.my.salesforce.com` via `simple-salesforce`.
   - **Graceful Fallback Mode**: If credentials or permissions are being configured, the server operates safely without crashing.

---

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Copy `.env.example` to `.env` and fill in the credentials:
```ini
SALESFORCE_USERNAME=amendamax@gmail.com
SALESFORCE_PASSWORD=YourPassword
SALESFORCE_SECURITY_TOKEN=YourSecurityToken
SALESFORCE_DOMAIN=centineltrust.my.salesforce.com
```

### 3. Run Self-Test
```bash
python test_server.py
```

### 4. Connect to Claude Desktop
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "salesforce-docupletion": {
      "command": "python",
      "args": [
        "C:\\Users\\bratu\\Documents\\antigravity\\amazing-borg\\salesforce-mcp-server\\server.py"
      ]
    }
  }
}
```

---

## Architecture Diagram

```
┌───────────────────────────┐         ┌──────────────────────────────────────┐
│  Claude Desktop / AI MCP  │ ◄─────► │   Salesforce MCP Server (server.py)  │
└───────────────────────────┘ (stdio) └──────────────────┬───────────────────┘
                                                         │
                             ┌───────────────────────────┴───────────────────────────┐
                             ▼                                                       ▼
                ┌─────────────────────────┐                             ┌─────────────────────────┐
                │   salesforce_client.py  │                             │   data_aggregator.py    │
                │   (simple-salesforce)   │                             │   (SQLite Local Engine) │
                └────────────┬────────────┘                             └────────────┬────────────┘
                             │                                                       │
                             ▼                                                       ▼
                ┌─────────────────────────┐                             ┌─────────────────────────┐
                │ centineltrust.my.sales- │                             │   data_aggregation.db   │
                │ force.com (REST / SOQL) │                             │   (Zero API Cost Cache) │
                └─────────────────────────┘                             └─────────────────────────┘
```
