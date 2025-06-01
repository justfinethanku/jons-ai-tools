"""
@RULE:PURPOSE: Centralized API configuration management with rule-based parameter control
@RULE:DEPENDENCIES: shared_utils, logging_manager
@RULE:INTERFACE: get_api_config, validate_api_params, apply_api_rules
@RULE:NO_CROSS_TALK: tool-specific implementations
"""

from typing import Dict, Any, Optional, Tuple
from frameworks.shared_utils import extract_string_rules
from frameworks.logging_manager import get_logger

logger = get_logger("api_config")

# Default API configurations with rules
DEFAULT_API_RULES = {
    "openai": {
        "DEFAULT_MODEL": "gpt-4.1-2025-04-14",
        "DEFAULT_TEMPERATURE": 1.0,
        "MAX_RETRIES": 3,
        "RETRY_DELAY_BASE": 1,
        "TIMEOUT_SECONDS": 120,
        "MAX_TOKENS": 4096
    },
    "gemini": {
        "DEFAULT_MODEL": "gemini-2.5-pro-preview-05-06", 
        "DEFAULT_TEMPERATURE": 0.2,
        "MAX_RETRIES": 3,
        "RETRY_DELAY_BASE": 2,
        "TIMEOUT_SECONDS": 120,
        "TOP_P": 0.95,
        "TOP_K": 40,
        "MAX_OUTPUT_TOKENS": 4096
    }
}

def extract_api_rules_from_context(context_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Extract API-specific rules from context (e.g., from prompt rules).
    
    Args:
        context_rules: Dictionary of rules from calling context
        
    Returns:
        Dictionary of API configuration overrides
    """
    api_overrides = {}
    
    if not context_rules:
        return api_overrides
    
    # Map context rules to API parameters
    rule_mapping = {
        'MODEL_PREFERENCE': 'model',
        'TEMPERATURE': 'temperature', 
        'FALLBACK_MODEL': 'fallback_model',
        'MAX_RETRIES': 'max_retries',
        'TIMEOUT': 'timeout_seconds',
        'TOP_P': 'top_p',
        'TOP_K': 'top_k',
        'MAX_TOKENS': 'max_tokens'
    }
    
    for rule_key, api_param in rule_mapping.items():
        if rule_key in context_rules:
            api_overrides[api_param] = context_rules[rule_key]
            logger.debug(f"API override: {api_param} = {context_rules[rule_key]}")
    
    return api_overrides

def get_api_config(provider: str, context_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get API configuration with rule-based overrides.
    
    Args:
        provider: API provider ('openai' or 'gemini')
        context_rules: Optional rules from calling context (e.g., prompt rules)
        
    Returns:
        Complete API configuration dictionary
    """
    if provider not in DEFAULT_API_RULES:
        raise ValueError(f"Unknown API provider: {provider}")
    
    # Start with defaults
    config = DEFAULT_API_RULES[provider].copy()
    
    # Apply context-based overrides
    if context_rules:
        overrides = extract_api_rules_from_context(context_rules)
        config.update(overrides)
        
        logger.log_operation_start("api_config_override", 
                                 provider=provider, 
                                 overrides_count=len(overrides))
    
    return config

def validate_api_params(provider: str, **params) -> Tuple[bool, str]:
    """
    Validate API parameters against provider requirements.
    
    Args:
        provider: API provider name
        **params: Parameters to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if provider == "openai":
            if 'temperature' in params:
                temp = params['temperature']
                if not 0 <= temp <= 2:
                    return False, f"Temperature {temp} out of range [0, 2]"
            
            if 'max_tokens' in params:
                max_tokens = params['max_tokens']
                if max_tokens <= 0 or max_tokens > 100000:
                    return False, f"Max tokens {max_tokens} out of valid range"
                    
        elif provider == "gemini":
            if 'temperature' in params:
                temp = params['temperature']
                if not 0 <= temp <= 2:
                    return False, f"Temperature {temp} out of range [0, 2]"
                    
            if 'top_p' in params:
                top_p = params['top_p']
                if not 0 <= top_p <= 1:
                    return False, f"Top_p {top_p} out of range [0, 1]"
                    
            if 'top_k' in params:
                top_k = params['top_k']
                if top_k <= 0:
                    return False, f"Top_k {top_k} must be positive"
        
        return True, ""
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def apply_retry_rules(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply retry-related rules from configuration.
    
    Args:
        config: API configuration dictionary
        
    Returns:
        Retry configuration parameters
    """
    return {
        'max_retries': config.get('MAX_RETRIES', 3),
        'base_delay': config.get('RETRY_DELAY_BASE', 1),
        'timeout': config.get('TIMEOUT_SECONDS', 120)
    }

def get_model_selection_rules(context_rules: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    Get model selection preferences from rules.
    
    Args:
        context_rules: Rules from calling context
        
    Returns:
        Dictionary with primary and fallback model preferences
    """
    if not context_rules:
        return {
            'primary_model': DEFAULT_API_RULES['gemini']['DEFAULT_MODEL'],
            'fallback_model': DEFAULT_API_RULES['openai']['DEFAULT_MODEL']
        }
    
    primary = context_rules.get('MODEL_PREFERENCE', DEFAULT_API_RULES['gemini']['DEFAULT_MODEL'])
    fallback = context_rules.get('FALLBACK_MODEL', DEFAULT_API_RULES['openai']['DEFAULT_MODEL'])
    
    return {
        'primary_model': primary,
        'fallback_model': fallback
    }

def log_api_configuration(provider: str, config: Dict[str, Any], context_source: str = "default"):
    """
    Log API configuration for debugging and monitoring.
    
    Args:
        provider: API provider name
        config: Applied configuration
        context_source: Source of configuration (e.g., "prompt_rules", "default")
    """
    logger.info("API configuration applied",
                provider=provider,
                config_source=context_source,
                model=config.get('model', config.get('DEFAULT_MODEL')),
                temperature=config.get('temperature', config.get('DEFAULT_TEMPERATURE')),
                max_retries=config.get('max_retries', config.get('MAX_RETRIES')))