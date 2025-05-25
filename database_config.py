"""
Database configuration module with proper fallbacks and environment variable support.
Centralizes all database configuration and provides secure credential management.
"""

import os
import sys
from typing import Dict, Optional, Any

class DatabaseConfig:
    """Secure database configuration with environment variable fallbacks."""
    
    def __init__(self, streamlit_secrets=None):
        """Initialize database configuration.
        
        Args:
            streamlit_secrets: Optional streamlit secrets object for testing
        """
        self.streamlit_secrets = streamlit_secrets
        self._config_cache = {}
    
    def get_notion_config(self) -> Dict[str, str]:
        """Get Notion API configuration with secure fallbacks."""
        if 'notion' in self._config_cache:
            return self._config_cache['notion']
        
        config = {}
        
        # Try Streamlit secrets first
        if self.streamlit_secrets and hasattr(self.streamlit_secrets, 'notion'):
            config.update({
                'api_key': self.streamlit_secrets.notion.get('NOTION_API_KEY'),
                'client_database_id': self.streamlit_secrets.notion.get('NOTION_DATABASE_ID'),
                'content_samples_database_id': self.streamlit_secrets.notion.get('Content_Samples_database_ID'),
                'voice_guidelines_database_id': self.streamlit_secrets.notion.get('voice_guidelines_database_id')
            })
        
        # Fallback to environment variables
        config.update({
            'api_key': config.get('api_key') or os.getenv('NOTION_API_KEY'),
            'client_database_id': config.get('client_database_id') or os.getenv('NOTION_DATABASE_ID'),
            'content_samples_database_id': config.get('content_samples_database_id') or os.getenv('CONTENT_SAMPLES_DB_ID'),
            'voice_guidelines_database_id': config.get('voice_guidelines_database_id') or os.getenv('VOICE_GUIDELINES_DB_ID')
        })
        
        # Validate required fields
        if not config.get('api_key'):
            raise ValueError("NOTION_API_KEY is required but not found in environment variables or secrets")
        
        if not config.get('client_database_id'):
            raise ValueError("NOTION_DATABASE_ID is required but not found in environment variables or secrets")
        
        self._config_cache['notion'] = config
        return config
    
    def get_openai_config(self) -> Dict[str, str]:
        """Get OpenAI API configuration with secure fallbacks."""
        if 'openai' in self._config_cache:
            return self._config_cache['openai']
        
        config = {}
        
        # Try Streamlit secrets first
        if self.streamlit_secrets and hasattr(self.streamlit_secrets, 'openai'):
            config.update({
                'api_key': self.streamlit_secrets.openai.get('OPENAI_API_KEY'),
                'organization': self.streamlit_secrets.openai.get('OPENAI_ORG_ID')
            })
        
        # Fallback to environment variables
        config.update({
            'api_key': config.get('api_key') or os.getenv('OPENAI_API_KEY'),
            'organization': config.get('organization') or os.getenv('OPENAI_ORG_ID')
        })
        
        if not config.get('api_key'):
            raise ValueError("OPENAI_API_KEY is required but not found in environment variables or secrets")
        
        self._config_cache['openai'] = config
        return config
    
    def validate_configuration(self) -> bool:
        """Validate all required configuration is present."""
        try:
            notion_config = self.get_notion_config()
            openai_config = self.get_openai_config()
            
            # Check Notion configuration
            required_notion_fields = ['api_key', 'client_database_id']
            for field in required_notion_fields:
                if not notion_config.get(field):
                    print(f"❌ Missing required Notion configuration: {field}")
                    return False
            
            # Check OpenAI configuration
            if not openai_config.get('api_key'):
                print("❌ Missing required OpenAI API key")
                return False
            
            print("✅ All required configuration is present")
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {str(e)}")
            return False
    
    def get_mock_config_for_testing(self) -> Dict[str, Any]:
        """Get mock configuration for testing purposes."""
        return {
            'notion': {
                'api_key': 'mock_notion_api_key',
                'client_database_id': 'mock_client_db_id',
                'content_samples_database_id': 'mock_content_samples_db_id',
                'voice_guidelines_database_id': 'mock_voice_guidelines_db_id'
            },
            'openai': {
                'api_key': 'mock_openai_api_key',
                'organization': 'mock_openai_org_id'
            }
        }

# Global instance for easy import
default_config = DatabaseConfig()

def get_notion_client():
    """Get a configured Notion client instance."""
    try:
        import streamlit as st
        config = DatabaseConfig(st.secrets)
    except ImportError:
        config = DatabaseConfig()
    
    notion_config = config.get_notion_config()
    
    from notion_client import Client
    return Client(auth=notion_config['api_key'])

def get_database_ids():
    """Get all database IDs as a dictionary."""
    try:
        import streamlit as st
        config = DatabaseConfig(st.secrets)
    except ImportError:
        config = DatabaseConfig()
    
    notion_config = config.get_notion_config()
    return {
        'client_database_id': notion_config['client_database_id'],
        'content_samples_database_id': notion_config['content_samples_database_id'],
        'voice_guidelines_database_id': notion_config['voice_guidelines_database_id']
    }

# Direct exports for backward compatibility with existing Brand Builder steps
def _get_config_safely():
    """Get configuration safely with fallbacks."""
    try:
        import streamlit as st
        config = DatabaseConfig(st.secrets)
    except ImportError:
        config = DatabaseConfig()
    return config.get_notion_config()

# Export individual database IDs and API key for direct import
try:
    _config = _get_config_safely()
    VOICE_GUIDELINES_DB_ID = _config.get('voice_guidelines_database_id')
    CONTENT_SAMPLES_DB_ID = _config.get('content_samples_database_id') 
    CLIENT_DATABASE_ID = _config.get('client_database_id')
    NOTION_API_KEY = _config.get('api_key')
except Exception:
    # Fallback values for testing/development when secrets aren't available
    VOICE_GUIDELINES_DB_ID = "mock_voice_guidelines_db_id"
    CONTENT_SAMPLES_DB_ID = "mock_content_samples_db_id"
    CLIENT_DATABASE_ID = "mock_client_db_id"
    NOTION_API_KEY = "mock_notion_api_key"