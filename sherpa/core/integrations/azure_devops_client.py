"""
SHERPA V1 - Azure DevOps Integration Client
Handles connection and operations with Azure DevOps services
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
import logging

try:
    from azure.devops.connection import Connection
    from msrest.authentication import BasicAuthentication
    from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
    from azure.devops.v7_1.work_item_tracking.models import Wiql
    AZURE_DEVOPS_AVAILABLE = True
except ImportError:
    AZURE_DEVOPS_AVAILABLE = False
    Connection = None
    BasicAuthentication = None
    WorkItemTrackingClient = None
    Wiql = None

logger = logging.getLogger("sherpa.azure_devops")


class AzureDevOpsClient:
    """Client for Azure DevOps API operations"""

    def __init__(self):
        """Initialize Azure DevOps client"""
        self.organization: Optional[str] = None
        self.project: Optional[str] = None
        self.connection: Optional[Connection] = None
        self.wit_client: Optional[WorkItemTrackingClient] = None
        self.is_connected = False

    async def connect(self, organization: str, project: str, pat: str) -> Dict[str, Any]:
        """
        Connect to Azure DevOps using Personal Access Token

        Args:
            organization: Azure DevOps organization name
            project: Project name
            pat: Personal Access Token

        Returns:
            Dict with connection status and details
        """
        try:
            if not AZURE_DEVOPS_AVAILABLE:
                # Return mock success for testing when package not installed
                logger.warning("Azure DevOps SDK not available, using mock mode")
                self.organization = organization
                self.project = project
                self.is_connected = True
                return {
                    "success": True,
                    "organization": organization,
                    "project": project,
                    "connection_status": "connected (mock mode)",
                    "message": "Connected to Azure DevOps in mock mode"
                }

            # Create organization URL
            organization_url = f"https://dev.azure.com/{organization}"

            # Create authentication credentials
            credentials = BasicAuthentication('', pat)

            # Create connection
            self.connection = Connection(base_url=organization_url, creds=credentials)

            # Get Work Item Tracking client
            self.wit_client = self.connection.clients.get_work_item_tracking_client()

            # Test connection by getting project info
            try:
                # Try to get a work item query to verify connection
                # This will throw an error if credentials are invalid
                core_client = self.connection.clients.get_core_client()
                project_obj = core_client.get_project(project)

                if not project_obj:
                    raise Exception(f"Project '{project}' not found")

            except Exception as e:
                logger.error(f"Failed to verify connection: {str(e)}")
                raise Exception(f"Failed to connect to Azure DevOps: {str(e)}")

            # Store connection details
            self.organization = organization
            self.project = project
            self.is_connected = True

            logger.info(f"Successfully connected to Azure DevOps: {organization}/{project}")

            return {
                "success": True,
                "organization": organization,
                "project": project,
                "connection_status": "connected",
                "message": f"Successfully connected to {organization}/{project}"
            }

        except Exception as e:
            logger.error(f"Azure DevOps connection failed: {str(e)}")
            self.is_connected = False
            raise Exception(f"Failed to connect to Azure DevOps: {str(e)}")

    async def get_work_items(self, query: Optional[str] = None, top: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch work items from Azure DevOps

        Args:
            query: Optional WIQL query string
            top: Maximum number of work items to return

        Returns:
            List of work items
        """
        if not self.is_connected:
            raise Exception("Not connected to Azure DevOps. Call connect() first.")

        try:
            if not AZURE_DEVOPS_AVAILABLE:
                # Return mock data for testing
                logger.info("Returning mock work items")
                return [
                    {
                        "id": 1001,
                        "title": "Implement user authentication",
                        "type": "User Story",
                        "state": "Active",
                        "assigned_to": "John Doe",
                        "description": "Add JWT-based authentication to the API"
                    },
                    {
                        "id": 1002,
                        "title": "Create dashboard UI",
                        "type": "User Story",
                        "state": "New",
                        "assigned_to": "Jane Smith",
                        "description": "Build React dashboard with charts"
                    }
                ]

            # Default query if none provided
            if not query:
                query = f"SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType] FROM WorkItems WHERE [System.TeamProject] = '{self.project}' ORDER BY [System.ChangedDate] DESC"

            # Execute WIQL query
            wiql = Wiql(query=query)
            query_results = self.wit_client.query_by_wiql(wiql, top=top)

            if not query_results.work_items:
                return []

            # Get work item IDs
            work_item_ids = [item.id for item in query_results.work_items]

            # Get full work item details
            work_items = self.wit_client.get_work_items(
                ids=work_item_ids,
                expand="all"
            )

            # Format results
            formatted_items = []
            for item in work_items:
                fields = item.fields
                formatted_items.append({
                    "id": item.id,
                    "title": fields.get("System.Title", ""),
                    "type": fields.get("System.WorkItemType", ""),
                    "state": fields.get("System.State", ""),
                    "assigned_to": fields.get("System.AssignedTo", {}).get("displayName", "") if isinstance(fields.get("System.AssignedTo"), dict) else str(fields.get("System.AssignedTo", "")),
                    "description": fields.get("System.Description", ""),
                    "created_date": fields.get("System.CreatedDate", ""),
                    "changed_date": fields.get("System.ChangedDate", "")
                })

            return formatted_items

        except Exception as e:
            logger.error(f"Failed to fetch work items: {str(e)}")
            raise Exception(f"Failed to fetch work items: {str(e)}")

    async def update_work_item(self, work_item_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a work item in Azure DevOps

        Args:
            work_item_id: Work item ID to update
            updates: Dictionary of field updates

        Returns:
            Updated work item details
        """
        if not self.is_connected:
            raise Exception("Not connected to Azure DevOps. Call connect() first.")

        try:
            if not AZURE_DEVOPS_AVAILABLE:
                # Return mock success for testing
                logger.info(f"Mock update work item {work_item_id}")
                return {
                    "success": True,
                    "work_item_id": work_item_id,
                    "updates": updates,
                    "message": "Work item updated successfully (mock mode)"
                }

            # Create JSON patch document
            from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation

            patch_document = []
            for field, value in updates.items():
                # Convert friendly field names to Azure DevOps field names
                field_name = field if field.startswith("System.") else f"System.{field}"

                patch_document.append(
                    JsonPatchOperation(
                        op="add",
                        path=f"/fields/{field_name}",
                        value=value
                    )
                )

            # Update work item
            updated_item = self.wit_client.update_work_item(
                document=patch_document,
                id=work_item_id,
                project=self.project
            )

            return {
                "success": True,
                "work_item_id": work_item_id,
                "title": updated_item.fields.get("System.Title", ""),
                "state": updated_item.fields.get("System.State", ""),
                "message": "Work item updated successfully"
            }

        except Exception as e:
            logger.error(f"Failed to update work item {work_item_id}: {str(e)}")
            raise Exception(f"Failed to update work item: {str(e)}")

    async def convert_work_item_to_spec(self, work_item_id: int) -> str:
        """
        Convert a work item to app_spec.txt format

        Args:
            work_item_id: Work item ID to convert

        Returns:
            Formatted spec string
        """
        if not self.is_connected:
            raise Exception("Not connected to Azure DevOps. Call connect() first.")

        try:
            if not AZURE_DEVOPS_AVAILABLE:
                # Return mock spec for testing
                logger.info(f"Mock convert work item {work_item_id} to spec")
                return f"""Project Specification: Work Item #{work_item_id}
===================================================================

## Overview

Implement user authentication

## Description

Add JWT-based authentication to the API

## Technical Requirements

- Backend: FastAPI with JWT authentication
- Database: Store user credentials securely
- Security: Hash passwords with bcrypt
- Tokens: Generate and validate JWT tokens

## Acceptance Criteria

- Users can register with email and password
- Users can login and receive JWT token
- Protected endpoints verify JWT token
- Tokens expire after 24 hours
- Passwords are hashed and never stored in plain text

## Success Criteria

- ✅ Registration endpoint works
- ✅ Login endpoint returns valid JWT
- ✅ Protected endpoints reject invalid tokens
- ✅ Password hashing implemented
- ✅ Token expiration works correctly
"""

            # Get work item details
            work_item = self.wit_client.get_work_item(work_item_id, expand="all")
            fields = work_item.fields

            # Extract fields
            title = fields.get("System.Title", "Untitled")
            description = fields.get("System.Description", "")
            work_item_type = fields.get("System.WorkItemType", "")
            acceptance_criteria = fields.get("Microsoft.VSTS.Common.AcceptanceCriteria", "")

            # Build spec file content
            spec_content = f"""Project Specification: {title}
===================================================================

## Overview

{title}

## Description

{description if description else "No description provided"}

## Work Item Details

- Type: {work_item_type}
- ID: #{work_item_id}
- Project: {self.project}

## Acceptance Criteria

{acceptance_criteria if acceptance_criteria else "No acceptance criteria defined"}

## Success Criteria

- ✅ All acceptance criteria met
- ✅ Code is tested and verified
- ✅ Documentation is complete
- ✅ Changes are committed to version control
"""

            logger.info(f"Successfully converted work item {work_item_id} to spec")
            return spec_content

        except Exception as e:
            logger.error(f"Failed to convert work item {work_item_id} to spec: {str(e)}")
            raise Exception(f"Failed to convert work item to spec: {str(e)}")

    def disconnect(self):
        """Disconnect from Azure DevOps"""
        self.connection = None
        self.wit_client = None
        self.is_connected = False
        logger.info("Disconnected from Azure DevOps")


# Singleton instance
_azure_devops_client: Optional[AzureDevOpsClient] = None


def get_azure_devops_client() -> AzureDevOpsClient:
    """Get or create singleton Azure DevOps client instance"""
    global _azure_devops_client
    if _azure_devops_client is None:
        _azure_devops_client = AzureDevOpsClient()
    return _azure_devops_client
