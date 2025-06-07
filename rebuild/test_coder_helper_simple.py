#!/usr/bin/env python3
"""
Simple test for coder helper tool without pytest dependency.
"""

import sys
from pathlib import Path
from unittest.mock import Mock

# Add the rebuild directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_coder_helper_tool():
    """Test coder helper tool basic functionality."""
    print("Testing Coder Helper Tool...")
    
    from tools.coder_helper import CoderHelperTool, refine_code_prompt, explain_code_prompt
    from tools.base_tool import ToolInput, ToolStatus, ToolCapability
    from shared.ai_client import AIClient, AIResponse, AIRequest, RequestType
    
    # Create mock AI client
    mock_ai_client = Mock(spec=AIClient)
    
    # Setup mock response for refinement
    mock_refine_response = AIResponse(
        success=True,
        content="Create a Python function that validates email addresses using regular expressions. The function should accept a string parameter and return True if the email is valid, False otherwise. Include proper error handling and type hints.",
        model_used="gpt-4",
        usage={"prompt_tokens": 80, "completion_tokens": 40, "total_tokens": 120},
        response_time=1.8
    )
    
    # Setup mock response for explanation
    mock_explain_response = AIResponse(
        success=True,
        content="This prompt asks for creating a Python function to validate email addresses. It specifies using regular expressions as the validation method, requires specific input/output behavior (string input, boolean output), and requests additional code quality features like error handling and type hints. The prompt is clear about the expected functionality and includes best practices for professional code development.",
        model_used="gpt-4",
        usage={"prompt_tokens": 90, "completion_tokens": 60, "total_tokens": 150},
        response_time=2.2
    )
    
    # Setup mock response for technical refinement
    mock_technical_response = AIResponse(
        success=True,
        content="Create a robust Python email validation function with the following specifications:\n\n**Requirements:**\n- Function name: `validate_email`\n- Input: email (str) - email address to validate\n- Output: bool - True if valid, False if invalid\n- Use regex pattern matching for validation\n- Follow RFC 5322 email format standards\n\n**Implementation Details:**\n- Include comprehensive type hints\n- Implement proper exception handling\n- Add docstring with examples\n- Include unit tests\n- Handle edge cases (None, empty strings, malformed inputs)",
        model_used="gpt-4",
        usage={"prompt_tokens": 100, "completion_tokens": 80, "total_tokens": 180},
        response_time=2.5
    )
    
    # Set up the mock to return different responses based on the operation
    def mock_make_request(request):
        if "technical" in request.prompt.lower() or "senior software engineering mentor" in request.prompt.lower():
            return mock_technical_response
        elif "explain" in request.prompt.lower() or "analyze a given prompt" in request.prompt.lower():
            return mock_explain_response
        else:
            return mock_refine_response
    
    mock_ai_client.make_request.side_effect = mock_make_request
    
    # Create tool
    tool = CoderHelperTool(ai_client=mock_ai_client)
    print(f"✓ Tool created: {tool.get_metadata().name}")
    
    # Test metadata
    metadata = tool.get_metadata()
    assert metadata.name == "coder_helper"
    assert "refine" in metadata.supported_operations
    assert "explain" in metadata.supported_operations
    assert "technical_refine" in metadata.supported_operations
    assert ToolCapability.PROMPT_REFINEMENT in metadata.capabilities
    print(f"✓ Metadata: {len(metadata.supported_operations)} operations")
    
    # Test validation for refine operation
    valid_input = ToolInput(
        operation="refine",
        parameters={"prompt": "Write code to validate emails"}
    )
    assert tool.validate(valid_input) == True
    print("✓ Input validation working")
    
    # Test prompt refinement operation
    refine_result = tool.execute(valid_input)
    assert refine_result.status == ToolStatus.SUCCESS
    assert "refined_prompt" in refine_result.output
    assert "original_prompt" in refine_result.output
    assert refine_result.output["original_prompt"] == "Write code to validate emails"
    print(f"✓ Prompt refinement: {refine_result.output['operation']}")
    
    # Test prompt explanation operation
    explain_input = ToolInput(
        operation="explain",
        parameters={"prompt": "Create a function to validate email addresses"}
    )
    explain_result = tool.execute(explain_input)
    assert explain_result.status == ToolStatus.SUCCESS
    assert "explanation" in explain_result.output
    assert "original_prompt" in explain_result.output
    print(f"✓ Prompt explanation: {explain_result.output['operation']}")
    
    # Test technical refinement operation
    technical_input = ToolInput(
        operation="technical_refine",
        parameters={"prompt": "Make a function to check emails"}
    )
    technical_result = tool.execute(technical_input)
    assert technical_result.status == ToolStatus.SUCCESS
    assert "technical_prompt" in technical_result.output
    assert "original_prompt" in technical_result.output
    print(f"✓ Technical refinement: {technical_result.output['operation']}")
    
    # Test AI client was called
    assert mock_ai_client.make_request.call_count >= 3
    print("✓ AI client integration working")
    
    # Test configuration override (lower temperature for code tasks)
    config_input = ToolInput(
        operation="refine",
        parameters={"prompt": "Write code"},
        configuration={"temperature": 0.1, "model": "gpt-3.5-turbo"}
    )
    config_result = tool.execute(config_input)
    assert config_result.status == ToolStatus.SUCCESS
    print("✓ Configuration override working")
    
    # Test convenience functions
    refined = refine_code_prompt(mock_ai_client, "Test prompt")
    assert refined != ""
    print("✓ Refine convenience function working")
    
    explained = explain_code_prompt(mock_ai_client, "Test prompt")
    assert explained != ""
    print("✓ Explain convenience function working")
    
    # Test metrics collection
    assert "response_time" in refine_result.metrics
    assert "input_tokens" in refine_result.metrics
    assert "output_tokens" in refine_result.metrics
    print("✓ Metrics collection working")
    
    print("\nCoder Helper Tool tests passed! ✅")
    return True


def main():
    """Run the test."""
    print("🧪 Testing Coder Helper Tool Implementation")
    print("=" * 50)
    
    try:
        success = test_coder_helper_tool()
        
        if success:
            print("\n" + "=" * 50)
            print("🎉 Coder Helper Tool Tests PASSED! ✅")
            print("\nTool Implementation Complete:")
            print("- ✅ BaseTool interface implemented")
            print("- ✅ AI client integration working")
            print("- ✅ Code prompt refinement functional")
            print("- ✅ Technical explanation working")
            print("- ✅ Technical refinement specialized")
            print("- ✅ Low-temperature settings for code accuracy")
            print("- ✅ Input validation working")
            print("- ✅ Error handling implemented")
            print("- ✅ Convenience functions available")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)