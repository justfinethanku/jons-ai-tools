"""
Test prompt refiner tool implementation.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add the rebuild directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.prompt_refiner import PromptRefinerTool, refine_prompt, revise_prompt
from tools.base_tool import (
    ToolInput, ToolStatus, ToolCapability, create_tool_input
)
from shared.ai_client import AIClient, AIResponse, AIRequest, RequestType


class TestPromptRefinerTool:
    """Test the prompt refiner tool."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_ai_client = Mock(spec=AIClient)
        self.tool = PromptRefinerTool(ai_client=self.mock_ai_client)
        
        # Setup mock AI response
        self.mock_ai_response = AIResponse(
            success=True,
            content="Analysis: This is a basic request that needs structure.\n\nRefined Prompt:\nYou are an expert data analyst. Analyze the following data and provide insights in a structured format with key findings and recommendations.",
            model_used="gpt-4",
            usage={"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
            response_time=1.5
        )
        self.mock_ai_client.make_request.return_value = self.mock_ai_response
    
    def test_tool_metadata(self):
        """Test tool metadata."""
        metadata = self.tool.get_metadata()
        
        assert metadata.name == "prompt_refiner"
        assert metadata.version == "1.0.0"
        assert "refine" in metadata.supported_operations
        assert "revise" in metadata.supported_operations
        assert "analyze" in metadata.supported_operations
        assert ToolCapability.AI_INTEGRATION in metadata.capabilities
        assert ToolCapability.PROMPT_REFINEMENT in metadata.capabilities
    
    def test_validate_refine_input(self):
        """Test validation for refine operation."""
        # Valid input
        valid_input = ToolInput(
            operation="refine",
            parameters={"prompt": "Analyze data"}
        )
        assert self.tool.validate(valid_input) == True
        
        # Invalid input - missing prompt
        invalid_input = ToolInput(
            operation="refine",
            parameters={}
        )
        assert self.tool.validate(invalid_input) == False
    
    def test_validate_revise_input(self):
        """Test validation for revise operation."""
        # Valid input
        valid_input = ToolInput(
            operation="revise",
            parameters={
                "current_prompt": "Analyze data",
                "revision_request": "Make it more specific"
            }
        )
        assert self.tool.validate(valid_input) == True
        
        # Invalid input - missing revision_request
        invalid_input = ToolInput(
            operation="revise",
            parameters={"current_prompt": "Analyze data"}
        )
        assert self.tool.validate(invalid_input) == False
    
    def test_refine_prompt_operation(self):
        """Test prompt refinement operation."""
        tool_input = ToolInput(
            operation="refine",
            parameters={"prompt": "Analyze data"}
        )
        
        result = self.tool.execute(tool_input)
        
        # Verify result
        assert result.status == ToolStatus.SUCCESS
        assert "refined_prompt" in result.output
        assert "analysis" in result.output
        assert "original_prompt" in result.output
        assert result.output["original_prompt"] == "Analyze data"
        
        # Verify AI client was called
        self.mock_ai_client.make_request.assert_called_once()
        call_args = self.mock_ai_client.make_request.call_args[0][0]
        assert isinstance(call_args, AIRequest)
        assert call_args.request_type == RequestType.CHAT
        assert "Analyze data" in call_args.prompt
    
    def test_revise_prompt_operation(self):
        """Test prompt revision operation."""
        # Mock different response for revision
        revision_response = AIResponse(
            success=True,
            content="You are an expert data analyst. Focus specifically on sales data and provide actionable insights for increasing revenue.",
            model_used="gpt-4",
            usage={"prompt_tokens": 60, "completion_tokens": 25, "total_tokens": 85},
            response_time=1.2
        )
        self.mock_ai_client.make_request.return_value = revision_response
        
        tool_input = ToolInput(
            operation="revise",
            parameters={
                "current_prompt": "Analyze data",
                "revision_request": "Focus on sales data specifically"
            }
        )
        
        result = self.tool.execute(tool_input)
        
        # Verify result
        assert result.status == ToolStatus.SUCCESS
        assert "revised_prompt" in result.output
        assert "original_prompt" in result.output
        assert "revision_request" in result.output
        assert result.output["original_prompt"] == "Analyze data"
        assert result.output["revision_request"] == "Focus on sales data specifically"
        
        # Verify AI client was called with revision prompt
        self.mock_ai_client.make_request.assert_called_once()
        call_args = self.mock_ai_client.make_request.call_args[0][0]
        assert "Analyze data" in call_args.prompt
        assert "Focus on sales data specifically" in call_args.prompt
    
    def test_analyze_prompt_operation(self):
        """Test prompt analysis operation."""
        # Mock analysis response
        analysis_response = AIResponse(
            success=True,
            content="Intent: Basic data analysis request\nStrengths: Clear action word\nWeaknesses: Too vague, no context\nSuggestions: Add specific data type and desired output format",
            model_used="gpt-4",
            usage={"prompt_tokens": 40, "completion_tokens": 35, "total_tokens": 75},
            response_time=1.0
        )
        self.mock_ai_client.make_request.return_value = analysis_response
        
        tool_input = ToolInput(
            operation="analyze",
            parameters={"prompt": "Analyze data"}
        )
        
        result = self.tool.execute(tool_input)
        
        # Verify result
        assert result.status == ToolStatus.SUCCESS
        assert "analysis" in result.output
        assert "original_prompt" in result.output
        assert result.output["original_prompt"] == "Analyze data"
        
        # Verify AI client was called
        self.mock_ai_client.make_request.assert_called_once()
    
    def test_ai_request_failure(self):
        """Test handling of AI request failures."""
        # Mock failed AI response
        failed_response = AIResponse(
            success=False,
            error_message="API rate limit exceeded"
        )
        self.mock_ai_client.make_request.return_value = failed_response
        
        tool_input = ToolInput(
            operation="refine",
            parameters={"prompt": "Analyze data"}
        )
        
        result = self.tool.execute(tool_input)
        
        # Verify error result
        assert result.status == ToolStatus.ERROR
        assert len(result.errors) > 0
        assert "API rate limit exceeded" in result.errors[0]
    
    def test_unsupported_operation(self):
        """Test handling of unsupported operations."""
        tool_input = ToolInput(
            operation="unsupported",
            parameters={"prompt": "Test"}
        )
        
        result = self.tool.execute(tool_input)
        
        # Verify error result
        assert result.status == ToolStatus.ERROR
        assert len(result.errors) > 0
        assert "Unsupported operation" in result.errors[0]
    
    def test_configuration_override(self):
        """Test configuration override in tool input."""
        tool_input = ToolInput(
            operation="refine",
            parameters={"prompt": "Analyze data"},
            configuration={
                "model": "gpt-3.5-turbo",
                "temperature": 0.8,
                "max_tokens": 1500
            }
        )
        
        result = self.tool.execute(tool_input)
        
        # Verify configuration was applied
        assert result.status == ToolStatus.SUCCESS
        call_args = self.mock_ai_client.make_request.call_args[0][0]
        assert call_args.model == "gpt-3.5-turbo"
        assert call_args.temperature == 0.8
        assert call_args.max_tokens == 1500
    
    def test_metrics_collection(self):
        """Test that metrics are properly collected."""
        tool_input = ToolInput(
            operation="refine",
            parameters={"prompt": "Analyze data"}
        )
        
        result = self.tool.execute(tool_input)
        
        # Verify metrics
        assert result.status == ToolStatus.SUCCESS
        assert "response_time" in result.metrics
        assert "input_tokens" in result.metrics
        assert "output_tokens" in result.metrics
        assert result.metrics["response_time"] == 1.5
        assert result.metrics["input_tokens"] == 50
        assert result.metrics["output_tokens"] == 30
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        # Test refine_prompt function
        refined = refine_prompt(self.mock_ai_client, "Analyze data")
        
        # Should return the refined prompt content
        assert refined == "You are an expert data analyst. Analyze the following data and provide insights in a structured format with key findings and recommendations."
        
        # Test revise_prompt function
        revision_response = AIResponse(
            success=True,
            content="Revised prompt content",
            model_used="gpt-4",
            usage={"total_tokens": 50},
            response_time=1.0
        )
        self.mock_ai_client.make_request.return_value = revision_response
        
        revised = revise_prompt(self.mock_ai_client, "Original prompt", "Make it better")
        assert revised == "Revised prompt content"


if __name__ == "__main__":
    pytest.main([__file__])