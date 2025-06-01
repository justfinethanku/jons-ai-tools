"""
@RULE:TOOL_TYPE: social_copy_generator
@RULE:PURPOSE: Social media copy generation tool configuration
@RULE:MODEL_PREFERENCE: gemini-1.5-flash
@RULE:FALLBACK_MODEL: gpt-4
@RULE:TEMPERATURE: 0.7
@RULE:MAX_RETRIES: 3
@RULE:TOP_P: 0.9
@RULE:MAX_TOKENS: 2000
@RULE:TIMEOUT: 30
@RULE:RATE_LIMIT: 60
@RULE:CACHE_ENABLED: true
@RULE:LOG_LEVEL: info
@RULE:ERROR_HANDLING: retry_with_fallback
@RULE:VALIDATION_ENABLED: true
@RULE:METRICS_TRACKING: true
"""

# Tool Configuration for Social Copy Generator
# This file defines the centralized configuration rules for the social copy tool

TOOL_NAME = "social_copy_tool"
TOOL_DESCRIPTION = "AI-powered social media copy generation with platform-specific rules"
TOOL_VERSION = "2.0.0"

# API Configuration Rules
API_CONFIG = {
    "model_preference": "gemini-1.5-flash",
    "fallback_model": "gpt-4", 
    "temperature": 0.7,
    "max_retries": 3,
    "top_p": 0.9,
    "max_tokens": 2000,
    "timeout": 30,
    "rate_limit": 60
}

# UI Configuration Rules
UI_CONFIG = {
    "theme": "retro_gaming",
    "loading_animation": "glitch_effect",
    "success_messages": "random_humorous",
    "error_messages": "self_deprecating",
    "max_file_size": "10MB",
    "supported_file_types": ["txt", "md", "docx", "pdf"]
}

# Behavior Configuration Rules
BEHAVIOR_CONFIG = {
    "cache_enabled": True,
    "log_level": "info",
    "error_handling": "retry_with_fallback",
    "validation_enabled": True,
    "metrics_tracking": True,
    "auto_save_outputs": False,
    "legacy_addon_support": True
}

# Platform-specific Rules (extracted from platform prompt files)
PLATFORM_RULES = {
    "facebook": {
        "character_limit": 8000,
        "hashtag_count": {"min": 3, "max": 5},
        "emoji_allowed": True,
        "required_cta": True
    },
    "linkedin": {
        "character_limit": 3000,
        "tone_style": "professional",
        "hashtag_count": {"min": 3, "max": 5},
        "emoji_allowed": False
    },
    "tiktok": {
        "character_limit": 2200,
        "hashtag_count": {"min": 3, "max": 5},
        "emoji_allowed": True,
        "engagement_rules": "no_follow_for_follow"
    },
    "youtube": {
        "character_limit": 5000,
        "hashtag_count": {"min": 3, "max": 5},
        "emoji_allowed": True,
        "required_cta": True
    }
}