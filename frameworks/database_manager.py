"""
Enhanced Database Manager with proper error handling, transactions, and validation.
Provides robust database operations for Brand Builder workflow.
"""
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from notion_client import Client, APIResponseError
try:
    from notion_client import RequestTimeoutError
except ImportError:
    # For older versions of notion-client that don't have RequestTimeoutError
    RequestTimeoutError = TimeoutError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

class DatabaseValidationError(DatabaseError):
    """Exception for schema validation errors"""
    pass

class DatabaseConnectionError(DatabaseError):
    """Exception for connection issues"""
    pass

class EnhancedDatabaseManager:
    """
    Enhanced database manager with error handling, validation, and transactions.
    """
    
    def __init__(self, api_key: str, retry_attempts: int = 3, timeout: int = 30):
        """
        Initialize the enhanced database manager.
        
        Args:
            api_key: Notion API key
            retry_attempts: Number of retry attempts for failed operations
            timeout: Timeout in seconds for API calls
        """
        self.api_key = api_key
        self.retry_attempts = retry_attempts
        self.timeout = timeout
        self.notion = None
        self._initialize_client()
        
        # Database schemas for validation
        self.schemas = {
            'voice_guidelines': {
                'required_fields': ['Name', 'Client', 'Status'],
                'optional_fields': ['Word_Choice_Analysis', 'Tone_Analysis', 'Personality_Analysis', 
                                  'Consistency_Assessment', 'Audience_Fit_Assessment', 'Last_Updated'],
                'field_types': {
                    'Name': 'title',
                    'Client': 'relation', 
                    'Status': 'select',
                    'Word_Choice_Analysis': 'rich_text',
                    'Tone_Analysis': 'rich_text',
                    'Personality_Analysis': 'rich_text',
                    'Consistency_Assessment': 'rich_text',
                    'Audience_Fit_Assessment': 'rich_text',
                    'Last_Updated': 'date'
                }
            },
            'content_samples': {
                'required_fields': ['Name', 'Client', 'Channel_Type', 'Sample_Content'],
                'optional_fields': ['Tone_Assessment', 'Original_Sample', 'Rewritten_Version', 'Notes'],
                'field_types': {
                    'Name': 'title',
                    'Client': 'relation',
                    'Channel_Type': 'select',
                    'Sample_Content': 'rich_text',
                    'Tone_Assessment': 'select',
                    'Original_Sample': 'checkbox',
                    'Rewritten_Version': 'checkbox',
                    'Notes': 'rich_text'
                }
            }
        }
    
    def _initialize_client(self):
        """Initialize Notion client with error handling"""
        try:
            self.notion = Client(auth=self.api_key, timeout_ms=self.timeout * 1000)
            logger.info("✅ Notion client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Notion client: {str(e)}")
            raise DatabaseConnectionError(f"Failed to initialize Notion client: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the database connection.
        
        Returns:
            Dict with health status and metrics
        """
        health_status = {
            'status': 'unknown',
            'timestamp': datetime.now().isoformat(),
            'response_time_ms': None,
            'error': None
        }
        
        try:
            start_time = time.time()
            
            # Test connection with a simple API call
            self.notion.users.me()
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            health_status.update({
                'status': 'healthy',
                'response_time_ms': round(response_time, 2)
            })
            
            logger.info(f"✅ Health check passed - Response time: {response_time:.2f}ms")
            
        except Exception as e:
            health_status.update({
                'status': 'unhealthy',
                'error': str(e)
            })
            logger.error(f"❌ Health check failed: {str(e)}")
            
        return health_status
    
    def validate_schema(self, data: Dict[str, Any], schema_name: str) -> List[str]:
        """
        Validate data against database schema.
        
        Args:
            data: Data to validate
            schema_name: Name of schema to validate against
            
        Returns:
            List of validation errors (empty if valid)
        """
        if schema_name not in self.schemas:
            return [f"Unknown schema: {schema_name}"]
        
        schema = self.schemas[schema_name]
        errors = []
        
        # Check required fields
        for field in schema['required_fields']:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check field types and format
        for field, value in data.items():
            if field in schema['field_types']:
                expected_type = schema['field_types'][field]
                if not self._validate_field_type(value, expected_type):
                    errors.append(f"Invalid type for field {field}: expected {expected_type}")
        
        return errors
    
    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validate field type according to Notion API requirements"""
        try:
            if expected_type == 'title':
                return isinstance(value, dict) and 'title' in value
            elif expected_type == 'rich_text':
                return isinstance(value, dict) and 'rich_text' in value
            elif expected_type == 'select':
                return isinstance(value, dict) and 'select' in value
            elif expected_type == 'relation':
                return isinstance(value, dict) and 'relation' in value
            elif expected_type == 'checkbox':
                return isinstance(value, dict) and 'checkbox' in value
            elif expected_type == 'date':
                return isinstance(value, dict) and 'date' in value
            else:
                return True  # Unknown type, assume valid
        except Exception:
            return False
    
    def _retry_operation(self, operation, *args, **kwargs):
        """
        Retry database operations with exponential backoff.
        
        Args:
            operation: Function to retry
            *args, **kwargs: Arguments for the operation
            
        Returns:
            Operation result
            
        Raises:
            DatabaseError: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(self.retry_attempts):
            try:
                return operation(*args, **kwargs)
            
            except (APIResponseError, RequestTimeoutError) as e:
                last_exception = e
                wait_time = (2 ** attempt) * 0.5  # Exponential backoff
                
                logger.warning(f"Database operation failed (attempt {attempt + 1}/{self.retry_attempts}): {str(e)}")
                logger.info(f"Retrying in {wait_time} seconds...")
                
                if attempt < self.retry_attempts - 1:
                    time.sleep(wait_time)
                
            except Exception as e:
                # Non-retryable error
                logger.error(f"Non-retryable database error: {str(e)}")
                raise DatabaseError(f"Database operation failed: {str(e)}")
        
        # All retry attempts failed
        logger.error(f"All retry attempts failed. Last error: {str(last_exception)}")
        raise DatabaseError(f"Database operation failed after {self.retry_attempts} attempts: {str(last_exception)}")
    
    def save_with_validation(self, database_id: str, properties: Dict[str, Any], 
                           schema_name: str, validate: bool = True) -> Dict[str, Any]:
        """
        Save data to database with validation and error handling.
        
        Args:
            database_id: Target database ID
            properties: Page properties to save
            schema_name: Schema name for validation
            validate: Whether to validate before saving
            
        Returns:
            Created page response
            
        Raises:
            DatabaseValidationError: If validation fails
            DatabaseError: If save operation fails
        """
        if validate:
            validation_errors = self.validate_schema(properties, schema_name)
            if validation_errors:
                error_msg = f"Schema validation failed: {'; '.join(validation_errors)}"
                logger.error(f"❌ {error_msg}")
                raise DatabaseValidationError(error_msg)
        
        try:
            logger.info(f"💾 Saving to {schema_name} database...")
            
            response = self._retry_operation(
                self.notion.pages.create,
                parent={"database_id": database_id},
                properties=properties
            )
            
            logger.info(f"✅ Successfully saved to database: {response['id']}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to save to database: {str(e)}")
            raise DatabaseError(f"Failed to save to database: {str(e)}")
    
    def query_with_retry(self, database_id: str, **query_params) -> Dict[str, Any]:
        """
        Query database with retry logic.
        
        Args:
            database_id: Database to query
            **query_params: Query parameters
            
        Returns:
            Query response
        """
        try:
            logger.info(f"🔍 Querying database: {database_id}")
            
            response = self._retry_operation(
                self.notion.databases.query,
                database_id=database_id,
                **query_params
            )
            
            logger.info(f"✅ Query successful - Found {len(response['results'])} results")
            return response
            
        except Exception as e:
            logger.error(f"❌ Database query failed: {str(e)}")
            raise DatabaseError(f"Database query failed: {str(e)}")
    
    def update_with_validation(self, page_id: str, properties: Dict[str, Any], 
                             schema_name: str, validate: bool = True) -> Dict[str, Any]:
        """
        Update page with validation and error handling.
        
        Args:
            page_id: Page to update
            properties: Properties to update
            schema_name: Schema name for validation
            validate: Whether to validate before updating
            
        Returns:
            Updated page response
        """
        if validate:
            validation_errors = self.validate_schema(properties, schema_name)
            if validation_errors:
                error_msg = f"Schema validation failed: {'; '.join(validation_errors)}"
                logger.error(f"❌ {error_msg}")
                raise DatabaseValidationError(error_msg)
        
        try:
            logger.info(f"🔄 Updating page: {page_id}")
            
            response = self._retry_operation(
                self.notion.pages.update,
                page_id=page_id,
                properties=properties
            )
            
            logger.info(f"✅ Successfully updated page: {page_id}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to update page: {str(e)}")
            raise DatabaseError(f"Failed to update page: {str(e)}")
    
    def bulk_save(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform bulk save operations with transaction-like behavior.
        
        Args:
            operations: List of save operations
            
        Returns:
            List of results
        """
        results = []
        successful_operations = []
        
        try:
            for i, operation in enumerate(operations):
                try:
                    result = self.save_with_validation(**operation)
                    results.append(result)
                    successful_operations.append(i)
                    
                except Exception as e:
                    logger.error(f"❌ Bulk operation {i} failed: {str(e)}")
                    
                    # Attempt to rollback successful operations (if supported)
                    self._attempt_rollback(successful_operations, results)
                    
                    raise DatabaseError(f"Bulk save failed at operation {i}: {str(e)}")
            
            logger.info(f"✅ Bulk save completed successfully - {len(results)} operations")
            return results
            
        except Exception as e:
            logger.error(f"❌ Bulk save failed: {str(e)}")
            raise
    
    def _attempt_rollback(self, successful_operations: List[int], results: List[Dict[str, Any]]):
        """
        Attempt to rollback successful operations.
        Note: Notion doesn't support true transactions, so this is best-effort cleanup.
        """
        logger.warning("⚠️ Attempting rollback of successful operations...")
        
        for i, result in enumerate(results):
            try:
                # Mark as failed/rollback rather than delete (safer)
                self.notion.pages.update(
                    page_id=result['id'],
                    properties={
                        "Status": {"select": {"name": "Failed - Rollback"}}
                    }
                )
                logger.info(f"🔄 Marked operation {i} for rollback")
                
            except Exception as e:
                logger.error(f"❌ Rollback failed for operation {i}: {str(e)}")
    
    def format_rich_text(self, content: str) -> Dict[str, Any]:
        """Helper to format rich text for Notion API"""
        return {"rich_text": [{"text": {"content": content[:2000]}}]}  # Notion limit
    
    def format_title(self, content: str) -> Dict[str, Any]:
        """Helper to format title for Notion API"""
        return {"title": [{"text": {"content": content[:100]}}]}  # Reasonable limit
    
    def format_select(self, option: str) -> Dict[str, Any]:
        """Helper to format select for Notion API"""
        return {"select": {"name": option}}
    
    def format_relation(self, page_ids: List[str]) -> Dict[str, Any]:
        """Helper to format relation for Notion API"""
        return {"relation": [{"id": page_id} for page_id in page_ids]}
    
    def format_checkbox(self, checked: bool) -> Dict[str, Any]:
        """Helper to format checkbox for Notion API"""
        return {"checkbox": checked}
    
    def format_date(self, date_str: str = None) -> Dict[str, Any]:
        """Helper to format date for Notion API"""
        if date_str is None:
            date_str = datetime.now().isoformat()
        return {"date": {"start": date_str}}


class NotionDatabaseManager:
    """
    Client-focused database manager for Brand Builder workflow.
    Consolidates client management operations from research_tools_framework.
    """
    
    def __init__(self, notion_api_key=None):
        """Initialize the Notion Database Manager"""
        # Use the new secure database configuration system
        try:
            from database_config import get_notion_client, get_database_ids
            
            if notion_api_key is None:
                self.notion = get_notion_client()
            else:
                self.notion = Client(auth=notion_api_key)
            
            # Get database IDs using the secure configuration system
            db_ids = get_database_ids()
            self.client_database_id = db_ids['client_database_id']
            self.content_samples_database_id = db_ids['content_samples_database_id']
            self.voice_guidelines_database_id = db_ids['voice_guidelines_database_id']
        except ImportError:
            # Fallback if database_config not available
            if notion_api_key is None:
                raise ValueError("Notion API key required when database_config not available")
            self.notion = Client(auth=notion_api_key)
            self.client_database_id = None
            self.content_samples_database_id = None
            self.voice_guidelines_database_id = None
    
    def get_client_list(self):
        """Get a list of all clients"""
        if not self.client_database_id:
            return {}
            
        response = self.notion.databases.query(
            database_id=self.client_database_id,
            sorts=[{"property": "Name", "direction": "ascending"}]
        )
        
        clients = {}
        for page in response["results"]:
            if "Name" in page["properties"] and page["properties"]["Name"]["title"]:
                client_name = page["properties"]["Name"]["title"][0]["text"]["content"]
                clients[client_name] = page["id"]
        
        return clients
    
    def create_new_client(self, client_name, industry):
        """Create a new client in the Notion database"""
        if not self.client_database_id:
            return None
            
        try:
            response = self.notion.pages.create(
                parent={"database_id": self.client_database_id},
                properties={
                    "Name": {"title": [{"text": {"content": client_name}}]},
                    "Industry": {"select": {"name": industry}},
                    "Research_Status": {"select": {"name": "In Progress"}},
                    "Last_Updated": {"date": {"start": self._get_current_date()}}
                }
            )
            return response["id"]
        except Exception as e:
            logger.error(f"Error creating new client: {str(e)}")
            return None
    
    def get_client_page_id(self, client_name):
        """Get the page ID for a client by name"""
        if not self.client_database_id:
            return None
            
        response = self.notion.databases.query(
            database_id=self.client_database_id,
            filter={"property": "Name", "title": {"equals": client_name}}
        )
        
        if response["results"]:
            return response["results"][0]["id"]
        return None
    
    def get_client_profile(self, client_page_id):
        """Get a client's profile data"""
        if not client_page_id:
            return {}
            
        try:
            page = self.notion.pages.retrieve(page_id=client_page_id)
            profile = {"id": client_page_id}
            props = page.get("properties", {})
            
            # Basic properties
            if "Name" in props and props["Name"].get("title") and props["Name"]["title"]:
                profile["Name"] = props["Name"]["title"][0]["text"]["content"]
            
            if "Industry" in props and props["Industry"].get("select"):
                profile["Industry"] = props["Industry"]["select"]["name"]
            
            # Rich text properties
            rich_text_props = [
                "Product_Service_Description", "Current_Target_Audience", "Ideal_Target_Audience",
                "Brand_Mission", "Words_Tones_To_Avoid", "Website", "Contact_Email", "Phone_Number",
                "Address", "LinkedIn_URL", "Twitter_URL", "Facebook_URL", "Instagram_URL", "Other_Social_Media"
            ]
            
            for prop in rich_text_props:
                if prop in props and props[prop].get("rich_text") and props[prop]["rich_text"]:
                    profile[prop] = props[prop]["rich_text"][0]["text"]["content"]
            
            # Multi-select properties
            multi_select_props = ["Brand_Values", "Desired_Emotional_Impact", "Brand_Personality"]
            for prop in multi_select_props:
                if prop in props and props[prop].get("multi_select"):
                    profile[prop] = [item["name"] for item in props[prop]["multi_select"]]
            
            # Status
            if "Research_Status" in props and props["Research_Status"].get("select"):
                profile["Research_Status"] = props["Research_Status"]["select"]["name"]
            else:
                profile["Research_Status"] = "Not Started"
            
            return profile
        except Exception as e:
            logger.error(f"Error retrieving client profile: {str(e)}")
            return {}
    
    def update_client_profile(self, client_page_id, profile_data):
        """Update a client's profile with research data"""
        properties = {
            "Research_Status": {"select": {"name": "In Progress"}},
            "Last_Updated": {"date": {"start": self._get_current_date()}}
        }
        
        # Rich text fields
        rich_text_fields = [
            "Product_Service_Description", "Current_Target_Audience", "Ideal_Target_Audience", 
            "Brand_Mission", "Words_Tones_To_Avoid", "Website", "Contact_Email", "Phone_Number",
            "Address", "LinkedIn_URL", "Twitter_URL", "Facebook_URL", "Instagram_URL", "Other_Social_Media"
        ]
        
        for field in rich_text_fields:
            if field in profile_data and profile_data[field]:
                properties[field] = {"rich_text": [{"text": {"content": profile_data[field]}}]}
        
        # Multi-select fields
        multi_select_fields = ["Brand_Values", "Desired_Emotional_Impact", "Brand_Personality"]
        for field in multi_select_fields:
            if field in profile_data and profile_data[field]:
                if isinstance(profile_data[field], str):
                    values = [v.strip() for v in profile_data[field].split(",")]
                else:
                    values = profile_data[field]
                properties[field] = {"multi_select": [{"name": value} for value in values]}
        
        try:
            self.notion.pages.update(page_id=client_page_id, properties=properties)
            return True
        except Exception as e:
            logger.error(f"Error updating client profile: {str(e)}")
            return False
    
    def get_tool_completion_status(self, client_page_id):
        """Get completion status of all tools for a client"""
        if not client_page_id:
            return {
                "brand_builder": False, "content_collector": False, "voice_auditor": False,
                "audience_definer": False, "voice_traits_builder": False, "gap_analyzer": False,
                "content_rewriter": False, "guidelines_finalizer": False
            }
            
        try:
            page = self.notion.pages.retrieve(page_id=client_page_id)
            props = page.get("properties", {})
            status = {
                "brand_builder": False, "content_collector": False, "voice_auditor": False,
                "audience_definer": False, "voice_traits_builder": False, "gap_analyzer": False,
                "content_rewriter": False, "guidelines_finalizer": False
            }
            
            prop_map = {
                "Brand_Builder_Complete": "brand_builder",
                "Content_Collector_Complete": "content_collector",
                "Voice_Auditor_Complete": "voice_auditor",
                "Audience_Definer_Complete": "audience_definer",
                "Voice_Traits_Builder_Complete": "voice_traits_builder",
                "Gap_Analyzer_Complete": "gap_analyzer",
                "Content_Rewriter_Complete": "content_rewriter",
                "Guidelines_Finalizer_Complete": "guidelines_finalizer"
            }
            
            for prop_name, status_key in prop_map.items():
                if prop_name in props and props[prop_name].get("checkbox") is not None:
                    status[status_key] = props[prop_name]["checkbox"]
            
            return status
        except Exception as e:
            logger.error(f"Error retrieving tool completion status: {str(e)}")
            return {
                "brand_builder": False, "content_collector": False, "voice_auditor": False,
                "audience_definer": False, "voice_traits_builder": False, "gap_analyzer": False,
                "content_rewriter": False, "guidelines_finalizer": False
            }
    
    def mark_tool_complete(self, client_page_id, tool_name):
        """Mark a specific tool as complete for a client"""
        property_map = {
            "brand_builder": "Brand_Builder_Complete",
            "content_collector": "Content_Collector_Complete",
            "voice_auditor": "Voice_Auditor_Complete",
            "audience_definer": "Audience_Definer_Complete",
            "voice_traits_builder": "Voice_Traits_Builder_Complete",
            "gap_analyzer": "Gap_Analyzer_Complete",
            "content_rewriter": "Content_Rewriter_Complete",
            "guidelines_finalizer": "Guidelines_Finalizer_Complete"
        }
        
        if tool_name in property_map:
            try:
                properties_to_update = {
                    "Last_Tool_Completed": {"rich_text": [{"text": {"content": tool_name}}]},
                    "Last_Updated": {"date": {"start": self._get_current_date()}}
                }
                
                self.notion.pages.update(page_id=client_page_id, properties=properties_to_update)
                return True
            except Exception:
                return False
        return False
    
    def get_deep_research_data(self, client_page_id):
        """Get deep research workflow data for a client"""
        try:
            client_profile = self.get_client_profile(client_page_id)
            workflow_data_str = client_profile.get("Deep_Research_Workflow", "{}")
            
            if isinstance(workflow_data_str, str):
                return json.loads(workflow_data_str) if workflow_data_str.strip() else {}
            else:
                return workflow_data_str or {}
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Could not parse workflow data: {e}")
            return {}
    
    def save_deep_research_step(self, client_page_id, step_name, step_data):
        """Save a step of the deep research workflow"""
        try:
            current_workflow = self.get_deep_research_data(client_page_id)
            current_workflow[step_name] = {
                "data": step_data,
                "completed_at": self._get_current_date(),
                "status": "completed"
            }
            
            workflow_json = json.dumps(current_workflow)
            success = self.update_client_profile(client_page_id, {
                "Deep_Research_Workflow": workflow_json,
                "Last_Updated": self._get_current_date()
            })
            
            return success
        except Exception as e:
            logger.error(f"Error saving workflow step: {str(e)}")
            return False
    
    def get_workflow_step_status(self, client_page_id, step_name):
        """Check if a workflow step is completed"""
        workflow_data = self.get_deep_research_data(client_page_id)
        return step_name in workflow_data and workflow_data[step_name].get("status") == "completed"
    
    def _get_current_date(self):
        """Get current date in ISO format"""
        return datetime.now().strftime("%Y-%m-%d")


# Utility functions consolidated from research_tools_framework
def format_list_for_display(items_list):
    """Format a list for display (converts list to comma-separated string)"""
    if not items_list:
        return ""
    
    if isinstance(items_list, list):
        return ", ".join(items_list)
    
    return str(items_list)


def parse_markdown_table(markdown_table):
    """Parse a markdown table into a list of dictionaries"""
    import re
    result = []
    
    # Split into lines
    lines = markdown_table.strip().split('\n')
    
    # Find header row
    header_row = None
    for i, line in enumerate(lines):
        if line.startswith('|') and i < len(lines) - 1 and re.match(r'^\|\s*[-:]+\s*\|', lines[i+1]):
            header_row = line
            break
    
    if not header_row:
        return result
    
    # Extract headers
    headers = [h.strip() for h in header_row.split('|')[1:-1]]
    
    # Process data rows
    for line in lines:
        # Skip header and separator rows
        if line == header_row or re.match(r'^\|\s*[-:]+\s*\|', line):
            continue
        
        # Extract cells
        if line.startswith('|') and line.endswith('|'):
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            
            # Skip if the number of cells doesn't match headers
            if len(cells) != len(headers):
                continue
            
            # Create a dictionary for this row
            row_dict = {headers[i]: cells[i] for i in range(len(headers))}
            result.append(row_dict)
    
    return result


def client_selector_sidebar(db_manager=None, allow_new_client=False):
    """Shared client selector sidebar component with option to create new client"""
    import streamlit as st
    
    # Initialize database manager if not provided
    if db_manager is None:
        db_manager = NotionDatabaseManager()
    
    # Get client list
    client_list = db_manager.get_client_list()
    
    # Create options for the dropdown
    client_options = list(client_list.keys())
    
    # Add "Create New Client" option if allowed
    if allow_new_client:
        client_options = ["➕ Create New Client"] + client_options
    
    # Display a message if no clients and not allowing new clients
    if not client_options and not allow_new_client:
        st.sidebar.warning("No clients found in Notion database. Please add clients directly in Notion.")
        return None, None, {}
    
    # Select client from dropdown
    selected_client = st.sidebar.selectbox(
        "Select Client",
        options=client_options,
        key="research_client_selector"
    )
    
    # Handle new client creation
    if selected_client == "➕ Create New Client":
        with st.sidebar.form("new_client_form"):
            st.subheader("Create New Client")
            new_client_name = st.text_input("Client Name", key="new_client_name")
            website_url = st.text_input("Website URL (optional)", key="new_client_website", 
                                      help="Provide URL to auto-extract company information")
            
            create_button = st.form_submit_button("Create Client")
            
            if create_button and new_client_name:
                # Create the new client
                new_client_id = db_manager.create_new_client(new_client_name, "Other")
                
                if new_client_id:
                    # Store in session state for continued use
                    st.session_state.client_page_id = new_client_id
                    st.session_state.client_name = new_client_name
                    
                    # Show success message and refresh
                    st.sidebar.success(f"✅ Created new client: {new_client_name}")
                    
                    # Return the new client info
                    return new_client_id, new_client_name, {
                        "brand_builder": False,
                        "content_collector": False,
                        "voice_auditor": False,
                        "audience_definer": False,
                        "voice_traits_builder": False,
                        "gap_analyzer": False,
                        "content_rewriter": False,
                        "guidelines_finalizer": False
                    }
                else:
                    st.sidebar.error("Failed to create new client")
        
        # If we reach here, no client was created yet
        return None, None, {}
    
    # Handle existing client selection
    elif selected_client in client_list:
        client_page_id = client_list[selected_client]
        
        # Store in session state
        st.session_state.client_page_id = client_page_id
        st.session_state.client_name = selected_client
        
        # Show tool completion status
        try:
            status = db_manager.get_tool_completion_status(client_page_id)
            
            st.sidebar.markdown("### Research Progress")
            status_emojis = {True: "✅", False: "⬜"}
            
            tool_labels = [
                ("brand_builder", "1. Brand Builder"),
                ("content_collector", "2. Content Collector"),
                ("voice_auditor", "3. Voice Auditor"),
                ("audience_definer", "4. Audience Definer"),
                ("voice_traits_builder", "5. Voice Traits Builder"),
                ("gap_analyzer", "6. Gap Analyzer"),
                ("content_rewriter", "7. Content Rewriter"),
                ("guidelines_finalizer", "8. Guidelines Finalizer")
            ]
            
            for key, label in tool_labels:
                st.sidebar.markdown(f"{status_emojis[status.get(key, False)]} {label}")
        
        except Exception as e:
            st.sidebar.warning("Could not retrieve tool status.")
            status = {}
        
        return client_page_id, selected_client, status
    else:
        # No valid selection
        st.sidebar.warning("Please select a client or create a new one.")
        return None, None, {}


def run_brand_builder():
    """Streamlit UI for Brand Builder - Step 1 Only"""
    import streamlit as st
    
    st.title("Brand Builder")
    st.subheader("Start here")
    
    st.write("Enter the name and URL of client and the workflow will take it from here!")
    
    # Import step 1 components
    from tools.brand_builder.step_01_website_extractor import AutomatedWebsiteExtractor, WorkflowContext
    
    # Input form
    with st.form("website_extractor"):
        client_name = st.text_input("Client Name", placeholder="Enter client name")
        website_url = st.text_input("Website URL", placeholder="https://example.com")
        
        submitted = st.form_submit_button("🔍 Extract Website Data")
        
        if submitted:
            if not client_name or not website_url:
                st.error("Please provide both client name and website URL")
            else:
                # Ensure URL has protocol
                if not website_url.startswith('http'):
                    website_url = f"https://{website_url}"
                
                # Create context and run extraction
                context = WorkflowContext()
                context.set_input("client_name", client_name)
                context.set_input("website_url", website_url)
                
                # Run the extraction
                with st.spinner("🔍 Extracting website data..."):
                    extractor = AutomatedWebsiteExtractor()
                    result = extractor.execute(context)
                
                # Show results
                if result.success:
                    st.success("✅ Website extraction completed!")
                    
                    # Display results
                    st.subheader("📊 Extraction Results")
                    
                    if result.data.get("analysis"):
                        st.write("### Business Analysis")
                        st.json(result.data["analysis"])
                    
                    if result.data.get("content_file"):
                        st.write(f"📁 **Content File:** `{result.data['content_file']}`")
                    
                    if result.data.get("sitemap_file"):
                        st.write(f"🗺️ **Sitemap File:** `{result.data['sitemap_file']}`")
                    
                    if result.data.get("client_id"):
                        st.write(f"🗄️ **Notion Client ID:** `{result.data['client_id']}`")
                    
                    st.balloons()
                else:
                    st.error("❌ Extraction failed:")
                    for error in result.errors:
                        st.error(f"  • {error}")