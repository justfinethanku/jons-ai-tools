"""
Unit tests for research_tools_framework.py
Tests NotionDatabaseManager and related functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from frameworks.research_tools_framework import NotionDatabaseManager

class TestNotionDatabaseManagerInit:
    """Test NotionDatabaseManager initialization"""
    
    def test_initialization_with_api_key(self):
        """Test initialization with provided API key"""
        with patch('frameworks.research_tools_framework.Client') as mock_client:
            manager = NotionDatabaseManager(notion_api_key="test_key")
            
            mock_client.assert_called_once_with(auth="test_key")
            assert manager.client_database_id == "test_db_id"
            assert manager.content_samples_database_id == "test_content_samples_db_id"
            assert manager.voice_guidelines_database_id == "test_voice_guidelines_db_id"
            
    def test_initialization_without_api_key(self):
        """Test initialization using secrets"""
        with patch('frameworks.research_tools_framework.Client') as mock_client:
            manager = NotionDatabaseManager()
            
            mock_client.assert_called_once_with(auth="test_api_key")

class TestClientListRetrieval:
    """Test client list retrieval functionality"""
    
    def test_get_client_list_success(self, mock_notion_client):
        """Test successful client list retrieval"""
        # Mock response with client data
        mock_notion_client.databases.query.return_value = {
            "results": [
                {
                    "id": "client_1_id",
                    "properties": {
                        "Name": {
                            "title": [
                                {
                                    "text": {"content": "Client 1"},
                                    "plain_text": "Client 1"
                                }
                            ]
                        }
                    }
                },
                {
                    "id": "client_2_id", 
                    "properties": {
                        "Name": {
                            "title": [
                                {
                                    "text": {"content": "Client 2"},
                                    "plain_text": "Client 2"
                                }
                            ]
                        }
                    }
                }
            ]
        }
        
        with patch('frameworks.research_tools_framework.Client', return_value=mock_notion_client):
            manager = NotionDatabaseManager()
            clients = manager.get_client_list()
            
            assert len(clients) == 2
            assert "Client 1" in clients
            assert "Client 2" in clients
            assert clients["Client 1"] == "client_1_id"
            assert clients["Client 2"] == "client_2_id"
            
    def test_get_client_list_empty_results(self, mock_notion_client):
        """Test client list retrieval with empty results"""
        mock_notion_client.databases.query.return_value = {"results": []}
        
        with patch('frameworks.research_tools_framework.Client', return_value=mock_notion_client):
            manager = NotionDatabaseManager()
            clients = manager.get_client_list()
            
            assert clients == {}
            
    def test_get_client_list_missing_name(self, mock_notion_client):
        """Test client list retrieval with missing name property"""
        mock_notion_client.databases.query.return_value = {
            "results": [
                {
                    "id": "client_id",
                    "properties": {
                        "Name": {"title": []}  # Empty title
                    }
                }
            ]
        }
        
        with patch('frameworks.research_tools_framework.Client', return_value=mock_notion_client):
            manager = NotionDatabaseManager()
            clients = manager.get_client_list()
            
            assert clients == {}
            
    def test_get_client_list_sorts_correctly(self, mock_notion_client):
        """Test that client list query includes proper sorting"""
        mock_notion_client.databases.query.return_value = {"results": []}
        
        with patch('frameworks.research_tools_framework.Client', return_value=mock_notion_client):
            manager = NotionDatabaseManager()
            manager.get_client_list()
            
            # Verify the query was called with correct sorting
            call_args = mock_notion_client.databases.query.call_args
            assert call_args[1]["database_id"] == "test_db_id"
            assert call_args[1]["sorts"] == [{
                "property": "Name",
                "direction": "ascending"
            }]

class TestClientCreation:
    """Test new client creation functionality"""
    
    def test_create_new_client_basic(self, mock_notion_client):
        """Test basic client creation"""
        mock_notion_client.pages.create.return_value = {
            "id": "new_client_id",
            "url": "https://notion.so/new_client_id"
        }
        
        with patch('frameworks.research_tools_framework.Client', return_value=mock_notion_client):
            manager = NotionDatabaseManager()
            result = manager.create_new_client("Test Client", "Technology")
            
            # Verify page creation was called
            assert mock_notion_client.pages.create.called
            call_args = mock_notion_client.pages.create.call_args
            
            # Check database parent
            assert call_args[1]["parent"]["database_id"] == "test_db_id"
            
            # Check properties
            properties = call_args[1]["properties"]
            assert properties["Name"]["title"][0]["text"]["content"] == "Test Client"
            assert properties["Industry"]["select"]["name"] == "Technology"

class TestDatabaseIntegration:
    """Test database integration features"""
    
    def test_database_ids_configured(self):
        """Test that all required database IDs are configured"""
        with patch('frameworks.research_tools_framework.Client'):
            manager = NotionDatabaseManager()
            
            assert hasattr(manager, 'client_database_id')
            assert hasattr(manager, 'content_samples_database_id') 
            assert hasattr(manager, 'voice_guidelines_database_id')
            assert manager.client_database_id == "test_db_id"
            assert manager.content_samples_database_id == "test_content_samples_db_id"
            assert manager.voice_guidelines_database_id == "test_voice_guidelines_db_id"

@pytest.mark.unit
class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_get_client_list_api_error(self, mock_notion_client):
        """Test client list retrieval with API error"""
        mock_notion_client.databases.query.side_effect = Exception("API Error")
        
        with patch('frameworks.research_tools_framework.Client', return_value=mock_notion_client):
            manager = NotionDatabaseManager()
            
            # Should handle error gracefully
            with pytest.raises(Exception):
                manager.get_client_list()
                
    def test_create_client_api_error(self, mock_notion_client):
        """Test client creation with API error"""
        mock_notion_client.pages.create.side_effect = Exception("API Error")
        
        with patch('frameworks.research_tools_framework.Client', return_value=mock_notion_client):
            manager = NotionDatabaseManager()
            
            # Should handle error gracefully
            with pytest.raises(Exception):
                manager.create_new_client("Test Client", "Technology")
                
    def test_malformed_client_data(self, mock_notion_client):
        """Test handling of malformed client data"""
        mock_notion_client.databases.query.return_value = {
            "results": [
                {
                    "id": "client_id",
                    "properties": {
                        # Missing Name property
                        "Other": {"rich_text": []}
                    }
                }
            ]
        }
        
        with patch('frameworks.research_tools_framework.Client', return_value=mock_notion_client):
            manager = NotionDatabaseManager()
            clients = manager.get_client_list()
            
            # Should handle missing Name gracefully
            assert clients == {}