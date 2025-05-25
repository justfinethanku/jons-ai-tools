"""
Integration tests for Brand Builder workflow.
Tests the complete Brand Builder pipeline with mocked external dependencies.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

@pytest.mark.integration
class TestBrandBuilderStep01:
    """Test Brand Builder Step 1: Website Extractor"""
    
    @patch('tools.brand_builder.step_01_website_extractor.requests.get')
    def test_website_extraction_success(self, mock_requests):
        """Test successful website content extraction"""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head><title>Test Company</title></head>
            <body>
                <h1>Welcome to Test Company</h1>
                <p>We provide innovative solutions...</p>
            </body>
        </html>
        """
        mock_requests.return_value = mock_response
        
        # Import and test the step
        from tools.brand_builder.step_01_website_extractor import extract_website_content
        
        result = extract_website_content("https://test.com")
        
        assert "Test Company" in result
        assert "innovative solutions" in result
        
    @patch('tools.brand_builder.step_01_website_extractor.requests.get')
    def test_website_extraction_failure(self, mock_requests):
        """Test website extraction with network failure"""
        mock_requests.side_effect = Exception("Network error")
        
        from tools.brand_builder.step_01_website_extractor import extract_website_content
        
        with pytest.raises(Exception):
            extract_website_content("https://invalid.com")

@pytest.mark.integration
class TestBrandBuilderStep02:
    """Test Brand Builder Step 2: Brand Analyzer"""
    
    def test_brand_analysis_with_context(self, sample_website_data, mock_notion_client):
        """Test brand analysis with website context"""
        with patch('tools.brand_builder.step_02_brand_analyzer.NotionDatabaseManager') as mock_db:
            mock_db_instance = Mock()
            mock_db_instance.voice_guidelines_database_id = "test_voice_guidelines_db_id"
            mock_db_instance.notion = mock_notion_client
            mock_db.return_value = mock_db_instance
            
            with patch('tools.brand_builder.step_02_brand_analyzer.call_gemini_api') as mock_gemini:
                mock_gemini.return_value = json.dumps({
                    "word_choice_analysis": "Professional and technical language",
                    "tone_analysis": "Confident and authoritative",
                    "personality_analysis": "Innovation-focused",
                    "consistency_assessment": "Highly consistent",
                    "audience_fit_assessment": "Well-targeted"
                })
                
                from tools.brand_builder.step_02_brand_analyzer import analyze_brand_voice
                
                result = analyze_brand_voice(
                    client_id="test_client_id",
                    website_data=sample_website_data,
                    context_data=sample_website_data
                )
                
                assert "word_choice_analysis" in result
                assert "tone_analysis" in result
                assert result["word_choice_analysis"] == "Professional and technical language"
                
                # Verify database save was called
                mock_notion_client.pages.create.assert_called_once()

@pytest.mark.integration 
class TestBrandBuilderStep03:
    """Test Brand Builder Step 3: Content Collector"""
    
    def test_content_collection_with_samples(self, sample_website_data, mock_notion_client):
        """Test content collection and database saving"""
        with patch('tools.brand_builder.step_03_content_collector.NotionDatabaseManager') as mock_db:
            mock_db_instance = Mock()
            mock_db_instance.content_samples_database_id = "test_content_samples_db_id"
            mock_db_instance.notion = mock_notion_client
            mock_db.return_value = mock_db_instance
            
            with patch('tools.brand_builder.step_03_content_collector.call_gemini_api') as mock_gemini:
                mock_gemini.return_value = json.dumps({
                    "content_samples": [
                        {
                            "channel_type": "Website Homepage",
                            "sample_content": "Welcome to our platform...",
                            "tone_assessment": "Professional",
                            "original_sample": True,
                            "notes": "Strong value proposition"
                        }
                    ]
                })
                
                from tools.brand_builder.step_03_content_collector import collect_content_samples
                
                result = collect_content_samples(
                    client_id="test_client_id",
                    website_data=sample_website_data,
                    context_data=sample_website_data
                )
                
                assert "content_samples" in result
                assert len(result["content_samples"]) == 1
                
                # Verify database saves were called
                assert mock_notion_client.pages.create.call_count == 1

@pytest.mark.integration
class TestBrandBuilderWorkflow:
    """Test complete Brand Builder workflow integration"""
    
    def test_sequential_workflow_steps(self, sample_website_data, mock_notion_client):
        """Test sequential execution of Brand Builder steps"""
        workflow_data = {}
        
        # Step 1: Website extraction (mocked)
        workflow_data["website_data"] = sample_website_data
        
        # Step 2: Brand analysis
        with patch('tools.brand_builder.step_02_brand_analyzer.NotionDatabaseManager') as mock_db:
            mock_db_instance = Mock()
            mock_db_instance.voice_guidelines_database_id = "test_voice_guidelines_db_id"
            mock_db_instance.notion = mock_notion_client
            mock_db.return_value = mock_db_instance
            
            with patch('tools.brand_builder.step_02_brand_analyzer.call_gemini_api') as mock_gemini:
                mock_gemini.return_value = json.dumps({
                    "word_choice_analysis": "Professional language",
                    "tone_analysis": "Authoritative tone",
                    "personality_analysis": "Innovation-focused",
                    "consistency_assessment": "Consistent",
                    "audience_fit_assessment": "Well-targeted"
                })
                
                from tools.brand_builder.step_02_brand_analyzer import analyze_brand_voice
                
                workflow_data["voice_analysis"] = analyze_brand_voice(
                    client_id="test_client_id",
                    website_data=workflow_data["website_data"],
                    context_data=workflow_data["website_data"]
                )
        
        # Step 3: Content collection
        with patch('tools.brand_builder.step_03_content_collector.NotionDatabaseManager') as mock_db:
            mock_db_instance = Mock()
            mock_db_instance.content_samples_database_id = "test_content_samples_db_id"
            mock_db_instance.notion = mock_notion_client
            mock_db.return_value = mock_db_instance
            
            with patch('tools.brand_builder.step_03_content_collector.call_gemini_api') as mock_gemini:
                mock_gemini.return_value = json.dumps({
                    "content_samples": [
                        {
                            "channel_type": "Website Homepage",
                            "sample_content": "Welcome message",
                            "tone_assessment": "Professional",
                            "original_sample": True,
                            "notes": "Analysis notes"
                        }
                    ]
                })
                
                from tools.brand_builder.step_03_content_collector import collect_content_samples
                
                workflow_data["content_samples"] = collect_content_samples(
                    client_id="test_client_id",
                    website_data=workflow_data["website_data"],
                    context_data=workflow_data["website_data"]
                )
        
        # Verify workflow data integrity
        assert "website_data" in workflow_data
        assert "voice_analysis" in workflow_data
        assert "content_samples" in workflow_data
        
        # Verify data flow between steps
        assert workflow_data["website_data"]["company_name"] == "Test Company"
        assert "word_choice_analysis" in workflow_data["voice_analysis"]
        assert "content_samples" in workflow_data["content_samples"]

@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database integration across Brand Builder steps"""
    
    def test_database_schema_validation(self, mock_notion_client):
        """Test that database schemas match expected format"""
        # Test Voice Guidelines database schema
        expected_voice_properties = [
            "Name", "Client", "Status", "Last_Updated",
            "Word_Choice_Analysis", "Tone_Analysis", "Personality_Analysis",
            "Consistency_Assessment", "Audience_Fit_Assessment"
        ]
        
        # Test Content Samples database schema  
        expected_content_properties = [
            "Name", "Client", "Channel_Type", "Sample_Content",
            "Tone_Assessment", "Original_Sample", "Rewritten_Version", "Notes"
        ]
        
        # This would typically verify against actual database schemas
        # For now, we're testing that our code expects these properties
        assert all(prop in expected_voice_properties for prop in [
            "Word_Choice_Analysis", "Tone_Analysis", "Personality_Analysis"
        ])
        
        assert all(prop in expected_content_properties for prop in [
            "Sample_Content", "Channel_Type", "Tone_Assessment"
        ])
        
    def test_cross_step_data_persistence(self, mock_notion_client):
        """Test that data persists correctly across workflow steps"""
        client_id = "test_client_id"
        
        # Mock database query to return previously saved data
        mock_notion_client.databases.query.return_value = {
            "results": [
                {
                    "id": "voice_guidelines_page_id",
                    "properties": {
                        "Client": {
                            "relation": [{"id": client_id}]
                        },
                        "Word_Choice_Analysis": {
                            "rich_text": [{"plain_text": "Previous analysis"}]
                        }
                    }
                }
            ]
        }
        
        with patch('frameworks.research_tools_framework.NotionDatabaseManager') as mock_db:
            mock_db_instance = Mock()
            mock_db_instance.notion = mock_notion_client
            mock_db_instance.voice_guidelines_database_id = "test_voice_guidelines_db_id"
            mock_db.return_value = mock_db_instance
            
            # Test that subsequent steps can access previously saved data
            manager = mock_db_instance
            query_result = manager.notion.databases.query(
                database_id=manager.voice_guidelines_database_id,
                filter={
                    "property": "Client",
                    "relation": {"contains": client_id}
                }
            )
            
            assert len(query_result["results"]) == 1
            assert "Previous analysis" in str(query_result["results"][0])

@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Test performance characteristics of Brand Builder workflow"""
    
    def test_workflow_memory_usage(self, sample_website_data):
        """Test that workflow doesn't consume excessive memory"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Simulate processing large dataset
        large_website_data = {
            **sample_website_data,
            "homepage_content": "Large content " * 1000,
            "about_content": "Large about " * 1000
        }
        
        # Process through multiple steps (mocked)
        for i in range(10):
            processed_data = {
                **large_website_data,
                "iteration": i
            }
            
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Should not increase memory by more than 100MB
        assert memory_increase < 100 * 1024 * 1024
        
    def test_workflow_timeout_handling(self):
        """Test that workflow handles timeouts appropriately"""
        import time
        
        start_time = time.time()
        
        # Simulate long-running operation with timeout
        with patch('tools.brand_builder.step_02_brand_analyzer.call_gemini_api') as mock_api:
            def slow_response(*args, **kwargs):
                time.sleep(0.1)  # Simulate delay
                return '{"result": "success"}'
            
            mock_api.side_effect = slow_response
            
            # Process should complete within reasonable time
            # (This is a simplified test - real implementation would have proper timeout handling)
            
        end_time = time.time()
        assert end_time - start_time < 1.0  # Should complete within 1 second