"""
Salesforce & Docupletion Model Context Protocol (MCP) Server.
Exposes tools for SOQL querying, record management, schema discovery,
and local high-speed data aggregation to AI assistants (Claude, Cursor, Agents).
"""
import sys
import logging
from typing import Any, Dict, List, Optional
try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as MCPServer
from salesforce_client import SalesforceClient
from data_aggregator import DataAggregator
import config

# Configure logging to stderr (stdio transport requires clean stdout for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("SalesforceMCPServer")

# Initialize MCP Server (v2.x MCPServer with backward-compatible fallback)
mcp = MCPServer(
    name=config.SERVER_NAME,
    instructions=(
        "Salesforce & DocupletionForms MCP Server. Provides intelligent tools for querying "
        "Salesforce CRM (Leads, Contacts, Custom Objects), executing SOQL/SOSL, "
        "creating/updating records, and querying the local high-speed Data Aggregation Table."
    ),
    version=config.SERVER_VERSION
)

# Initialize Core Services
sf_client = SalesforceClient()
aggregator = DataAggregator()

# Attempt connection on startup
sf_client.connect()

@mcp.tool()
def salesforce_status() -> Dict[str, Any]:
    """Checks the live connection status to the Salesforce instance and local aggregator."""
    summary = aggregator.get_aggregation_summary()
    return {
        "salesforce_connected": sf_client.is_connected,
        "instance_domain": sf_client.domain,
        "username": sf_client.username,
        "mode": "Live Production" if sf_client.is_connected else "Development Mock Mode",
        "aggregated_data_summary": summary
    }

@mcp.tool()
def salesforce_query(soql: str) -> Dict[str, Any]:
    """Executes a SOQL (Salesforce Object Query Language) query.
    Example: 'SELECT Id, Name, Email, Status FROM Lead LIMIT 10'
    """
    logger.info("MCP Tool salesforce_query called: %s", soql)
    return sf_client.query(soql)

@mcp.tool()
def salesforce_describe_object(object_name: str) -> Dict[str, Any]:
    """Retrieves schema metadata, custom fields, and picklist values for any Salesforce object.
    Example: 'Lead', 'Contact', 'Account', or custom object 'Docupletion_Form__c'
    """
    logger.info("MCP Tool salesforce_describe_object called for: %s", object_name)
    return sf_client.describe_object(object_name)

@mcp.tool()
def salesforce_create_record(object_name: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a new record in Salesforce (e.g. Lead, Contact, or custom object).
    Also immediately indexes it into the local Data Aggregation Table.
    """
    logger.info("MCP Tool salesforce_create_record called on: %s", object_name)
    res = sf_client.create_record(object_name, fields)
    if res.get("success") or res.get("id"):
        rec_id = res.get("id")
        aggregator.upsert_record(
            source_type=f"Salesforce_{object_name}",
            external_id=rec_id,
            name=fields.get("Name") or f"{fields.get('FirstName', '')} {fields.get('LastName', '')}".strip(),
            email=fields.get("Email"),
            company=fields.get("Company"),
            status=fields.get("Status", "New"),
            form_name=object_name,
            payload=fields
        )
    return res

@mcp.tool()
def salesforce_update_record(object_name: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    """Updates an existing record in Salesforce by its ID and refreshes the local aggregation table."""
    logger.info("MCP Tool salesforce_update_record called on: %s (ID: %s)", object_name, record_id)
    res = sf_client.update_record(object_name, record_id, fields)
    if res.get("success"):
        aggregator.upsert_record(
            source_type=f"Salesforce_{object_name}",
            external_id=record_id,
            name=fields.get("Name"),
            email=fields.get("Email"),
            company=fields.get("Company"),
            status=fields.get("Status"),
            payload=fields
        )
    return res

@mcp.tool()
def salesforce_search_sosl(search_term: str) -> Dict[str, Any]:
    """Executes a global SOSL text search across all Salesforce objects.
    Example: 'John Doe' or 'Acme Corp'
    """
    logger.info("MCP Tool salesforce_search_sosl: %s", search_term)
    return sf_client.search_sosl(search_term)

@mcp.tool()
def sync_salesforce_to_aggregation_table(object_type: str = "Lead", limit: int = 100) -> Dict[str, Any]:
    """Pulls recent records from Salesforce and syncs them into the local Data Aggregation Table.
    This creates an offline-accessible, ultra-fast cache that eliminates API rate-limit bottlenecks.
    """
    logger.info("Syncing %s records (Limit: %d) into Aggregation Table", object_type, limit)
    soql = f"SELECT Id, Name, Email, Company, Status, CreatedDate FROM {object_type} ORDER BY CreatedDate DESC LIMIT {limit}"
    query_res = sf_client.query(soql)
    records = query_res.get("records", [])
    count = aggregator.bulk_ingest_salesforce_records(object_type, records)
    return {
        "synced_count": count,
        "object_type": object_type,
        "status": "COMPLETED",
        "mock_mode": sf_client._mock_mode
    }

@mcp.tool()
def query_aggregation_table(source_type: Optional[str] = None, status: Optional[str] = None,
                            search: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Queries the local Consolidated Data Aggregation Table.
    Lightning-fast, offline-capable, and incurs ZERO Salesforce API calls!
    """
    return aggregator.query_records(source_type=source_type, status=status, search_term=search, limit=limit)

@mcp.tool()
def get_aggregation_kpis() -> Dict[str, Any]:
    """Retrieves high-level KPI metrics, lead counts by status, and sync telemetry from the Aggregator."""
    return aggregator.get_aggregation_summary()

if __name__ == "__main__":
    logger.info("Starting %s v%s (MCP Transport: stdio)", config.SERVER_NAME, config.SERVER_VERSION)
    mcp.run(transport="stdio")
