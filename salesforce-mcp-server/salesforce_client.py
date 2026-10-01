"""
Salesforce API Client Wrapper using simple-salesforce.
Supports standard CRUD, SOQL, SOSL, Schema Metadata inspection,
and a Mock Fallback mode for offline development and testing.
"""
import logging
from typing import Any, Dict, List, Optional
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed, SalesforceError
import config

logger = logging.getLogger(__name__)

class SalesforceClient:
    def __init__(self, username: str = None, password: str = None, 
                 security_token: str = None, domain: str = None):
        self.username = username or config.SF_USERNAME
        self.password = password or config.SF_PASSWORD
        self.security_token = security_token or config.SF_SECURITY_TOKEN
        self.domain = domain or config.SF_DOMAIN
        self.client: Optional[Salesforce] = None
        self._mock_mode = False

    def connect(self) -> bool:
        """Establishes connection to Salesforce. Falls back to mock mode if credentials are missing or invalid."""
        if not self.password:
            logger.warning("No Salesforce password provided. Operating in Mock Mode for development.")
            self._mock_mode = True
            return False

        try:
            domain_name = None
            if self.domain:
                clean_domain = self.domain.replace("https://", "").replace("http://", "").strip("/")
                if clean_domain in ("test", "login"):
                    domain_name = clean_domain
                elif clean_domain.endswith(".salesforce.com"):
                    domain_name = clean_domain.replace(".salesforce.com", "")
                else:
                    domain_name = clean_domain

            self.client = Salesforce(
                username=self.username,
                password=self.password,
                security_token=self.security_token,
                domain=domain_name or "login"
            )
            self._mock_mode = False
            logger.info("Connected successfully to Salesforce instance: %s", self.domain)
            return True
        except SalesforceAuthenticationFailed as e:
            logger.error("Salesforce Authentication Failed: %s. Enabling Mock Mode.", e)
            self._mock_mode = True
            return False
        except Exception as e:
            logger.error("Unexpected error connecting to Salesforce: %s. Enabling Mock Mode.", e)
            self._mock_mode = True
            return False

    @property
    def is_connected(self) -> bool:
        return self.client is not None and not self._mock_mode

    def query(self, soql: str) -> Dict[str, Any]:
        """Executes a SOQL query."""
        if not self.is_connected:
            return self._mock_query(soql)
        try:
            return self.client.query(soql)
        except SalesforceError as e:
            return {"error": str(e), "success": False}

    def query_all(self, soql: str) -> Dict[str, Any]:
        """Executes a SOQL query including deleted/archived records."""
        if not self.is_connected:
            return self._mock_query(soql)
        try:
            return self.client.query_all(soql)
        except SalesforceError as e:
            return {"error": str(e), "success": False}

    def get_record(self, object_name: str, record_id: str, fields: List[str] = None) -> Dict[str, Any]:
        """Retrieves a specific record by ID."""
        if not self.is_connected:
            return {"Id": record_id, "Name": f"Mock {object_name} {record_id}", "Status": "Active", "mock": True}
        try:
            obj = getattr(self.client, object_name)
            if fields:
                soql = f"SELECT {', '.join(fields)} FROM {object_name} WHERE Id = '{record_id}'"
                res = self.query(soql)
                records = res.get("records", [])
                return records[0] if records else {"error": "Record not found"}
            return obj.get(record_id)
        except SalesforceError as e:
            return {"error": str(e), "success": False}

    def create_record(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a record in the specified standard or custom object."""
        if not self.is_connected:
            mock_id = f"mock_001_{object_name[:3]}_xyz"
            logger.info("Mock create in %s: %s (Assigned ID: %s)", object_name, data, mock_id)
            return {"id": mock_id, "success": True, "errors": [], "mock": True}
        try:
            obj = getattr(self.client, object_name)
            return obj.create(data)
        except SalesforceError as e:
            return {"error": str(e), "success": False}

    def update_record(self, object_name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a record in Salesforce."""
        if not self.is_connected:
            logger.info("Mock update in %s (%s): %s", object_name, record_id, data)
            return {"success": True, "id": record_id, "mock": True}
        try:
            obj = getattr(self.client, object_name)
            status_code = obj.update(record_id, data)
            return {"success": status_code in (200, 204), "statusCode": status_code, "id": record_id}
        except SalesforceError as e:
            return {"error": str(e), "success": False}

    def delete_record(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """Deletes a record."""
        if not self.is_connected:
            return {"success": True, "id": record_id, "deleted": True, "mock": True}
        try:
            obj = getattr(self.client, object_name)
            status_code = obj.delete(record_id)
            return {"success": status_code in (200, 204), "id": record_id}
        except SalesforceError as e:
            return {"error": str(e), "success": False}

    def describe_object(self, object_name: str) -> Dict[str, Any]:
        """Returns the schema description and field list of an object."""
        if not self.is_connected:
            return {
                "name": object_name,
                "label": object_name,
                "fields": [
                    {"name": "Id", "type": "id", "label": "Record ID"},
                    {"name": "Name", "type": "string", "label": "Full Name"},
                    {"name": "CreatedDate", "type": "datetime", "label": "Created Date"},
                    {"name": "Status", "type": "picklist", "label": "Status"},
                    {"name": "Docupletion_Form_ID__c", "type": "string", "label": "Docupletion Form ID"}
                ],
                "mock": True
            }
        try:
            obj = getattr(self.client, object_name)
            return obj.describe()
        except SalesforceError as e:
            return {"error": str(e), "success": False}

    def search_sosl(self, search_text: str) -> Dict[str, Any]:
        """Executes a SOSL full-text search across records."""
        if not self.is_connected:
            return {"searchRecords": [
                {"Id": "001MockLead1", "attributes": {"type": "Lead"}, "Name": f"Match for {search_text}"}
            ], "mock": True}
        try:
            return self.client.search(f"FIND {{{search_text}}}")
        except SalesforceError as e:
            return {"error": str(e), "success": False}

    def _mock_query(self, soql: str) -> Dict[str, Any]:
        """Provides simulated results when working offline or waiting for admin credentials."""
        logger.info("Mock SOQL query executed: %s", soql)
        soql_lower = soql.lower()
        if "lead" in soql_lower:
            records = [
                {"Id": "00Q5g000001mockA", "Name": "David Miller", "Company": "Acme Legal", "Status": "Open - Not Contacted", "Email": "david@acmelegal.com"},
                {"Id": "00Q5g000002mockB", "Name": "Sarah Jenkins", "Company": "Apex Trust", "Status": "Working - Contacted", "Email": "sjenkins@apextrust.org"}
            ]
        elif "contact" in soql_lower:
            records = [
                {"Id": "0035g000001mockC", "Name": "Robert Vance", "Email": "robert@vance.com", "Title": "Managing Partner"}
            ]
        else:
            records = [
                {"Id": "001MockGeneric1", "Name": "Docupletion Sample Submission", "CreatedDate": "2026-09-10T12:00:00Z", "Status": "Processed"}
            ]
        return {"totalSize": len(records), "done": True, "records": records, "mock": True}
