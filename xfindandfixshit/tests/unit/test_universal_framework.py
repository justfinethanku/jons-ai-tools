"""
Unit tests for universal_framework.py
Tests core functionality without external dependencies.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from frameworks.universal_framework import (
    enhance_prompt_with_client_context,
    outputs_to_txt_bytes,
    call_openai_api,
    call_gemini_api
)

class TestPromptEnhancement:
    """Test prompt enhancement with client context"""
    
    def test_enhance_prompt_with_client_context_no_client(self):
        """Test prompt enhancement when no client data provided"""
        prompt = "Generate marketing copy"
        result = enhance_prompt_with_client_context(prompt, None)
        assert result == prompt
        
    def test_enhance_prompt_with_client_context_basic(self, sample_client_data):
        """Test basic prompt enhancement with client data"""
        prompt = "Generate marketing copy"
        result = enhance_prompt_with_client_context(prompt, sample_client_data)
        
        assert "CLIENT CONTEXT" in result
        assert sample_client_data["name"] in result
        assert sample_client_data["brand_voice"] in result
        assert sample_client_data["tone"] in result
        assert sample_client_data["industry"] in result
        
    def test_enhance_prompt_with_client_context_with_role(self, sample_client_data):
        """Test prompt enhancement with existing Role section"""
        prompt = "# Role\nYou are a marketing expert\n\nGenerate copy"
        result = enhance_prompt_with_client_context(prompt, sample_client_data)
        
        assert "# Role" in result
        assert "CLIENT CONTEXT" in result
        assert "marketing expert" in result
        
    def test_enhance_prompt_with_keywords(self, sample_client_data):
        """Test prompt enhancement includes keywords"""
        result = enhance_prompt_with_client_context("Test prompt", sample_client_data)
        
        assert "innovation" in result
        assert "technology" in result
        assert "Keywords to include:" in result
        
    def test_enhance_prompt_with_custom_prompts(self, sample_client_data):
        """Test prompt enhancement includes custom instructions"""
        result = enhance_prompt_with_client_context("Test prompt", sample_client_data)
        
        assert sample_client_data["custom_prompts"] in result
        assert "Custom Instructions:" in result

class TestOutputUtilities:
    """Test output utility functions"""
    
    def test_outputs_to_txt_bytes_empty(self):
        """Test conversion of empty outputs dict"""
        result = outputs_to_txt_bytes({})
        assert isinstance(result, bytes)
        assert len(result) == 0
        
    def test_outputs_to_txt_bytes_single_output(self):
        """Test conversion of single output"""
        outputs = {"Title": "Content here"}
        result = outputs_to_txt_bytes(outputs)
        
        decoded = result.decode("utf-8")
        assert "Title" in decoded
        assert "Content here" in decoded
        assert "=" * len("Title") in decoded
        
    def test_outputs_to_txt_bytes_multiple_outputs(self):
        """Test conversion of multiple outputs"""
        outputs = {
            "Section 1": "Content 1",
            "Section 2": "Content 2"
        }
        result = outputs_to_txt_bytes(outputs)
        
        decoded = result.decode("utf-8")
        assert "Section 1" in decoded
        assert "Section 2" in decoded
        assert "Content 1" in decoded
        assert "Content 2" in decoded

class TestAPIIntegrations:
    """Test API integration functions"""
    
    @patch('openai.ChatCompletion.create')
    def test_call_openai_api_success(self, mock_openai, mock_openai_response):
        """Test successful OpenAI API call"""
        mock_openai.return_value = mock_openai_response
        
        result = call_openai_api("Test prompt")
        
        assert result == "Test OpenAI response"
        mock_openai.assert_called_once()
        
    @patch('openai.ChatCompletion.create')
    def test_call_openai_api_failure(self, mock_openai):
        """Test OpenAI API call failure"""
        mock_openai.side_effect = Exception("API Error")
        
        result = call_openai_api("Test prompt")
        
        assert "Error calling OpenAI API" in result
        assert "API Error" in result
        
    @patch('openai.ChatCompletion.create')
    def test_call_openai_api_custom_params(self, mock_openai, mock_openai_response):
        """Test OpenAI API call with custom parameters"""
        mock_openai.return_value = mock_openai_response
        
        result = call_openai_api("Test prompt", model="gpt-3.5-turbo", temperature=0.8)
        
        call_args = mock_openai.call_args
        assert call_args[1]["model"] == "gpt-3.5-turbo"
        assert call_args[1]["temperature"] == 0.8
        
    @patch('google.generativeai.GenerativeModel')
    def test_call_gemini_api_success(self, mock_gemini_model, mock_gemini_response):
        """Test successful Gemini API call"""
        mock_instance = Mock()
        mock_instance.generate_content.return_value = mock_gemini_response
        mock_gemini_model.return_value = mock_instance
        
        result = call_gemini_api("Test prompt")
        
        assert result == "Test Gemini response"
        mock_instance.generate_content.assert_called_once_with("Test prompt")
        
    @patch('google.generativeai.GenerativeModel')
    def test_call_gemini_api_with_schema(self, mock_gemini_model, mock_gemini_response):
        """Test Gemini API call with response schema"""
        mock_instance = Mock()
        mock_instance.generate_content.return_value = mock_gemini_response
        mock_gemini_model.return_value = mock_instance
        
        schema = {"type": "object", "properties": {"result": {"type": "string"}}}
        result = call_gemini_api("Test prompt", response_schema=schema)
        
        # Should return the structured JSON response
        assert '{"structured": "response"}' in result
        
    @patch('google.generativeai.GenerativeModel')
    def test_call_gemini_api_failure(self, mock_gemini_model):
        """Test Gemini API call failure"""
        mock_instance = Mock()
        mock_instance.generate_content.side_effect = Exception("API Error")
        mock_gemini_model.return_value = mock_instance
        
        result = call_gemini_api("Test prompt")
        
        assert "Error:" in result
        assert "API Error" in result

@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_enhance_prompt_empty_client_data(self):
        """Test prompt enhancement with empty client data"""
        result = enhance_prompt_with_client_context("Test", {})
        assert "CLIENT CONTEXT" in result
        assert "Unknown" in result  # Default name
        
    def test_enhance_prompt_partial_client_data(self):
        """Test prompt enhancement with partial client data"""
        partial_data = {"name": "Test Client"}
        result = enhance_prompt_with_client_context("Test", partial_data)
        
        assert "Test Client" in result
        assert "Professional" in result  # Default brand voice
        assert "General" in result  # Default industry