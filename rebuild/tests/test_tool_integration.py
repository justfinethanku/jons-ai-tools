"""
Integration tests for tool execution pipeline.

Tests the complete workflow from tool input through AI client to final output.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

# Import the modules under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.base_tool import (
    BaseTool, ToolMetadata, ToolInput, ToolResult, ToolStatus,
    ToolCapability, ExecutionContext
)
from shared.ai_client import AIClient, APIProvider, ClientConfig, AIRequest, AIResponse, RequestType
from core.llm_integrator import LLMIntegrator, CodeContext


class MockTool(BaseTool):
    """Mock tool for testing."""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="mock_tool",
            version="1.0.0",
            description="Mock tool for testing",
            supported_operations=["test_operation"],
            capabilities=[ToolCapability.TEXT_PROCESSING]
        )
    
    def execute(self, tool_input: ToolInput) -> ToolResult:
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output={"result": f"Processed: {tool_input.operation}"},
            metadata={"processed_at": "2024-01-01"}
        )
    
    def validate(self, tool_input: ToolInput) -> bool:
        return tool_input.operation in ["test_operation"]


class TestToolExecutionPipeline:
    """Test the complete tool execution pipeline."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_ai_client = Mock(spec=AIClient)
        self.mock_llm_integrator = Mock(spec=LLMIntegrator)
        self.mock_tool = MockTool()
        
        # Setup mock AI response
        self.mock_ai_response = AIResponse(
            success=True,
            content="Generated content based on prompt",
            model_used="gpt-4",
            usage={"total_tokens": 100},
            response_time=1.0
        )
        self.mock_ai_client.make_request.return_value = self.mock_ai_response
    
    def test_basic_tool_functionality(self):
        """Test basic tool functionality without AI integration."""
        # Test metadata
        metadata = self.mock_tool.get_metadata()
        assert metadata.name == "mock_tool"
        assert metadata.version == "1.0.0"
        assert "test_operation" in metadata.supported_operations
        
        # Test validation
        valid_input = ToolInput(operation="test_operation")
        invalid_input = ToolInput(operation="invalid_operation")
        
        assert self.mock_tool.validate(valid_input) == True
        assert self.mock_tool.validate(invalid_input) == False
        
        # Test execution
        result = self.mock_tool.execute(valid_input)
        assert result.status == ToolStatus.SUCCESS
        assert "Processed: test_operation" in result.output["result"]
    
    def test_tool_with_ai_client_integration(self):
        """Test tool integration with AI client."""
        # Create a tool that uses AI client
        class AITool(BaseTool):
            def __init__(self, ai_client):
                super().__init__()
                self.ai_client = ai_client
            
            def get_metadata(self) -> ToolMetadata:
                return ToolMetadata(
                    name="ai_tool",
                    version="1.0.0",
                    description="AI-powered tool",
                    supported_operations=["generate"],
                    capabilities=[ToolCapability.AI_INTEGRATION]
                )
            
            def execute(self, tool_input: ToolInput) -> ToolResult:
                # Make AI request
                ai_request = AIRequest(
                    request_type=RequestType.CHAT,
                    prompt=f"Process this: {tool_input.parameters.get('prompt', '')}"
                )
                
                ai_response = self.ai_client.make_request(ai_request)
                
                if ai_response.success:
                    return ToolResult(
                        status=ToolStatus.SUCCESS,
                        output={"generated_content": ai_response.content},
                        metadata={"model_used": ai_response.model_used}
                    )
                else:
                    return ToolResult(
                        status=ToolStatus.ERROR,
                        output={},
                        errors=[ai_response.error_message]
                    )
            
            def validate(self, tool_input: ToolInput) -> bool:
                return tool_input.operation == "generate"
        
        # Test the AI tool
        ai_tool = AITool(self.mock_ai_client)
        
        tool_input = ToolInput(
            operation="generate",
            parameters={"prompt": "Generate a test function"}
        )
        
        result = ai_tool.execute(tool_input)
        
        assert result.status == ToolStatus.SUCCESS
        assert "generated_content" in result.output
        assert result.output["generated_content"] == "Generated content based on prompt"
        assert result.metadata["model_used"] == "gpt-4"
        
        # Verify AI client was called
        self.mock_ai_client.make_request.assert_called_once()
        call_args = self.mock_ai_client.make_request.call_args[0][0]
        assert isinstance(call_args, AIRequest)
        assert "Generate a test function" in call_args.prompt
    
    def test_tool_error_handling(self):
        """Test tool error handling."""
        # Mock AI client failure
        error_response = AIResponse(
            success=False,
            error_message="API rate limit exceeded",
            response_time=0.1
        )
        self.mock_ai_client.make_request.return_value = error_response
        
        class ErrorTool(BaseTool):
            def __init__(self, ai_client):
                self.ai_client = ai_client
            
            def get_metadata(self) -> ToolMetadata:
                return ToolMetadata(
                    name="error_tool",
                    version="1.0.0",
                    description="Tool that tests error handling",
                    supported_operations=["fail"],
                    capabilities=[ToolCapability.AI_INTEGRATION]
                )
            
            def execute(self, tool_input: ToolInput) -> ToolResult:
                ai_request = AIRequest(
                    request_type=RequestType.CHAT,
                    prompt="This will fail"
                )
                
                ai_response = self.ai_client.make_request(ai_request)
                
                if not ai_response.success:
                    return ToolResult(
                        status=ToolStatus.ERROR,
                        output={},
                        errors=[ai_response.error_message],
                        metadata={"failure_reason": "ai_api_error"}
                    )
                
                return ToolResult(status=ToolStatus.SUCCESS, output={})
            
            def validate(self, tool_input: ToolInput) -> bool:
                return True
        
        error_tool = ErrorTool(self.mock_ai_client)
        tool_input = ToolInput(operation="fail")
        
        result = error_tool.execute(tool_input)
        
        assert result.status == ToolStatus.ERROR
        assert len(result.errors) > 0
        assert "API rate limit exceeded" in result.errors[0]
        assert result.metadata["failure_reason"] == "ai_api_error"
    
    def test_tool_with_llm_integrator(self):
        """Test tool integration with LLM integrator."""
        class RuleDrivenTool(BaseTool):
            def __init__(self, llm_integrator):
                self.llm_integrator = llm_integrator
            
            def get_metadata(self) -> ToolMetadata:
                return ToolMetadata(
                    name="rule_driven_tool",
                    version="1.0.0",
                    description="Tool that uses LLM integrator",
                    supported_operations=["generate_with_rules"],
                    capabilities=[ToolCapability.RULE_PROCESSING, ToolCapability.AI_INTEGRATION]
                )
            
            def execute(self, tool_input: ToolInput) -> ToolResult:
                # Extract rules and context from input
                rules = tool_input.parameters.get("rules", {})
                context = CodeContext(
                    file_path=tool_input.parameters.get("file_path", "/test.py"),
                    function_name=tool_input.parameters.get("function_name")
                )
                
                # Convert rules to prompt using LLM integrator
                prompt = self.llm_integrator.convert_rules_to_prompt(rules, context)
                
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    output={"generated_prompt": prompt},
                    metadata={"rule_count": len(rules)}
                )
            
            def validate(self, tool_input: ToolInput) -> bool:
                return tool_input.operation == "generate_with_rules"
        
        # Mock LLM integrator
        self.mock_llm_integrator.convert_rules_to_prompt.return_value = "Generated prompt with rules applied"
        
        rule_tool = RuleDrivenTool(self.mock_llm_integrator)
        
        tool_input = ToolInput(
            operation="generate_with_rules",
            parameters={
                "rules": {
                    "PURPOSE": "Generate utility function",
                    "IMPORTS_ALLOWED": "os, sys"
                },
                "file_path": "/utils/helpers.py",
                "function_name": "process_data"
            }
        )
        
        result = rule_tool.execute(tool_input)
        
        assert result.status == ToolStatus.SUCCESS
        assert "generated_prompt" in result.output
        assert result.output["generated_prompt"] == "Generated prompt with rules applied"
        assert result.metadata["rule_count"] == 2
        
        # Verify LLM integrator was called correctly
        self.mock_llm_integrator.convert_rules_to_prompt.assert_called_once()
        call_args = self.mock_llm_integrator.convert_rules_to_prompt.call_args
        rules, context = call_args[0]
        
        assert rules["PURPOSE"] == "Generate utility function"
        assert context.file_path == "/utils/helpers.py"
        assert context.function_name == "process_data"
    
    def test_tool_execution_context(self):
        """Test tool execution with execution context."""
        class ContextAwareTool(BaseTool):
            def get_metadata(self) -> ToolMetadata:
                return ToolMetadata(
                    name="context_tool",
                    version="1.0.0",
                    description="Context-aware tool",
                    supported_operations=["process_with_context"],
                    capabilities=[ToolCapability.CONTEXT_AWARE]
                )
            
            def execute(self, tool_input: ToolInput) -> ToolResult:
                # Access execution context
                context = tool_input.execution_context
                
                output = {
                    "user_id": context.user_id if context else "unknown",
                    "session_id": context.session_id if context else "unknown",
                    "operation": tool_input.operation
                }
                
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    output=output,
                    metadata={"context_available": context is not None}
                )
            
            def validate(self, tool_input: ToolInput) -> bool:
                return True
        
        context_tool = ContextAwareTool()
        
        # Test with execution context
        execution_context = ExecutionContext(
            user_id="test_user",
            session_id="session_123",
            environment="test"
        )
        
        tool_input = ToolInput(
            operation="process_with_context",
            execution_context=execution_context
        )
        
        result = context_tool.execute(tool_input)
        
        assert result.status == ToolStatus.SUCCESS
        assert result.output["user_id"] == "test_user"
        assert result.output["session_id"] == "session_123"
        assert result.metadata["context_available"] == True
    
    def test_tool_prompt_loading(self):
        """Test tool loading prompts from files."""
        class PromptBasedTool(BaseTool):
            def __init__(self, prompts_dir):
                self.prompts_dir = Path(prompts_dir)
            
            def get_metadata(self) -> ToolMetadata:
                return ToolMetadata(
                    name="prompt_tool",
                    version="1.0.0",
                    description="Tool that loads prompts from files",
                    supported_operations=["generate_from_template"],
                    capabilities=[ToolCapability.TEMPLATE_PROCESSING]
                )
            
            def _load_prompt(self, prompt_name: str) -> str:
                """Load prompt from file."""
                prompt_file = self.prompts_dir / f"{prompt_name}.txt"
                if prompt_file.exists():
                    return prompt_file.read_text()
                return f"Default prompt for {prompt_name}"
            
            def execute(self, tool_input: ToolInput) -> ToolResult:
                template_name = tool_input.parameters.get("template", "default")
                prompt_template = self._load_prompt(template_name)
                
                # Simple template variable replacement
                variables = tool_input.parameters.get("variables", {})
                formatted_prompt = prompt_template
                for key, value in variables.items():
                    formatted_prompt = formatted_prompt.replace(f"{{{key}}}", str(value))
                
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    output={"formatted_prompt": formatted_prompt},
                    metadata={"template_used": template_name}
                )
            
            def validate(self, tool_input: ToolInput) -> bool:
                return tool_input.operation == "generate_from_template"
        
        # Create temporary prompts directory
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir)
            
            # Create test prompt file
            test_prompt_file = prompts_dir / "test_template.txt"
            test_prompt_file.write_text("Generate {function_name} for {purpose}")
            
            prompt_tool = PromptBasedTool(prompts_dir)
            
            tool_input = ToolInput(
                operation="generate_from_template",
                parameters={
                    "template": "test_template",
                    "variables": {
                        "function_name": "process_data",
                        "purpose": "data processing"
                    }
                }
            )
            
            result = prompt_tool.execute(tool_input)
            
            assert result.status == ToolStatus.SUCCESS
            assert result.output["formatted_prompt"] == "Generate process_data for data processing"
            assert result.metadata["template_used"] == "test_template"
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # This simulates a real tool workflow:
        # 1. Validate input
        # 2. Load prompt template
        # 3. Apply rules via LLM integrator
        # 4. Make AI request
        # 5. Process response
        # 6. Return formatted result
        
        class CompleteWorkflowTool(BaseTool):
            def __init__(self, ai_client, llm_integrator):
                self.ai_client = ai_client
                self.llm_integrator = llm_integrator
            
            def get_metadata(self) -> ToolMetadata:
                return ToolMetadata(
                    name="complete_workflow_tool",
                    version="1.0.0",
                    description="Complete workflow tool",
                    supported_operations=["full_workflow"],
                    capabilities=[
                        ToolCapability.AI_INTEGRATION,
                        ToolCapability.RULE_PROCESSING,
                        ToolCapability.TEMPLATE_PROCESSING
                    ]
                )
            
            def execute(self, tool_input: ToolInput) -> ToolResult:
                try:
                    # Step 1: Extract parameters
                    rules = tool_input.parameters.get("rules", {})
                    context_data = tool_input.parameters.get("context", {})
                    
                    # Step 2: Create context
                    context = CodeContext(
                        file_path=context_data.get("file_path", "/test.py"),
                        function_name=context_data.get("function_name")
                    )
                    
                    # Step 3: Generate prompt with rules
                    base_prompt = self.llm_integrator.convert_rules_to_prompt(rules, context)
                    
                    # Step 4: Make AI request
                    ai_request = AIRequest(
                        request_type=RequestType.CHAT,
                        prompt=base_prompt,
                        temperature=tool_input.parameters.get("temperature", 0.7)
                    )
                    
                    ai_response = self.ai_client.make_request(ai_request)
                    
                    if ai_response.success:
                        return ToolResult(
                            status=ToolStatus.SUCCESS,
                            output={
                                "generated_content": ai_response.content,
                                "prompt_used": base_prompt,
                                "token_usage": ai_response.usage
                            },
                            metadata={
                                "model_used": ai_response.model_used,
                                "response_time": ai_response.response_time,
                                "rules_applied": len(rules)
                            }
                        )
                    else:
                        return ToolResult(
                            status=ToolStatus.ERROR,
                            output={},
                            errors=[ai_response.error_message]
                        )
                
                except Exception as e:
                    return ToolResult(
                        status=ToolStatus.ERROR,
                        output={},
                        errors=[str(e)]
                    )
            
            def validate(self, tool_input: ToolInput) -> bool:
                return (
                    tool_input.operation == "full_workflow" and
                    "rules" in tool_input.parameters and
                    "context" in tool_input.parameters
                )
        
        # Set up mocks
        self.mock_llm_integrator.convert_rules_to_prompt.return_value = "Complete prompt with rules applied"
        
        workflow_tool = CompleteWorkflowTool(self.mock_ai_client, self.mock_llm_integrator)
        
        tool_input = ToolInput(
            operation="full_workflow",
            parameters={
                "rules": {
                    "PURPOSE": "Generate utility function",
                    "RESPONSIBILITY": "Process user data",
                    "IMPORTS_ALLOWED": "os, sys, pathlib"
                },
                "context": {
                    "file_path": "/utils/data_processor.py",
                    "function_name": "process_user_data"
                },
                "temperature": 0.8
            }
        )
        
        # Validate input
        assert workflow_tool.validate(tool_input) == True
        
        # Execute workflow
        result = workflow_tool.execute(tool_input)
        
        # Verify success
        assert result.status == ToolStatus.SUCCESS
        assert "generated_content" in result.output
        assert "prompt_used" in result.output
        assert "token_usage" in result.output
        
        assert result.output["generated_content"] == "Generated content based on prompt"
        assert result.output["prompt_used"] == "Complete prompt with rules applied"
        assert result.output["token_usage"]["total_tokens"] == 100
        
        assert result.metadata["model_used"] == "gpt-4"
        assert result.metadata["rules_applied"] == 3
        
        # Verify all integrations were called
        self.mock_llm_integrator.convert_rules_to_prompt.assert_called_once()
        self.mock_ai_client.make_request.assert_called_once()
        
        # Verify call arguments
        llm_call_args = self.mock_llm_integrator.convert_rules_to_prompt.call_args[0]
        rules, context = llm_call_args
        assert rules["PURPOSE"] == "Generate utility function"
        assert context.function_name == "process_user_data"
        
        ai_call_args = self.mock_ai_client.make_request.call_args[0][0]
        assert ai_call_args.prompt == "Complete prompt with rules applied"
        assert ai_call_args.temperature == 0.8


if __name__ == "__main__":
    pytest.main([__file__])