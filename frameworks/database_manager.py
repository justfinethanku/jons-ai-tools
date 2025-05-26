"""
database_manager

Enhanced Database Manager with proper error handling, transactions, and validation.
Provides robust database operations for Brand Builder workflow.
"""
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from notion_client import Client, APIResponseError
try:
    from notion_client import RequestTimeoutError
except ImportError:
    # For older versions of notion-client that don't have RequestTimeoutError
    RequestTimeoutError = TimeoutError
from frameworks.logging_manager import get_logger

# Get structured logger
logger = get_logger("database_manager")

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
    DEPRECATED: Use NotionDatabaseManager instead.
    This class is kept for backward compatibility only.
    All features have been merged into NotionDatabaseManager.
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
            logger.log_operation_success("initialize_notion_client")
        except Exception as e:
            logger.log_operation_failure("initialize_notion_client", str(e))
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
            
            logger.log_api_call("notion", "users.me", status_code=200, duration_ms=round(response_time, 2))
            
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
        
        try:
            for i, operation in enumerate(operations):
                try:
                    result = self.save_with_validation(**operation)
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"❌ Bulk operation {i} failed: {str(e)}")
                    
                    # Attempt to rollback successful operations (if supported)
                    self._attempt_rollback(results)
                    
                    raise DatabaseError(f"Bulk save failed at operation {i}: {str(e)}")
            
            logger.info(f"✅ Bulk save completed successfully - {len(results)} operations")
            return results
            
        except Exception as e:
            logger.error(f"❌ Bulk save failed: {str(e)}")
            raise
    
    def _attempt_rollback(self, results: List[Dict[str, Any]]):
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
    
    def __init__(self, notion_api_key=None, retry_attempts=3):
        """Initialize the Notion Database Manager"""
        self.retry_attempts = retry_attempts
        
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
                import streamlit as st
                notion_api_key = st.secrets.get("notion", {}).get("NOTION_API_KEY")
                if not notion_api_key:
                    raise ValueError("Notion API key required - add to .streamlit/secrets.toml")
            
            self.notion = Client(auth=notion_api_key)
            
            # Get database IDs from Streamlit secrets
            import streamlit as st
            self.client_database_id = st.secrets.get("notion", {}).get("NOTION_DATABASE_ID")
            self.content_samples_database_id = st.secrets.get("notion", {}).get("Content_Samples_database_ID")
            self.voice_guidelines_database_id = st.secrets.get("notion", {}).get("voice_guidelines_database_id")
    
    def get_client_list(self):
        """Get a list of all clients"""
        if not self.client_database_id:
            return {}
            
        response = self._retry_operation(
            self.notion.databases.query,
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
            
        print(f"DEBUG: Attempting to create client with database_id: {self.client_database_id}")
        print(f"DEBUG: Client name: {client_name}, Industry: {industry}")
        
        try:
            response = self._retry_operation(
                self.notion.pages.create,
                parent={"database_id": self.client_database_id},
                properties={
                    "Name": {"title": [{"text": {"content": client_name}}]},
                    "Industry": {"rich_text": [{"text": {"content": industry}}]},
                    "Research_Status": {"select": {"name": "In Progress"}}
                }
            )
            print(f"DEBUG: Successfully created client with ID: {response['id']}")
            return response["id"]
        except Exception as e:
            print(f"DEBUG: Full error creating client: {type(e).__name__}: {str(e)}")
            print(f"DEBUG: Database ID was: {self.client_database_id}")
            print(f"DEBUG: Notion client exists: {self.notion is not None}")
            logger.error(f"Error creating new client: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_client_page_id(self, client_name):
        """Get the page ID for a client by name"""
        if not self.client_database_id:
            return None
            
        response = self._retry_operation(
            self.notion.databases.query,
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
            page = self._retry_operation(
                self.notion.pages.retrieve,
                page_id=client_page_id
            )
            profile = {"id": client_page_id}
            props = page.get("properties", {})
            
            # Basic properties
            if "Name" in props and props["Name"].get("title") and props["Name"]["title"]:
                profile["Name"] = props["Name"]["title"][0]["text"]["content"]
            
            if "Industry" in props and props["Industry"].get("select"):
                profile["Industry"] = props["Industry"]["select"]["name"]
            
            # Rich text properties
            rich_text_props = [
                "Product_Service_Description", "Target_Audience", "Ideal_Target_Audience",
                "Brand_Mission", "Website", "Contact_Email", "Phone_Number",
                "Location", "LinkedIn_URL", "Twitter_URL", "Facebook_URL", "Instagram_URL", "Other_Social_Media",
                "Brand_Values"
            ]
            
            for prop in rich_text_props:
                if prop in props and props[prop].get("rich_text") and props[prop]["rich_text"]:
                    profile[prop] = props[prop]["rich_text"][0]["text"]["content"]
            
            # Multi-select properties
            multi_select_props = ["Desired_Emotional_Impact", "Brand_Personality"]
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
        try:
            print(f"\n=== DB MANAGER UPDATE DEBUG ===")
            print(f"Page ID: {client_page_id}")
            print(f"Updates received: {json.dumps(profile_data, indent=2)}")
            
            properties = {}
            
            # Process ALL fields dynamically instead of using hardcoded lists
            for field, value in profile_data.items():
                if value is None or value == "" or value == "Not found":
                    continue
                
                # Special handling for specific field types based on Notion schema
                if field == "Research_Status":
                    # Select field
                    properties[field] = {"select": {"name": str(value)}}
                    
                elif field == "Website":
                    # URL field
                    properties[field] = {"url": str(value)}
                    
               # elif field == "Company_Size":
                    # Select field - ensure it matches Notion's select options
                 #   if value and str(value).strip():
                        # Map common values to Notion's expected options
                     #   size_mapping = {
                      #      "Solo entrepreneur": "1-10 employees",
                       #     "1-5 employees": "1-10 employees",
                       #     "6-10 employees": "1-10 employees",
                        #    "Small": "11-50 employees",
                        #    "Medium": "51-200 employees",
                        #    "Large": "201-500 employees",
                        #    "Enterprise": "501+ employees"
                       # }
                      #  mapped_value = size_mapping.get(str(value), str(value))
                      #  properties[field] = {"select": {"name": mapped_value}}
                        
                elif field == "Last_Updated":
                    # Date field
                    properties[field] = {"date": {"start": str(value)}}
                    
                elif field == "Contact_Email":
                    # Email field
                    if "@" in str(value):  # Basic email validation
                        properties[field] = {"email": str(value)}
                    else:
                        # If not a valid email, put in rich text
                        properties[field] = {"rich_text": [{"text": {"content": str(value)[:2000]}}]}
                        
                elif field == "Phone_Number":
                    # Phone field
                    properties[field] = {"phone_number": str(value)}
                    
                elif field == "Deep_Research_Workflow":
                    # This is JSON data, store as rich text
                    content = str(value)[:2000]  # Notion limit
                    properties[field] = {"rich_text": [{"text": {"content": content}}]}
                    
                elif field in ["Brand_Personality_Traits", "Voice_Characteristics"]:
                    # Multi-select fields (if they exist in the schema)
                    if isinstance(value, list):
                        # Only add if the field exists in Notion schema
                        properties[field] = {"multi_select": [{"name": str(item)[:100]} for item in value[:10]]}  # Limit to 10 items
                    else:
                        # If not a list, convert to rich text
                        properties[field] = {"rich_text": [{"text": {"content": str(value)[:2000]}}]}
                        
                else:
                    # Default: Everything else goes to rich_text
                    # Handle different data types appropriately
                    if isinstance(value, (dict, list)):
                        # If it's already been formatted by _format_for_notion, it's a string
                        # Otherwise, convert to a readable format
                        if isinstance(value, str):
                            formatted_text = value
                        else:
                            # Pretty print JSON for readability
                            formatted_text = json.dumps(value, indent=2)
                    else:
                        formatted_text = str(value)
                    
                    # Apply Notion's character limit for rich text
                    if len(formatted_text) > 2000:
                        formatted_text = formatted_text[:1997] + "..."
                    
                    properties[field] = {"rich_text": [{"text": {"content": formatted_text}}]}
            
            # Always ensure Research_Status is set if not provided
            if "Research_Status" not in properties and profile_data.get("Research_Status") != "Website Data Extracted":
                properties["Research_Status"] = {"select": {"name": "In Progress"}}
            
            print(f"\nFinal properties object has {len(properties)} fields")
            print(f"Fields being updated: {list(properties.keys())}")
            
            # Only show first 500 chars of each field in debug to avoid clutter
            print("\nField preview:")
            for field, prop in properties.items():
                if "rich_text" in prop:
                    content = prop["rich_text"][0]["text"]["content"]
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"  {field}: {preview}")
                else:
                    print(f"  {field}: {prop}")
            
            response = self._retry_operation(
                self.notion.pages.update,
                page_id=client_page_id,
                properties=properties
            )
            print(f"Notion API response: Success")
            return True
        except Exception as e:
            print(f"Notion API error: {str(e)}")
            import traceback
            traceback.print_exc()
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
            page = self._retry_operation(
                self.notion.pages.retrieve,
                page_id=client_page_id
            )
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
                    "Last_Tool_Completed": {"rich_text": [{"text": {"content": tool_name}}]}
                }
                
                self._retry_operation(
                    self.notion.pages.update,
                    page_id=client_page_id,
                    properties=properties_to_update
                )
                return True
            except Exception:
                return False
        return False
    
    def update_tool_completion(self, client_page_id: str, tool_name: str, completed: bool = True):
        """Update tool completion checkbox using new schema fields"""
        field_map = {
            "brand_builder": "Brand_Builder_Complete",
            "content_collector": "Content_Collector_Complete",
            "voice_auditor": "Voice_Auditor_Complete",
            "audience_definer": "Audience_Definer_Complete",
            "voice_traits_builder": "Voice_Traits_Builder_Complete",
            "gap_analyzer": "Gap_Analyzer_Complete",
            "content_rewriter": "Content_Rewriter_Complete",
            "guidelines_finalizer": "Guidelines_Finalizer_Complete"
        }
        
        if tool_name not in field_map:
            return False
            
        try:
            properties = {
                field_map[tool_name]: self.format_checkbox(completed),
                "Last_Tool_Completed": self.format_rich_text(tool_name)
            }
            
            self._retry_operation(
                self.notion.pages.update,
                page_id=client_page_id,
                properties=properties
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update tool completion: {str(e)}")
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
                "Deep_Research_Workflow": workflow_json
            })
            
            return success
        except Exception as e:
            logger.error(f"Error saving workflow step: {str(e)}")
            return False
    
    def get_workflow_step_status(self, client_page_id, step_name):
        """Check if a workflow step is completed"""
        workflow_data = self.get_deep_research_data(client_page_id)
        return step_name in workflow_data and workflow_data[step_name].get("status") == "completed"
    
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
    
    def _get_current_date(self):
        """Get current date in ISO format """
        return datetime.now().strftime("%Y-%m-%d")


