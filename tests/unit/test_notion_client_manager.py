"""
Unit tests for notion_client_manager.py
Tests Notion client functionality with mocked responses.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from notion_client_manager import NotionClientManager

class TestNotionClientManagerInitialization:
    """Test NotionClientManager initialization"""
    
    def test_initialization_success(self):
        """Test successful initialization with mocked secrets"""
        manager = NotionClientManager()
        
        assert manager.notion is not None
        assert manager.database_id == "test_db_id"
        
    @patch('notion_client_manager.st.secrets', side_effect=KeyError("notion"))
    @patch.dict('os.environ', {'NOTION_API_KEY': 'env_key', 'NOTION_DATABASE_ID': 'env_db'})
    def test_initialization_fallback_to_env(self, mock_secrets):
        """Test initialization falls back to environment variables"""
        manager = NotionClientManager()
        
        # Should still initialize notion client from env vars
        assert manager.database_id == 'env_db'
        
    @patch('notion_client_manager.st.secrets', side_effect=KeyError("notion"))
    @patch.dict('os.environ', {}, clear=True)
    def test_initialization_no_credentials(self, mock_secrets):
        """Test initialization with no credentials"""
        manager = NotionClientManager()
        
        assert manager.notion is None
        assert manager.database_id is None

class TestClientRetrieval:
    """Test client data retrieval from Notion"""
    
    def test_get_clients_success(self, mock_notion_client):
        """Test successful client retrieval"""
        with patch('notion_client_manager.Client', return_value=mock_notion_client):
            manager = NotionClientManager()
            clients = manager.get_clients()
            
            assert len(clients) == 1
            assert clients[0]["name"] == "Test Client 1"
            assert clients[0]["brand_voice"] == "Professional and friendly"
            assert clients[0]["industry"] == "Technology"
            
    def test_get_clients_no_connection(self):
        """Test client retrieval with no Notion connection"""
        with patch('notion_client_manager.st.secrets', side_effect=KeyError("notion")):
            manager = NotionClientManager()
            clients = manager.get_clients()
            
            assert clients == []
            
    def test_get_clients_api_error(self, mock_notion_client):
        """Test client retrieval with API error"""
        mock_notion_client.databases.query.side_effect = Exception("API Error")
        
        with patch('notion_client_manager.Client', return_value=mock_notion_client):
            manager = NotionClientManager()
            clients = manager.get_clients()
            
            assert clients == []

class TestClientFormatting:
    """Test client data formatting"""
    
    def test_format_client_complete_data(self):
        """Test formatting client with complete data"""
        manager = NotionClientManager()
        
        page_data = {
            "id": "test_id",
            "properties": {
                "Name": {"title": [{"plain_text": "Test Client"}]},
                "Brand Voice": {"rich_text": [{"plain_text": "Professional"}]},
                "Tone": {"select": {"name": "Friendly"}},
                "Industry": {"select": {"name": "Tech"}},
                "Target Audience": {"rich_text": [{"plain_text": "Developers"}]},
                "Keywords": {"multi_select": [{"name": "innovation"}]},
                "Custom Prompts": {"rich_text": [{"plain_text": "Focus on quality"}]}
            },
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z"
        }
        
        client = manager._format_client(page_data)
        
        assert client["id"] == "test_id"
        assert client["name"] == "Test Client"
        assert client["brand_voice"] == "Professional"
        assert client["tone"] == "Friendly"
        assert client["industry"] == "Tech"
        assert client["target_audience"] == "Developers"
        assert client["keywords"] == ["innovation"]
        assert client["custom_prompts"] == "Focus on quality"
        
    def test_format_client_missing_data(self):
        """Test formatting client with missing data"""
        manager = NotionClientManager()
        
        page_data = {
            "id": "test_id",
            "properties": {
                "Name": {"title": [{"plain_text": "Test Client"}]}
            },
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z"
        }
        
        client = manager._format_client(page_data)
        
        assert client["id"] == "test_id"
        assert client["name"] == "Test Client"
        assert client["brand_voice"] == ""
        assert client["tone"] == ""
        assert client["industry"] == ""
        assert client["keywords"] == []
        
    def test_format_client_error(self):
        """Test formatting client with malformed data"""
        manager = NotionClientManager()
        
        # Malformed page data
        page_data = {"invalid": "data"}
        
        client = manager._format_client(page_data)
        
        assert client is None

class TestPropertyExtraction:
    """Test Notion property extraction methods"""
    
    def test_extract_title_success(self):
        """Test successful title extraction"""
        manager = NotionClientManager()
        
        prop = {"title": [{"plain_text": "Test Title"}]}
        result = manager._extract_title(prop)
        
        assert result == "Test Title"
        
    def test_extract_title_empty(self):
        """Test title extraction with empty property"""
        manager = NotionClientManager()
        
        prop = {"title": []}
        result = manager._extract_title(prop)
        
        assert result == ""
        
    def test_extract_rich_text_multiple(self):
        """Test rich text extraction with multiple elements"""
        manager = NotionClientManager()
        
        prop = {"rich_text": [
            {"plain_text": "First "},
            {"plain_text": "Second"}
        ]}
        result = manager._extract_rich_text(prop)
        
        assert result == "First  Second"
        
    def test_extract_select_success(self):
        """Test select property extraction"""
        manager = NotionClientManager()
        
        prop = {"select": {"name": "Option A"}}
        result = manager._extract_select(prop)
        
        assert result == "Option A"
        
    def test_extract_multi_select_success(self):
        """Test multi-select property extraction"""
        manager = NotionClientManager()
        
        prop = {"multi_select": [
            {"name": "Tag 1"},
            {"name": "Tag 2"}
        ]}
        result = manager._extract_multi_select(prop)
        
        assert result == ["Tag 1", "Tag 2"]

class TestConnectionStatus:
    """Test connection status checks"""
    
    def test_is_connected_true(self):
        """Test connection status when properly connected"""
        manager = NotionClientManager()
        
        assert manager.is_connected() is True
        
    def test_is_connected_false_no_client(self):
        """Test connection status with no client"""
        with patch('notion_client_manager.st.secrets', side_effect=KeyError("notion")):
            manager = NotionClientManager()
            
            assert manager.is_connected() is False
            
    def test_is_connected_false_no_database_id(self):
        """Test connection status with client but no database ID"""
        # Create a manager and manually remove database_id
        manager = NotionClientManager()
        manager.database_id = None
        
        assert manager.is_connected() is False

@pytest.mark.unit 
class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_save_generated_content_no_connection(self):
        """Test saving content with no connection"""
        with patch('notion_client_manager.st.secrets', side_effect=KeyError("notion")):
            manager = NotionClientManager()
            
            # Should not raise exception
            manager.save_generated_content("client_id", "content_type", "content")
            
    def test_get_clients_empty_response(self, mock_notion_client):
        """Test client retrieval with empty response"""
        mock_notion_client.databases.query.return_value = {"results": []}
        
        with patch('notion_client_manager.Client', return_value=mock_notion_client):
            manager = NotionClientManager()
            clients = manager.get_clients()
            
            assert clients == []