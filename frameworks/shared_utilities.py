"""
Shared utilities module to break circular dependencies.
Contains common functions used by multiple frameworks and tools.
"""

import json
import re
from typing import Dict, Any, Tuple, Optional

def clean_json_response(response_text: str) -> str:
    """
    Clean and extract JSON from API responses.
    
    Args:
        response_text: Raw response text that may contain JSON
        
    Returns:
        Cleaned JSON string
    """
    if not response_text:
        return "{}"
    
    # Remove markdown code blocks
    response_text = re.sub(r'```json\s*', '', response_text)
    response_text = re.sub(r'```\s*$', '', response_text)
    
    # Remove any leading/trailing whitespace
    response_text = response_text.strip()
    
    # Try to find JSON content between braces
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group()
    
    # Clean up common JSON formatting issues
    response_text = re.sub(r',\s*}', '}', response_text)  # Remove trailing commas
    response_text = re.sub(r',\s*]', ']', response_text)  # Remove trailing commas in arrays
    
    return response_text

def safe_json_parse(json_string: str, fallback: Optional[Dict] = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Safely parse JSON string with fallback handling.
    
    Args:
        json_string: JSON string to parse
        fallback: Fallback dictionary if parsing fails
        
    Returns:
        Tuple of (success: bool, parsed_data: dict)
    """
    if fallback is None:
        fallback = {}
    
    try:
        cleaned = clean_json_response(json_string)
        parsed = json.loads(cleaned)
        return True, parsed
    except (json.JSONDecodeError, Exception) as e:
        print(f"⚠️ JSON parsing failed: {str(e)}")
        return False, fallback

def validate_json_schema(data: Dict[str, Any], required_fields: list) -> Tuple[bool, list]:
    """
    Validate that JSON data contains required fields.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid: bool, missing_fields: list)
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields

def format_validation_error(missing_fields: list, context: str = "") -> str:
    """
    Format validation error message for missing fields.
    
    Args:
        missing_fields: List of missing field names
        context: Additional context for the error
        
    Returns:
        Formatted error message
    """
    if not missing_fields:
        return ""
    
    fields_str = ", ".join(missing_fields)
    base_msg = f"Missing required fields: {fields_str}"
    
    if context:
        return f"{context} - {base_msg}"
    
    return base_msg

def get_current_date() -> str:
    """Get current date in ISO format."""
    from datetime import datetime
    return datetime.now().isoformat()

def sanitize_text_for_notion(text: str, max_length: int = 2000) -> str:
    """
    Sanitize text for Notion rich text fields.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove any problematic characters
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', str(text))
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length-3] + "..."
    
    return sanitized

def extract_between_markers(text: str, start_marker: str, end_marker: str) -> str:
    """
    Extract content between two markers in text.
    
    Args:
        text: Source text
        start_marker: Starting marker
        end_marker: Ending marker
        
    Returns:
        Extracted content or empty string if not found
    """
    pattern = f"{re.escape(start_marker)}(.*?){re.escape(end_marker)}"
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    return ""

# Safe wrapper functions to avoid circular imports

def revise_prompt_safely(prompt: str, revision_request: str) -> str:
    """
    Safe wrapper for prompt revision to avoid circular imports.
    """
    try:
        # Import only when needed to avoid circular dependency
        from tools.prompt_refiner import revise_prompt
        return revise_prompt(prompt, revision_request)
    except ImportError as e:
        print(f"⚠️ Could not import prompt_refiner: {e}")
        return f"{prompt}\n\n[REVISION REQUESTED: {revision_request}]"

def extract_website_data_safely(client_name: str, website_url: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Safe wrapper for website data extraction to avoid circular imports.
    """
    try:
        # Import only when needed to avoid circular dependency
        from tools.brand_builder import extract_website_data
        return extract_website_data(client_name, website_url)
    except ImportError as e:
        error_msg = f"Could not import brand_builder: {e}"
        print(f"⚠️ {error_msg}")
        return False, None, error_msg

def analyze_brand_voice_safely(client_name: str, website_data: Dict) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Safe wrapper for brand voice analysis to avoid circular imports.
    """
    try:
        # Import only when needed to avoid circular dependency
        from tools.brand_builder import analyze_brand_voice
        return analyze_brand_voice(client_name, website_data)
    except ImportError as e:
        error_msg = f"Could not import brand_builder: {e}"
        print(f"⚠️ {error_msg}")
        return False, None, error_msg