"""
Test suite for shared/utils.py module.

Tests all utility functions for security, edge cases, and correctness.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
import hashlib
import json
from datetime import datetime

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.utils import (
    validate_file_path,
    sanitize_input,
    format_output,
    calculate_metrics,
    hash_content,
    timestamp_now,
    safe_json_parse,
    safe_json_stringify,
    get_environment_variable,
    parse_configuration_string
)


class TestValidateFilePath:
    """Test file path validation functionality."""
    
    def test_valid_file_path_string(self):
        """Test validation of valid file path as string."""
        result, message = validate_file_path("/tmp/test.txt")
        assert result == True
        assert message == ""
    
    def test_valid_file_path_pathlib(self):
        """Test validation of valid file path as Path object."""
        result, message = validate_file_path(Path("/tmp/test.txt"))
        assert result == True
        assert message == ""
    
    def test_path_traversal_attack_prevention(self):
        """Test prevention of path traversal attacks."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "/tmp/../../../etc/passwd",
            "subdir/../../etc/passwd"
        ]
        
        for path in malicious_paths:
            result, message = validate_file_path(path)
            assert result == False
            assert "path traversal" in message.lower() or "security" in message.lower()
    
    def test_file_extension_validation(self):
        """Test file extension validation."""
        # Valid extensions
        result, message = validate_file_path("/tmp/test.txt", allowed_extensions=[".txt", ".md"])
        assert result == True
        
        # Invalid extensions
        result, message = validate_file_path("/tmp/test.exe", allowed_extensions=[".txt", ".md"])
        assert result == False
        assert "extension" in message.lower()
    
    def test_file_existence_check(self):
        """Test file existence validation."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Test existing file
            result, message = validate_file_path(tmp_path, must_exist=True)
            assert result == True
            
            # Test non-existing file
            result, message = validate_file_path("/nonexistent/file.txt", must_exist=True)
            assert result == False
            assert "not exist" in message.lower() or "not found" in message.lower()
        finally:
            os.unlink(tmp_path)
    
    def test_empty_path(self):
        """Test validation of empty paths."""
        result, message = validate_file_path("")
        assert result == False
        assert "empty" in message.lower() or "invalid" in message.lower()
    
    def test_none_path(self):
        """Test validation of None path."""
        with pytest.raises((TypeError, AttributeError)):
            validate_file_path(None)


class TestSanitizeInput:
    """Test input sanitization functionality."""
    
    def test_sanitize_clean_string(self):
        """Test sanitization of clean string input."""
        result = sanitize_input("Hello World")
        assert result == "Hello World"
    
    def test_sanitize_string_with_dangerous_chars(self):
        """Test removal of potentially dangerous characters."""
        dangerous_input = "Hello<script>alert('xss')</script>World"
        result = sanitize_input(dangerous_input)
        assert "<script>" not in result
        assert "alert" not in result
        assert "Hello" in result and "World" in result
    
    def test_sanitize_string_length_limit(self):
        """Test string length limitation."""
        long_string = "A" * 1000
        result = sanitize_input(long_string, max_length=100)
        assert len(result) <= 100
    
    def test_sanitize_string_allowed_chars(self):
        """Test character filtering."""
        input_str = "Hello123!@#$%"
        result = sanitize_input(input_str, allowed_chars=r"[A-Za-z0-9\s]")
        assert "!" not in result
        assert "@" not in result
        assert "Hello123" in result
    
    def test_sanitize_dictionary(self):
        """Test sanitization of dictionary input."""
        input_dict = {
            "name": "Test<script>",
            "value": "Safe content",
            "nested": {
                "key": "More<script>content"
            }
        }
        result = sanitize_input(input_dict)
        assert isinstance(result, dict)
        assert "<script>" not in str(result)
        assert "Test" in result["name"]
        assert result["value"] == "Safe content"
    
    def test_sanitize_empty_input(self):
        """Test sanitization of empty inputs."""
        assert sanitize_input("") == ""
        assert sanitize_input({}) == {}
    
    def test_sanitize_none_input(self):
        """Test handling of None input."""
        result = sanitize_input(None)
        assert result is None or result == ""


class TestFormatOutput:
    """Test output formatting functionality."""
    
    def test_format_json_pretty(self):
        """Test pretty JSON formatting."""
        data = {"name": "test", "value": 123}
        result = format_output(data, format_type="json", pretty=True)
        assert json.loads(result) == data  # Valid JSON
        assert "\n" in result  # Pretty formatted
    
    def test_format_json_compact(self):
        """Test compact JSON formatting."""
        data = {"name": "test", "value": 123}
        result = format_output(data, format_type="json", pretty=False)
        assert json.loads(result) == data
        assert "\n" not in result  # Compact
    
    def test_format_table(self):
        """Test table formatting."""
        data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]
        result = format_output(data, format_type="table")
        assert "name" in result and "age" in result
        assert "John" in result and "Jane" in result
    
    def test_format_text(self):
        """Test plain text formatting."""
        data = {"message": "Hello World"}
        result = format_output(data, format_type="text")
        assert isinstance(result, str)
        assert "Hello World" in result
    
    def test_format_unsupported_type(self):
        """Test handling of unsupported format types."""
        data = {"test": "value"}
        result = format_output(data, format_type="unsupported")
        # Should fallback to JSON or return error message
        assert isinstance(result, str)


class TestCalculateMetrics:
    """Test metrics calculation functionality."""
    
    def test_calculate_text_metrics(self):
        """Test calculation of text metrics."""
        text = "Hello world. This is a test sentence with multiple words."
        metrics = calculate_metrics(text)
        
        assert "character_count" in metrics
        assert "word_count" in metrics
        assert "sentence_count" in metrics
        assert metrics["character_count"] > 0
        assert metrics["word_count"] > 0
        assert metrics["sentence_count"] > 0
    
    def test_calculate_complexity_metrics(self):
        """Test complexity metrics calculation."""
        text = "This is a simple sentence. This is a more complex sentence with additional clauses."
        metrics = calculate_metrics(text)
        
        assert "complexity_score" in metrics
        assert "readability_score" in metrics
    
    def test_calculate_empty_text_metrics(self):
        """Test metrics for empty text."""
        metrics = calculate_metrics("")
        assert metrics["character_count"] == 0
        assert metrics["word_count"] == 0
        assert metrics["sentence_count"] == 0


class TestHashContent:
    """Test content hashing functionality."""
    
    def test_hash_string_content(self):
        """Test hashing of string content."""
        content = "Hello World"
        hash_result = hash_content(content)
        
        # Should return consistent hash
        expected_hash = hashlib.sha256(content.encode()).hexdigest()
        assert hash_result == expected_hash
    
    def test_hash_bytes_content(self):
        """Test hashing of bytes content."""
        content = b"Hello World"
        hash_result = hash_content(content)
        
        expected_hash = hashlib.sha256(content).hexdigest()
        assert hash_result == expected_hash
    
    def test_hash_consistency(self):
        """Test that same content produces same hash."""
        content = "Consistent content"
        hash1 = hash_content(content)
        hash2 = hash_content(content)
        assert hash1 == hash2
    
    def test_hash_different_content(self):
        """Test that different content produces different hashes."""
        hash1 = hash_content("Content 1")
        hash2 = hash_content("Content 2")
        assert hash1 != hash2


class TestTimestampNow:
    """Test timestamp generation functionality."""
    
    def test_timestamp_iso_format(self):
        """Test ISO format timestamp generation."""
        timestamp = timestamp_now(format_type="iso")
        # Should be parseable as ISO format
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    def test_timestamp_unix_format(self):
        """Test Unix timestamp generation."""
        timestamp = timestamp_now(format_type="unix")
        assert isinstance(timestamp, (int, float))
        assert timestamp > 0
    
    def test_timestamp_human_format(self):
        """Test human-readable timestamp generation."""
        timestamp = timestamp_now(format_type="human")
        assert isinstance(timestamp, str)
        assert len(timestamp) > 10  # Should be reasonably long
    
    def test_timestamp_consistency(self):
        """Test timestamp consistency within short timeframe."""
        ts1 = timestamp_now(format_type="unix")
        ts2 = timestamp_now(format_type="unix")
        # Should be very close in time
        assert abs(ts1 - ts2) < 1  # Less than 1 second difference


class TestSafeJsonParse:
    """Test safe JSON parsing functionality."""
    
    def test_parse_valid_json(self):
        """Test parsing of valid JSON."""
        json_str = '{"name": "test", "value": 123}'
        result = safe_json_parse(json_str)
        assert result == {"name": "test", "value": 123}
    
    def test_parse_invalid_json(self):
        """Test handling of invalid JSON."""
        invalid_json = '{"name": "test", "value":}'
        result = safe_json_parse(invalid_json)
        assert result is None or result == {}
    
    def test_parse_empty_string(self):
        """Test parsing of empty string."""
        result = safe_json_parse("")
        assert result is None or result == {}
    
    def test_parse_with_fallback(self):
        """Test parsing with fallback value."""
        fallback = {"default": "value"}
        result = safe_json_parse("invalid json", fallback=fallback)
        assert result == fallback


class TestSafeJsonStringify:
    """Test safe JSON stringification functionality."""
    
    def test_stringify_valid_object(self):
        """Test stringification of valid object."""
        obj = {"name": "test", "value": 123}
        result = safe_json_stringify(obj)
        assert json.loads(result) == obj
    
    def test_stringify_complex_object(self):
        """Test stringification of complex nested object."""
        obj = {
            "simple": "value",
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "number": 123.45,
            "boolean": True,
            "null": None
        }
        result = safe_json_stringify(obj)
        parsed = json.loads(result)
        assert parsed == obj
    
    def test_stringify_unserializable_object(self):
        """Test handling of unserializable objects."""
        class CustomObject:
            pass
        
        obj = {"custom": CustomObject()}
        result = safe_json_stringify(obj)
        # Should handle gracefully, either by exclusion or string conversion
        assert isinstance(result, str)


class TestGetEnvironmentVariable:
    """Test environment variable access functionality."""
    
    def test_get_existing_variable(self):
        """Test retrieval of existing environment variable."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = get_environment_variable("TEST_VAR")
            assert result == "test_value"
    
    def test_get_nonexistent_variable(self):
        """Test retrieval of non-existent variable."""
        result = get_environment_variable("NONEXISTENT_VAR")
        assert result is None
    
    def test_get_variable_with_default(self):
        """Test retrieval with default value."""
        result = get_environment_variable("NONEXISTENT_VAR", default="default_value")
        assert result == "default_value"
    
    def test_get_variable_type_conversion(self):
        """Test type conversion of environment variables."""
        with patch.dict(os.environ, {"TEST_INT": "123", "TEST_BOOL": "true"}):
            int_result = get_environment_variable("TEST_INT", var_type=int)
            bool_result = get_environment_variable("TEST_BOOL", var_type=bool)
            
            assert int_result == 123
            assert bool_result == True


class TestParseConfigurationString:
    """Test configuration string parsing functionality."""
    
    def test_parse_key_value_pairs(self):
        """Test parsing of key=value configuration string."""
        config_str = "key1=value1;key2=value2;key3=value3"
        result = parse_configuration_string(config_str)
        
        expected = {"key1": "value1", "key2": "value2", "key3": "value3"}
        assert result == expected
    
    def test_parse_json_configuration(self):
        """Test parsing of JSON configuration string."""
        config_str = '{"key1": "value1", "key2": 123, "key3": true}'
        result = parse_configuration_string(config_str, format_type="json")
        
        expected = {"key1": "value1", "key2": 123, "key3": True}
        assert result == expected
    
    def test_parse_invalid_configuration(self):
        """Test handling of invalid configuration string."""
        result = parse_configuration_string("invalid config string")
        assert result == {} or result is None
    
    def test_parse_empty_configuration(self):
        """Test parsing of empty configuration string."""
        result = parse_configuration_string("")
        assert result == {}


if __name__ == "__main__":
    pytest.main([__file__])