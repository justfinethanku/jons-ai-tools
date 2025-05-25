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