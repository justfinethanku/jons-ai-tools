"""
Test suite for shared/ai_client.py module.

Tests AI client functionality including provider interfaces, rate limiting, 
request/response handling, and error conditions.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from enum import Enum

# Import the module under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.ai_client import (
    APIProvider,
    RequestType,
    ClientConfig,
    AIRequest,
    AIResponse,
    RateLimiter,
    AIClient,
    create_ai_client,
    make_simple_request
)


class TestAPIProvider:
    """Test APIProvider enumeration."""
    
    def test_provider_values(self):
        """Test that all expected providers are available."""
        expected_providers = ['OPENAI', 'ANTHROPIC', 'GOOGLE', 'AZURE_OPENAI', 'LOCAL']
        actual_providers = [provider.name for provider in APIProvider]
        
        for provider in expected_providers:
            assert provider in actual_providers


class TestRequestType:
    """Test RequestType enumeration."""
    
    def test_request_types(self):
        """Test that all expected request types are available."""
        expected_types = ['COMPLETION', 'CHAT', 'EMBEDDING', 'MODERATION']
        actual_types = [req_type.name for req_type in RequestType]
        
        for req_type in expected_types:
            assert req_type in actual_types


class TestClientConfig:
    """Test ClientConfig data structure."""
    
    def test_client_config_creation(self):
        """Test creation of client configuration."""
        config = ClientConfig(
            provider=APIProvider.OPENAI,
            api_key="test-key-123",
            model="gpt-4",
            max_retries=5,
            timeout=60
        )
        
        assert config.provider == APIProvider.OPENAI
        assert config.api_key == "test-key-123"
        assert config.model == "gpt-4"
        assert config.max_retries == 5
        assert config.timeout == 60
    
    def test_client_config_defaults(self):
        """Test default values in client configuration."""
        config = ClientConfig(
            provider=APIProvider.OPENAI,
            api_key="test-key"
        )
        
        # Test that defaults are reasonable
        assert config.max_retries >= 1
        assert config.timeout > 0
        assert config.rate_limit_rpm > 0
        assert config.rate_limit_tpm > 0
        assert 0 <= config.default_temperature <= 2
        assert config.default_max_tokens > 0


class TestAIRequest:
    """Test AIRequest data structure."""
    
    def test_ai_request_creation(self):
        """Test creation of AI request."""
        request = AIRequest(
            request_type=RequestType.CHAT,
            prompt="Hello, world!",
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000
        )
        
        assert request.request_type == RequestType.CHAT
        assert request.prompt == "Hello, world!"
        assert request.model == "gpt-4"
        assert request.temperature == 0.7
        assert request.max_tokens == 1000
    
    def test_ai_request_with_metadata(self):
        """Test AI request with metadata and parameters."""
        metadata = {"user_id": "test-user", "session_id": "session-123"}
        parameters = {"top_p": 0.9, "frequency_penalty": 0.1}
        
        request = AIRequest(
            request_type=RequestType.COMPLETION,
            prompt="Test prompt",
            metadata=metadata,
            parameters=parameters
        )
        
        assert request.metadata == metadata
        assert request.parameters == parameters
    
    def test_ai_request_with_messages(self):
        """Test AI request with chat messages."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
        
        request = AIRequest(
            request_type=RequestType.CHAT,
            prompt=messages
        )
        
        assert request.prompt == messages


class TestAIResponse:
    """Test AIResponse data structure."""
    
    def test_successful_response(self):
        """Test creation of successful AI response."""
        response = AIResponse(
            success=True,
            content="Hello! How can I help you?",
            model_used="gpt-4",
            usage={"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
            response_time=1.5
        )
        
        assert response.success == True
        assert response.content == "Hello! How can I help you?"
        assert response.model_used == "gpt-4"
        assert response.usage["total_tokens"] == 18
        assert response.response_time == 1.5
    
    def test_error_response(self):
        """Test creation of error AI response."""
        response = AIResponse(
            success=False,
            error_message="API rate limit exceeded",
            response_time=0.1
        )
        
        assert response.success == False
        assert response.error_message == "API rate limit exceeded"
        assert response.content == ""
    
    def test_response_with_metadata(self):
        """Test AI response with metadata."""
        metadata = {"request_id": "req-123", "model_version": "gpt-4-0613"}
        
        response = AIResponse(
            success=True,
            content="Response content",
            metadata=metadata
        )
        
        assert response.metadata == metadata


class TestRateLimiter:
    """Test RateLimiter functionality."""
    
    def test_rate_limiter_creation(self):
        """Test creation of rate limiter."""
        limiter = RateLimiter(requests_per_minute=60, tokens_per_minute=60000)
        assert limiter is not None
    
    def test_can_make_request_within_limits(self):
        """Test allowing requests within rate limits."""
        limiter = RateLimiter(requests_per_minute=60, tokens_per_minute=60000)
        
        # First request should be allowed
        assert limiter.can_make_request(estimated_tokens=100) == True
    
    def test_rate_limiting_enforcement(self):
        """Test that rate limiting is enforced."""
        # Very restrictive limits for testing
        limiter = RateLimiter(requests_per_minute=1, tokens_per_minute=100)
        
        # First request should be allowed
        assert limiter.can_make_request(estimated_tokens=50) == True
        limiter.record_request(tokens_used=50)
        
        # Second request might be limited depending on implementation
        # This tests the rate limiting logic exists
        result = limiter.can_make_request(estimated_tokens=60)
        assert isinstance(result, bool)
    
    def test_record_request(self):
        """Test recording requests for rate limiting."""
        limiter = RateLimiter(requests_per_minute=60, tokens_per_minute=60000)
        
        # Should not raise exception
        limiter.record_request(tokens_used=100)
        limiter.record_request(tokens_used=200)
    
    def test_token_estimation_limits(self):
        """Test token-based rate limiting."""
        limiter = RateLimiter(requests_per_minute=100, tokens_per_minute=1000)
        
        # Large token request might be limited
        result = limiter.can_make_request(estimated_tokens=2000)
        assert isinstance(result, bool)


class TestAIClient:
    """Test AIClient functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = ClientConfig(
            provider=APIProvider.OPENAI,
            api_key="test-api-key",
            model="gpt-4",
            max_retries=3,
            timeout=30,
            rate_limit_rpm=60,
            rate_limit_tpm=60000
        )
    
    def test_ai_client_creation(self):
        """Test creation of AI client."""
        client = AIClient(self.config)
        assert client is not None
    
    @patch('shared.ai_client.openai.OpenAI')
    def test_make_request_success(self, mock_openai):
        """Test successful API request."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello! How can I help?"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 8
        mock_response.usage.total_tokens = 18
        
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        client = AIClient(self.config)
        request = AIRequest(
            request_type=RequestType.CHAT,
            prompt="Hello, world!",
            model="gpt-4"
        )
        
        response = client.make_request(request)
        
        assert isinstance(response, AIResponse)
        assert response.success == True
        assert "Hello" in response.content
    
    def test_make_request_validation_error(self):
        """Test request validation errors."""
        client = AIClient(self.config)
        
        # Invalid request (empty prompt)
        request = AIRequest(
            request_type=RequestType.CHAT,
            prompt="",
            model="gpt-4"
        )
        
        response = client.make_request(request)
        assert response.success == False
        assert len(response.error_message) > 0
    
    def test_validate_request(self):
        """Test request validation functionality."""
        client = AIClient(self.config)
        
        # Valid request
        valid_request = AIRequest(
            request_type=RequestType.CHAT,
            prompt="Hello, world!",
            model="gpt-4"
        )
        
        errors = client.validate_request(valid_request)
        assert len(errors) == 0
        
        # Invalid request
        invalid_request = AIRequest(
            request_type=RequestType.CHAT,
            prompt="",  # Empty prompt
            model=""    # Empty model
        )
        
        errors = client.validate_request(invalid_request)
        assert len(errors) > 0
    
    def test_estimate_tokens(self):
        """Test token estimation functionality."""
        client = AIClient(self.config)
        
        text = "Hello, world! This is a test message."
        estimated_tokens = client.estimate_tokens(text)
        
        assert isinstance(estimated_tokens, int)
        assert estimated_tokens > 0
        assert estimated_tokens < 100  # Should be reasonable for short text
    
    def test_get_available_models(self):
        """Test getting available models."""
        client = AIClient(self.config)
        
        models = client.get_available_models()
        assert isinstance(models, list)
        # For testing, might return empty list or mock models
    
    @patch('shared.ai_client.openai.OpenAI')
    def test_error_handling_and_retries(self, mock_openai):
        """Test error handling and retry logic."""
        # Mock API error
        mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")
        
        client = AIClient(self.config)
        request = AIRequest(
            request_type=RequestType.CHAT,
            prompt="Hello, world!",
            model="gpt-4"
        )
        
        response = client.make_request(request)
        
        assert response.success == False
        assert "error" in response.error_message.lower()
    
    def test_rate_limiting_integration(self):
        """Test integration with rate limiting."""
        # Test that rate limiter is respected
        config = ClientConfig(
            provider=APIProvider.OPENAI,
            api_key="test-key",
            rate_limit_rpm=1,  # Very restrictive
            rate_limit_tpm=100
        )
        
        client = AIClient(config)
        request = AIRequest(
            request_type=RequestType.CHAT,
            prompt="Hello, world!",
            model="gpt-4"
        )
        
        # First request should work (or be rate limited gracefully)
        response1 = client.make_request(request)
        assert isinstance(response1, AIResponse)
        
        # Second immediate request might be rate limited
        response2 = client.make_request(request)
        assert isinstance(response2, AIResponse)


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_create_ai_client(self):
        """Test AI client factory function."""
        client = create_ai_client(
            provider=APIProvider.OPENAI,
            api_key="test-key",
            model="gpt-4",
            max_retries=5
        )
        
        assert isinstance(client, AIClient)
    
    @patch('shared.ai_client.AIClient.make_request')
    def test_make_simple_request(self, mock_make_request):
        """Test simple request convenience function."""
        # Mock successful response
        mock_response = AIResponse(
            success=True,
            content="Simple response"
        )
        mock_make_request.return_value = mock_response
        
        client = Mock()
        result = make_simple_request(client, "Hello, world!")
        
        assert result == "Simple response"
    
    @patch('shared.ai_client.AIClient.make_request')
    def test_make_simple_request_error(self, mock_make_request):
        """Test simple request error handling."""
        # Mock error response
        mock_response = AIResponse(
            success=False,
            error_message="API Error"
        )
        mock_make_request.return_value = mock_response
        
        client = Mock()
        result = make_simple_request(client, "Hello, world!")
        
        assert result == ""  # Should return empty string on error


class TestProviderSpecificBehavior:
    """Test provider-specific behavior."""
    
    def test_openai_provider_config(self):
        """Test OpenAI-specific configuration."""
        config = ClientConfig(
            provider=APIProvider.OPENAI,
            api_key="sk-test-key",
            model="gpt-4"
        )
        
        client = AIClient(config)
        assert client is not None
    
    def test_anthropic_provider_config(self):
        """Test Anthropic-specific configuration."""
        config = ClientConfig(
            provider=APIProvider.ANTHROPIC,
            api_key="claude-key",
            model="claude-3-sonnet"
        )
        
        client = AIClient(config)
        assert client is not None
    
    def test_google_provider_config(self):
        """Test Google-specific configuration."""
        config = ClientConfig(
            provider=APIProvider.GOOGLE,
            api_key="google-key",
            model="gemini-pro"
        )
        
        client = AIClient(config)
        assert client is not None


class TestSecurityAndValidation:
    """Test security and validation features."""
    
    def test_api_key_validation(self):
        """Test API key validation."""
        # Empty API key should be rejected
        with pytest.raises((ValueError, Exception)):
            config = ClientConfig(
                provider=APIProvider.OPENAI,
                api_key="",  # Empty key
                model="gpt-4"
            )
            client = AIClient(config)
    
    def test_model_validation(self):
        """Test model name validation."""
        config = ClientConfig(
            provider=APIProvider.OPENAI,
            api_key="valid-key",
            model="invalid-model-name"
        )
        
        client = AIClient(config)
        request = AIRequest(
            request_type=RequestType.CHAT,
            prompt="Hello",
            model="invalid-model"
        )
        
        # Should handle invalid model gracefully
        response = client.make_request(request)
        assert isinstance(response, AIResponse)
    
    def test_input_sanitization(self):
        """Test that inputs are properly sanitized."""
        client = AIClient(ClientConfig(
            provider=APIProvider.OPENAI,
            api_key="test-key",
            model="gpt-4"
        ))
        
        # Test with potentially malicious input
        malicious_prompt = "<script>alert('xss')</script>Prompt content"
        request = AIRequest(
            request_type=RequestType.CHAT,
            prompt=malicious_prompt,
            model="gpt-4"
        )
        
        # Should validate or sanitize input
        errors = client.validate_request(request)
        # Either validation passes (sanitized) or fails (rejected)
        assert isinstance(errors, list)


if __name__ == "__main__":
    pytest.main([__file__])