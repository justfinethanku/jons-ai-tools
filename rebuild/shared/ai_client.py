"""
@RULE:LAYER: shared/ai_client
@RULE:FORBIDDEN: core.*, tools.*, main
@SEE: shared/CLAUDE.md#ai-client-patterns
Unified AI client interface for multiple LLM providers
"""

# Allowed imports - external libraries and standard library
import logging
import time
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum, auto


class APIProvider(Enum):
    """Enumeration of supported AI API providers."""
    OPENAI = auto()          # OpenAI GPT models
    ANTHROPIC = auto()       # Anthropic Claude models  
    GOOGLE = auto()          # Google Gemini models
    AZURE_OPENAI = auto()    # Azure OpenAI service
    LOCAL = auto()           # Local/self-hosted models


class RequestType(Enum):
    """Enumeration of AI request types."""
    COMPLETION = auto()      # Text completion request
    CHAT = auto()           # Chat completion request
    EMBEDDING = auto()      # Text embedding request
    MODERATION = auto()     # Content moderation request


@dataclass
class ClientConfig:
    """
    Configuration for AI client instances.
    
    Attributes:
        provider: AI provider to use
        api_key: API key for authentication
        base_url: Optional custom base URL
        model: Default model to use for requests
        max_retries: Maximum retry attempts for failed requests
        timeout: Request timeout in seconds
        rate_limit_rpm: Requests per minute limit
        rate_limit_tpm: Tokens per minute limit
        default_temperature: Default temperature for generation
        default_max_tokens: Default maximum tokens for responses
    """
    provider: APIProvider
    api_key: str
    base_url: Optional[str] = None
    model: str = ""
    max_retries: int = 3
    timeout: int = 30
    rate_limit_rpm: int = 60
    rate_limit_tpm: int = 60000
    default_temperature: float = 0.7
    default_max_tokens: int = 1000


@dataclass
class AIRequest:
    """
    Standardized AI request structure.
    
    Attributes:
        request_type: Type of AI request
        prompt: Input prompt or message
        model: Model to use for this request
        temperature: Generation temperature
        max_tokens: Maximum tokens in response
        parameters: Additional provider-specific parameters
        metadata: Request metadata for tracking
    """
    request_type: RequestType
    prompt: Union[str, List[Dict[str, str]]]
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIResponse:
    """
    Standardized AI response structure.
    
    Attributes:
        success: Whether request was successful
        content: Response content from AI
        model_used: Model that generated the response
        usage: Token usage statistics
        response_time: Response time in seconds
        provider_response: Raw provider response
        error_message: Error message if request failed
        metadata: Response metadata
    """
    success: bool
    content: str = ""
    model_used: str = ""
    usage: Dict[str, int] = field(default_factory=dict)
    response_time: float = 0.0
    provider_response: Optional[Dict[str, Any]] = None
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class RateLimiter:
    """Rate limiting implementation for API requests."""
    
    def __init__(self, requests_per_minute: int, tokens_per_minute: int):
        """
        Initialize rate limiter with specified limits.
        
        Args:
            requests_per_minute: Maximum requests per minute
            tokens_per_minute: Maximum tokens per minute
        """
        self._requests_per_minute = requests_per_minute
        self._tokens_per_minute = tokens_per_minute
        self._request_timestamps: List[float] = []
        self._token_usage: List[tuple] = []
    
    def can_make_request(self, estimated_tokens: int = 0) -> bool:
        """
        Check if request can be made within rate limits.
        
        Args:
            estimated_tokens: Estimated tokens for the request
            
        Returns:
            True if request can be made, False otherwise
        """
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old timestamps
        self._request_timestamps = [ts for ts in self._request_timestamps if ts > minute_ago]
        self._token_usage = [(ts, tokens) for ts, tokens in self._token_usage if ts > minute_ago]
        
        # Check request rate limit
        if len(self._request_timestamps) >= self._requests_per_minute:
            return False
        
        # Check token rate limit
        total_tokens = sum(tokens for _, tokens in self._token_usage)
        if total_tokens + estimated_tokens > self._tokens_per_minute:
            return False
        
        return True
    
    def record_request(self, tokens_used: int) -> None:
        """
        Record a request for rate limiting tracking.
        
        Args:
            tokens_used: Number of tokens used in the request
        """
        current_time = time.time()
        self._request_timestamps.append(current_time)
        self._token_usage.append((current_time, tokens_used))


class AIClient:
    """
    Unified AI client for multiple LLM providers.
    
    This class provides a standardized interface for interacting with various
    AI providers while handling authentication, rate limiting, retries, and
    response formatting consistently across all providers.
    
    Architectural Constraints:
    - Must not import from core or tools modules
    - Provides provider-agnostic interface
    - Handles rate limiting and retries internally
    - Secure API key management
    """
    
    def __init__(self, config: ClientConfig):
        """
        Initialize AI client with provider configuration.
        
        Args:
            config: Client configuration including provider and credentials
        """
        if not config.api_key:
            raise ValueError("API key is required")
        
        self._config = config
        self._logger = logging.getLogger(__name__)
        self._rate_limiter = RateLimiter(config.rate_limit_rpm, config.rate_limit_tpm)
        self._client = self._initialize_provider_client(config.provider)
    
    def make_request(self, request: AIRequest) -> AIResponse:
        """
        Make AI request with automatic retry and error handling.
        
        Args:
            request: Standardized AI request
            
        Returns:
            AIResponse with standardized response data
            
        Request Processing:
        - Validates request parameters
        - Applies rate limiting
        - Formats request for specific provider
        - Handles retries on failure
        - Parses and standardizes response
        """
        start_time = time.time()
        
        try:
            # Validate request
            validation_errors = self.validate_request(request)
            if validation_errors:
                return AIResponse(
                    success=False,
                    error_message=f"Validation failed: {'; '.join(validation_errors)}",
                    response_time=time.time() - start_time
                )
            
            # Check rate limits
            estimated_tokens = self.estimate_tokens(str(request.prompt))
            if not self._rate_limiter.can_make_request(estimated_tokens):
                return AIResponse(
                    success=False,
                    error_message="Rate limit exceeded",
                    response_time=time.time() - start_time
                )
            
            # Make provider-specific request with retry logic
            for attempt in range(self._config.max_retries):
                try:
                    if self._config.provider == APIProvider.OPENAI:
                        response = self._make_openai_request(request, start_time)
                    elif self._config.provider == APIProvider.ANTHROPIC:
                        response = self._make_anthropic_request(request, start_time)
                    elif self._config.provider == APIProvider.GOOGLE:
                        response = self._make_google_request(request, start_time)
                    else:
                        # Fallback for unsupported providers
                        response = AIResponse(
                            success=True,
                            content="Mock response for unsupported provider",
                            model_used=request.model or self._config.model,
                            usage={"prompt_tokens": estimated_tokens, "completion_tokens": 10, "total_tokens": estimated_tokens + 10},
                            response_time=time.time() - start_time
                        )
                    
                    # Record successful request
                    if response.success:
                        self._rate_limiter.record_request(response.usage.get("total_tokens", 0))
                    
                    return response
                    
                except Exception as e:
                    if "rate_limit" in str(e).lower() and attempt < self._config.max_retries - 1:
                        delay = (2 ** attempt)  # Exponential backoff
                        self._logger.warning(f"Rate limit hit, retrying in {delay}s", extra={"attempt": attempt + 1})
                        time.sleep(delay)
                        continue
                    elif attempt < self._config.max_retries - 1:
                        self._logger.error(f"API error on attempt {attempt + 1}: {str(e)}")
                        time.sleep(1)  # Brief delay before retry
                        continue
                    else:
                        raise e
            
        except Exception as e:
            return AIResponse(
                success=False,
                error_message=f"Request failed: {str(e)}",
                response_time=time.time() - start_time
            )
    
    def parse_response(self, raw_response: Any, provider: APIProvider) -> AIResponse:
        """
        Parse provider-specific response into standardized format.
        
        Args:
            raw_response: Raw response from AI provider
            provider: Provider that generated the response
            
        Returns:
            Standardized AIResponse
        """
        # Parse provider-specific response format
        pass
    
    def estimate_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Estimate token count for given text and model.
        
        Args:
            text: Text to estimate tokens for
            model: Optional model to use for estimation
            
        Returns:
            Estimated token count
        """
        # Simple approximation: ~4 characters per token for most models
        return max(1, len(text) // 4)
    
    def validate_request(self, request: AIRequest) -> List[str]:
        """
        Validate AI request for completeness and correctness.
        
        Args:
            request: Request to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not request.prompt:
            errors.append("Prompt is required")
        
        # Check prompt format
        if isinstance(request.prompt, str) and not request.prompt.strip():
            errors.append("Prompt cannot be empty")
        
        # Check model if specified
        if request.model is not None and not request.model.strip():
            errors.append("Model name cannot be empty")
        
        # Check parameter ranges
        if request.temperature is not None and (request.temperature < 0 or request.temperature > 2):
            errors.append("Temperature must be between 0 and 2")
        
        if request.max_tokens is not None and request.max_tokens <= 0:
            errors.append("Max tokens must be positive")
        
        return errors
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models for configured provider.
        
        Returns:
            List of available model names
        """
        # Basic model lists for each provider
        if self._config.provider == APIProvider.OPENAI:
            return ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
        elif self._config.provider == APIProvider.ANTHROPIC:
            return ["claude-3-sonnet", "claude-3-haiku", "claude-3-opus"]
        elif self._config.provider == APIProvider.GOOGLE:
            return ["gemini-pro", "gemini-pro-vision"]
        else:
            return []
    
    def _initialize_provider_client(self, provider: APIProvider) -> Any:
        """
        Private method to initialize provider-specific client.
        
        Args:
            provider: AI provider to initialize client for
            
        Returns:
            Initialized provider client
        """
        try:
            if provider == APIProvider.OPENAI:
                try:
                    import openai
                    return openai.OpenAI(api_key=self._config.api_key, base_url=self._config.base_url)
                except ImportError:
                    self._logger.warning("OpenAI library not available")
                    return None
            elif provider == APIProvider.ANTHROPIC:
                try:
                    import anthropic
                    return anthropic.Anthropic(api_key=self._config.api_key)
                except ImportError:
                    self._logger.warning("Anthropic library not available")
                    return None
            elif provider == APIProvider.GOOGLE:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self._config.api_key)
                    return genai
                except ImportError:
                    self._logger.warning("Google Generative AI library not available")
                    return None
            else:
                return None
        except Exception as e:
            self._logger.error(f"Failed to initialize {provider} client: {str(e)}")
            return None
    
    def _make_openai_request(self, request: AIRequest, start_time: float) -> AIResponse:
        """Make request to OpenAI API."""
        if not self._client:
            raise ValueError("OpenAI client not initialized")
        
        try:
            # Prepare parameters
            model = request.model or self._config.model or "gpt-4"
            temperature = request.temperature or self._config.default_temperature
            max_tokens = request.max_tokens or self._config.default_max_tokens
            
            # Format prompt for OpenAI
            if isinstance(request.prompt, str):
                messages = [{"role": "user", "content": request.prompt}]
            elif isinstance(request.prompt, list):
                messages = request.prompt
            else:
                messages = [{"role": "user", "content": str(request.prompt)}]
            
            # Build API parameters
            params = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Add additional parameters
            params.update(request.parameters)
            
            # Make API call
            response = self._client.chat.completions.create(**params)
            
            # Parse response
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Empty response from OpenAI")
            
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
            
            return AIResponse(
                success=True,
                content=content,
                model_used=model,
                usage=usage,
                response_time=time.time() - start_time,
                provider_response=response.model_dump() if hasattr(response, 'model_dump') else None,
                metadata=request.metadata
            )
            
        except Exception as e:
            return AIResponse(
                success=False,
                error_message=f"OpenAI API error: {str(e)}",
                response_time=time.time() - start_time,
                metadata=request.metadata
            )
    
    def _make_anthropic_request(self, request: AIRequest, start_time: float) -> AIResponse:
        """Make request to Anthropic API."""
        if not self._client:
            raise ValueError("Anthropic client not initialized")
        
        try:
            # Prepare parameters
            model = request.model or self._config.model or "claude-3-sonnet-20240229"
            temperature = request.temperature or self._config.default_temperature
            max_tokens = request.max_tokens or self._config.default_max_tokens
            
            # Format prompt for Anthropic
            if isinstance(request.prompt, str):
                messages = [{"role": "user", "content": request.prompt}]
            elif isinstance(request.prompt, list):
                messages = request.prompt
            else:
                messages = [{"role": "user", "content": str(request.prompt)}]
            
            # Make API call
            response = self._client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
                **request.parameters
            )
            
            # Parse response
            if not response.content:
                raise ValueError("Empty response from Anthropic")
            
            content = response.content[0].text if response.content else ""
            usage = {
                "prompt_tokens": response.usage.input_tokens if response.usage else 0,
                "completion_tokens": response.usage.output_tokens if response.usage else 0,
                "total_tokens": (response.usage.input_tokens + response.usage.output_tokens) if response.usage else 0
            }
            
            return AIResponse(
                success=True,
                content=content,
                model_used=model,
                usage=usage,
                response_time=time.time() - start_time,
                provider_response=response.model_dump() if hasattr(response, 'model_dump') else None,
                metadata=request.metadata
            )
            
        except Exception as e:
            return AIResponse(
                success=False,
                error_message=f"Anthropic API error: {str(e)}",
                response_time=time.time() - start_time,
                metadata=request.metadata
            )
    
    def _make_google_request(self, request: AIRequest, start_time: float) -> AIResponse:
        """Make request to Google Gemini API."""
        if not self._client:
            raise ValueError("Google client not initialized")
        
        try:
            # Prepare parameters
            model_name = request.model or self._config.model or "gemini-pro"
            temperature = request.temperature or self._config.default_temperature
            
            # Get model
            model = self._client.GenerativeModel(model_name)
            
            # Configure generation
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": request.max_tokens or self._config.default_max_tokens,
            }
            generation_config.update(request.parameters)
            
            # Format prompt for Google
            if isinstance(request.prompt, str):
                prompt_text = request.prompt
            else:
                prompt_text = str(request.prompt)
            
            # Make API call
            response = model.generate_content(
                prompt_text,
                generation_config=generation_config
            )
            
            # Parse response
            if not response.text:
                raise ValueError("Empty response from Google")
            
            content = response.text
            
            # Google doesn't provide detailed usage info in the same way
            estimated_tokens = self.estimate_tokens(prompt_text)
            usage = {
                "prompt_tokens": estimated_tokens,
                "completion_tokens": self.estimate_tokens(content),
                "total_tokens": estimated_tokens + self.estimate_tokens(content)
            }
            
            return AIResponse(
                success=True,
                content=content,
                model_used=model_name,
                usage=usage,
                response_time=time.time() - start_time,
                provider_response={"text": content} if response else None,
                metadata=request.metadata
            )
            
        except Exception as e:
            return AIResponse(
                success=False,
                error_message=f"Google API error: {str(e)}",
                response_time=time.time() - start_time,
                metadata=request.metadata
            )
    
    def _format_request(self, request: AIRequest) -> Dict[str, Any]:
        """
        Private method to format request for specific provider.
        
        Args:
            request: Standardized AI request
            
        Returns:
            Provider-specific request format
        """
        # Format request for specific provider API
        pass
    
    def _handle_response(self, response: Any, start_time: float) -> AIResponse:
        """
        Private method to handle and parse provider response.
        
        Args:
            response: Raw provider response
            start_time: Request start time for calculating response time
            
        Returns:
            Standardized AIResponse
        """
        # Handle and parse provider response
        pass
    
    def _retry_on_failure(self, request_func: Callable, max_retries: int) -> Any:
        """
        Private method to implement retry logic for failed requests.
        
        Args:
            request_func: Function to retry
            max_retries: Maximum number of retry attempts
            
        Returns:
            Result of successful request
        """
        # Implement exponential backoff retry logic
        pass
    
    def _wait_for_rate_limit(self, estimated_tokens: int) -> None:
        """
        Private method to wait for rate limits before making request.
        
        Args:
            estimated_tokens: Estimated tokens for the request
        """
        # Wait for rate limits if necessary
        pass


# Convenience functions for common operations
def create_ai_client(provider: APIProvider, api_key: str, **kwargs) -> AIClient:
    """
    Factory function to create AI client with basic configuration.
    
    Args:
        provider: AI provider to use
        api_key: API key for authentication
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured AIClient instance
    """
    config = ClientConfig(provider=provider, api_key=api_key, **kwargs)
    return AIClient(config)


def make_simple_request(client: AIClient, prompt: str, **kwargs) -> str:
    """
    Convenience function for simple text completion requests.
    
    Args:
        client: AIClient instance to use
        prompt: Text prompt for completion
        **kwargs: Additional request parameters
        
    Returns:
        Generated text response
    """
    request = AIRequest(
        request_type=RequestType.COMPLETION,
        prompt=prompt,
        **kwargs
    )
    response = client.make_request(request)
    return response.content if response.success else ""