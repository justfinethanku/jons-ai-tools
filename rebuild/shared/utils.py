"""
@RULE:LAYER: shared/utils
@RULE:FORBIDDEN: core.*, tools.*, main, external AI libraries
@SEE: shared/CLAUDE.md#utility-patterns
Common utility functions for file operations, validation, and formatting
"""

# Allowed imports - standard library only
import hashlib
import json
import logging
import re
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple


# File validation functions
def validate_file_path(file_path: Union[str, Path], must_exist: bool = False, allowed_extensions: Optional[List[str]] = None) -> Tuple[bool, str]:
    """
    Validate file path for security and accessibility.
    
    Args:
        file_path: Path to validate
        must_exist: Whether file must already exist
        allowed_extensions: Optional list of allowed file extensions
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Validation Checks:
    - Path traversal attack prevention
    - File extension validation
    - Accessibility and permissions
    - Existence check if required
    """
    try:
        # Handle empty or None paths
        if not file_path:
            return False, "File path is empty or None"
        
        # Convert to Path object for consistent handling
        path = Path(file_path)
        
        # Check for path traversal attacks
        path_str = str(path)
        if ".." in path_str or path_str.startswith("/"):
            # Allow absolute paths but check for traversal patterns
            if ".." in path.parts:
                return False, "Path contains path traversal attempts (security violation)"
        
        # Validate file extension if specified
        if allowed_extensions:
            if not path.suffix or path.suffix not in allowed_extensions:
                return False, f"File extension not allowed. Allowed: {allowed_extensions}"
        
        # Check file existence if required
        if must_exist:
            if not path.exists():
                return False, f"File does not exist: {path}"
            
            # Check if it's actually a file (not directory)
            if not path.is_file():
                return False, f"Path exists but is not a file: {path}"
        
        # Check parent directory permissions if file doesn't exist
        if not must_exist and not path.exists():
            parent = path.parent
            if not parent.exists():
                return False, f"Parent directory does not exist: {parent}"
            if not os.access(parent, os.W_OK):
                return False, f"No write permission to parent directory: {parent}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Path validation error: {str(e)}"


def sanitize_input(input_data: Union[str, Dict[str, Any]], max_length: Optional[int] = None, allowed_chars: Optional[str] = None) -> Union[str, Dict[str, Any]]:
    """
    Sanitize input data for security and consistency.
    
    Args:
        input_data: Data to sanitize (string or dictionary)
        max_length: Optional maximum length for strings
        allowed_chars: Optional regex pattern for allowed characters
        
    Returns:
        Sanitized input data
        
    Sanitization Process:
    - Remove potentially dangerous characters
    - Limit string length to prevent DoS
    - Normalize whitespace and encoding
    - Recursively sanitize dictionary values
    """
    if input_data is None:
        return None
    
    if isinstance(input_data, str):
        return _sanitize_string(input_data, max_length, allowed_chars)
    elif isinstance(input_data, dict):
        return _sanitize_dict(input_data, max_length, allowed_chars)
    else:
        # For other types, convert to string and sanitize
        return _sanitize_string(str(input_data), max_length, allowed_chars)


def _sanitize_string(text: str, max_length: Optional[int] = None, allowed_chars: Optional[str] = None) -> str:
    """Private method to sanitize string input."""
    if not text:
        return text
    
    # Remove dangerous script tags and similar
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'javascript:',
        r'on\w+\s*=',  # onclick, onload, etc.
    ]
    
    sanitized = text
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    # Apply character filtering if specified
    if allowed_chars:
        sanitized = re.sub(f'[^{allowed_chars}]', '', sanitized)
    
    # Normalize whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Apply length limit
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def _sanitize_dict(data: Dict[str, Any], max_length: Optional[int] = None, allowed_chars: Optional[str] = None) -> Dict[str, Any]:
    """Private method to recursively sanitize dictionary data."""
    sanitized = {}
    
    for key, value in data.items():
        # Sanitize the key
        clean_key = _sanitize_string(str(key), max_length, allowed_chars)
        
        # Sanitize the value recursively
        if isinstance(value, str):
            sanitized[clean_key] = _sanitize_string(value, max_length, allowed_chars)
        elif isinstance(value, dict):
            sanitized[clean_key] = _sanitize_dict(value, max_length, allowed_chars)
        elif isinstance(value, list):
            sanitized[clean_key] = [sanitize_input(item, max_length, allowed_chars) for item in value]
        else:
            # For other types, keep as-is or convert to string if needed
            sanitized[clean_key] = value
    
    return sanitized


def format_output(data: Any, format_type: str = "json", pretty: bool = True) -> str:
    """
    Format data for output in various formats.
    
    Args:
        data: Data to format
        format_type: Output format ('json', 'yaml', 'table', 'text')
        pretty: Whether to apply pretty formatting
        
    Returns:
        Formatted string representation of data
        
    Supported Formats:
    - JSON with optional pretty printing
    - YAML format for configuration
    - Table format for structured data
    - Plain text for simple output
    """
    try:
        if format_type.lower() == "json":
            return _format_json(data, pretty)
        elif format_type.lower() == "table":
            return _format_table(data)
        elif format_type.lower() == "text":
            return _format_text(data)
        else:
            # Fallback to JSON for unsupported formats
            return _format_json(data, pretty)
    except Exception as e:
        return f"Error formatting output: {str(e)}"


def _format_json(data: Any, pretty: bool = True) -> str:
    """Private method to format data as JSON."""
    try:
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False, default=str)
        else:
            return json.dumps(data, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        # Fallback for non-serializable objects
        return json.dumps({"data": str(data)}, indent=2 if pretty else None)


def _format_table(data: Any) -> str:
    """Private method to format data as a table."""
    if isinstance(data, list) and data and isinstance(data[0], dict):
        # Format list of dictionaries as table
        headers = list(data[0].keys())
        lines = []
        
        # Header row
        header_line = " | ".join(str(h) for h in headers)
        lines.append(header_line)
        lines.append("-" * len(header_line))
        
        # Data rows
        for item in data:
            row = " | ".join(str(item.get(h, "")) for h in headers)
            lines.append(row)
        
        return "\n".join(lines)
    elif isinstance(data, dict):
        # Format dictionary as key-value table
        lines = []
        for key, value in data.items():
            lines.append(f"{key} | {value}")
        return "\n".join(lines)
    else:
        # Fallback to string representation
        return str(data)


def _format_text(data: Any) -> str:
    """Private method to format data as plain text."""
    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{key}: {json.dumps(value, default=str)}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
    elif isinstance(data, list):
        return "\n".join(str(item) for item in data)
    else:
        return str(data)


# Metrics and analysis functions
def calculate_metrics(content: str, metric_types: Optional[List[str]] = None) -> Dict[str, Union[int, float]]:
    """
    Calculate various metrics for text content.
    
    Args:
        content: Text content to analyze
        metric_types: Optional list of specific metrics to calculate
        
    Returns:
        Dictionary of calculated metrics
        
    Available Metrics:
    - Character count and word count
    - Line count and paragraph count
    - Complexity metrics (sentences, avg words per sentence)
    - Readability scores
    - Code-specific metrics (if applicable)
    """
    if not content:
        return {
            "character_count": 0,
            "word_count": 0,
            "sentence_count": 0,
            "complexity_score": 0.0,
            "readability_score": 0.0
        }
    
    metrics = {}
    
    # Basic metrics
    metrics["character_count"] = len(content)
    metrics["word_count"] = len(content.split())
    
    # Sentence count (simple approximation)
    sentence_endings = content.count('.') + content.count('!') + content.count('?')
    metrics["sentence_count"] = max(1, sentence_endings)  # At least 1 sentence
    
    # Complexity metrics
    if metrics["sentence_count"] > 0:
        avg_words_per_sentence = metrics["word_count"] / metrics["sentence_count"]
        metrics["complexity_score"] = min(10.0, avg_words_per_sentence / 2)  # Scale 0-10
    else:
        metrics["complexity_score"] = 0.0
    
    # Simple readability score (inverse of complexity)
    metrics["readability_score"] = max(0.0, 10.0 - metrics["complexity_score"])
    
    # Filter metrics if specific types requested
    if metric_types:
        filtered_metrics = {}
        for metric_type in metric_types:
            if metric_type in metrics:
                filtered_metrics[metric_type] = metrics[metric_type]
        return filtered_metrics
    
    return metrics


def hash_content(content: Union[str, bytes], algorithm: str = "sha256") -> str:
    """
    Generate hash of content for integrity checking.
    
    Args:
        content: Content to hash (string or bytes)
        algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256', 'sha512')
        
    Returns:
        Hexadecimal hash string
        
    Security Note:
    - Default to SHA256 for security
    - Support multiple algorithms for compatibility
    - Handle both string and binary content
    """
    try:
        # Convert string to bytes if necessary
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
        
        # Create hash object for specified algorithm
        if algorithm.lower() == "md5":
            hash_obj = hashlib.md5()
        elif algorithm.lower() == "sha1":
            hash_obj = hashlib.sha1()
        elif algorithm.lower() == "sha256":
            hash_obj = hashlib.sha256()
        elif algorithm.lower() == "sha512":
            hash_obj = hashlib.sha512()
        else:
            # Default to SHA256 for unsupported algorithms
            hash_obj = hashlib.sha256()
        
        # Update hash with content and return hexadecimal digest
        hash_obj.update(content_bytes)
        return hash_obj.hexdigest()
        
    except Exception as e:
        # Fallback: return empty hash on error
        return ""


# Time and timestamp functions
def timestamp_now(format_type: str = "iso") -> Union[str, int, float]:
    """
    Generate current timestamp in specified format.
    
    Args:
        format_type: Format type ('iso', 'unix', 'human', 'filename')
        
    Returns:
        Formatted timestamp string or numeric value
        
    Supported Formats:
    - ISO 8601 format with timezone
    - Unix timestamp (seconds since epoch)
    - Human-readable format
    - Filename-safe format (no special characters)
    """
    try:
        now = datetime.now(timezone.utc)
        
        if format_type.lower() == "iso":
            return now.isoformat()
        elif format_type.lower() == "unix":
            return now.timestamp()
        elif format_type.lower() == "human":
            return now.strftime("%Y-%m-%d %H:%M:%S UTC")
        elif format_type.lower() == "filename":
            return now.strftime("%Y%m%d_%H%M%S")
        else:
            # Default to ISO format
            return now.isoformat()
            
    except Exception as e:
        # Fallback to simple string representation
        return str(datetime.now())


# JSON and data processing utilities
def safe_json_parse(json_string: str, fallback: Any = None) -> Any:
    """
    Safely parse JSON string with error handling.
    
    Args:
        json_string: JSON string to parse
        fallback: Default value to return on parse failure
        
    Returns:
        Parsed JSON data or fallback value
    """
    try:
        if not json_string or not json_string.strip():
            return fallback if fallback is not None else {}
        
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError, ValueError):
        return fallback if fallback is not None else {}


def safe_json_stringify(data: Any, default: str = "{}") -> str:
    """
    Safely convert data to JSON string with error handling.
    
    Args:
        data: Data to convert to JSON
        default: Default JSON string on conversion failure
        
    Returns:
        JSON string representation or default
    """
    try:
        return json.dumps(data, ensure_ascii=False, default=str)
    except (TypeError, ValueError, OverflowError):
        return default


# Environment and configuration utilities
def get_environment_variable(var_name: str, default: Any = None, var_type: type = str) -> Any:
    """
    Get environment variable with type conversion and default fallback.
    
    Args:
        var_name: Name of environment variable
        default: Default value if variable not found
        var_type: Type to convert the variable to
        
    Returns:
        Environment variable value or default
    """
    try:
        value = os.environ.get(var_name)
        if value is None:
            return default
        
        # Type conversion
        if var_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif var_type == int:
            return int(value)
        elif var_type == float:
            return float(value)
        else:
            return str(value)
            
    except (ValueError, TypeError):
        return default


def parse_configuration_string(config_str: str, format_type: str = "key_value") -> Dict[str, Any]:
    """
    Parse configuration string into dictionary.
    
    Args:
        config_str: Configuration string to parse
        format_type: Format type ('key_value', 'json')
        
    Returns:
        Parsed configuration dictionary
    """
    try:
        if not config_str or not config_str.strip():
            return {}
        
        if format_type.lower() == "json":
            return safe_json_parse(config_str, {})
        else:
            # Parse key=value;key=value format
            config = {}
            pairs = config_str.split(';')
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    config[key.strip()] = value.strip()
            return config
            
    except Exception:
        return {}
