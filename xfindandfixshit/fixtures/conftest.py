"""
Test fixtures and configuration for pytest.
Provides mocks for external dependencies like Notion API, OpenAI, and Streamlit.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Mock Streamlit before importing our modules
@pytest.fixture(autouse=True)
def mock_streamlit():
    """Auto-use fixture to mock Streamlit in all tests"""
    mock_st = MagicMock()
    
    # Mock secrets
    mock_st.secrets = {
        "notion": {
            "NOTION_API_KEY": "test_api_key",
            "NOTION_DATABASE_ID": "test_db_id", 
            "Content_Samples_database_ID": "test_content_samples_db_id",
            "voice_guidelines_database_id": "test_voice_guidelines_db_id"
        },
        "openai": {
            "API_KEY": "test_openai_key"
        },
        "google": {
            "GEMINI_API_KEY": "test_gemini_key"
        }
    }
    
    # Mock session state
    mock_st.session_state = {}
    
    # Mock common Streamlit functions
    mock_st.error = Mock()
    mock_st.warning = Mock()
    mock_st.success = Mock()
    mock_st.info = Mock()
    mock_st.sidebar = Mock()
    mock_st.columns = Mock(return_value=[Mock(), Mock()])
    mock_st.button = Mock(return_value=False)
    mock_st.selectbox = Mock(return_value="None")
    mock_st.expander = Mock()
    mock_st.rerun = Mock()
    mock_st.download_button = Mock()
    mock_st.set_page_config = Mock()
    mock_st.cache_resource = lambda func: func
    
    with patch('streamlit', mock_st):
        yield mock_st

@pytest.fixture
def mock_notion_client():
    """Mock Notion client with typical API responses"""
    mock_client = Mock()
    
    # Mock database query response
    mock_client.databases.query.return_value = {
        "results": [
            {
                "id": "test_page_id_1",
                "properties": {
                    "Name": {"title": [{"text": {"content": "Test Client 1"}, "plain_text": "Test Client 1"}]},
                    "Brand Voice": {"rich_text": [{"plain_text": "Professional and friendly"}]},
                    "Tone": {"select": {"name": "Professional"}},
                    "Industry": {"select": {"name": "Technology"}},
                    "Target Audience": {"rich_text": [{"plain_text": "Tech professionals"}]},
                    "Keywords": {"multi_select": [{"name": "innovation"}, {"name": "technology"}]}
                },
                "created_time": "2024-01-01T00:00:00.000Z",
                "last_edited_time": "2024-01-01T00:00:00.000Z"
            }
        ]
    }
    
    # Mock page creation response
    mock_client.pages.create.return_value = {
        "id": "new_page_id",
        "url": "https://notion.so/new_page_id"
    }
    
    # Mock page retrieval
    mock_client.pages.retrieve.return_value = {
        "id": "test_page_id",
        "properties": {}
    }
    
    return mock_client

@pytest.fixture
def sample_client_data():
    """Sample client data for testing"""
    return {
        "id": "test_client_id",
        "name": "Test Client",
        "brand_voice": "Professional and friendly", 
        "tone": "Professional",
        "industry": "Technology",
        "target_audience": "Tech professionals",
        "keywords": ["innovation", "technology"],
        "custom_prompts": "Focus on innovation",
        "created_time": "2024-01-01T00:00:00.000Z",
        "last_edited_time": "2024-01-01T00:00:00.000Z"
    }

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test OpenAI response"
    return mock_response

@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response"""
    mock_response = Mock()
    mock_response.text = "Test Gemini response"
    mock_response.candidates = [Mock()]
    mock_response.candidates[0].content.parts = [Mock()]
    mock_response.candidates[0].content.parts[0].text = '{"structured": "response"}'
    return mock_response

@pytest.fixture
def sample_website_data():
    """Sample website extraction data"""
    return {
        "company_name": "Test Company",
        "industry": "Technology",
        "website_url": "https://test.com",
        "homepage_content": "Welcome to Test Company...",
        "about_content": "About us content...",
        "services_content": "Our services include...",
        "mission_statement": "To innovate and lead",
        "value_propositions": ["Innovation", "Quality", "Service"]
    }

@pytest.fixture
def sample_content_samples():
    """Sample content samples for testing"""
    return [
        {
            "channel_type": "Website Homepage",
            "content": "Welcome to our innovative platform...",
            "tone_assessment": "Professional",
            "is_original": True
        },
        {
            "channel_type": "Social Media",
            "content": "Check out our latest features! 🚀",
            "tone_assessment": "Casual",
            "is_original": True
        }
    ]

@pytest.fixture
def sample_voice_analysis():
    """Sample voice analysis data"""
    return {
        "word_choice_analysis": "Uses technical terms appropriately...",
        "tone_analysis": "Maintains professional yet approachable tone...",
        "personality_analysis": "Confident and expert...",
        "consistency_assessment": "High consistency across channels...",
        "audience_fit_assessment": "Well-aligned with target audience..."
    }

@pytest.fixture
def database_error_mock():
    """Mock that simulates database connection errors"""
    def error_side_effect(*args, **kwargs):
        raise Exception("Database connection failed")
    return error_side_effect