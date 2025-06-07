"""
@RULE:LAYER: tools/coder_helper
@RULE:FORBIDDEN: core.*, main, streamlit, frameworks.*
@SEE: tools/CLAUDE.md#base-tool-patterns
Code-focused prompt refinement and explanation tool
"""

# Allowed imports
import logging
import time
from typing import Dict, Any, Optional
from pathlib import Path

# Import from base tool layer
from .base_tool import (
    BaseTool, ToolMetadata, ToolInput, ToolResult, ToolStatus,
    ToolCapability, create_success_result, create_error_result
)

# Import from shared layer
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.ai_client import AIClient, AIRequest, RequestType


# Built-in code prompt refinement template
CODE_PROMPT_TEMPLATE = """Role: Prompt Engineering Expert

Objective:
Rewrite the following prompt so it is clearer and easier for an LLM (like GPT-4) to understand and respond to. Keep the meaning the same. Do not add or remove information. Just rephrase for clarity.

Prompt:
[ {rough_prompt} ]

Rewritten for clarity:"""

# Built-in code explanation template
EXPLAINER_TEMPLATE = """Role: AI Prompt Engineer
Objective: Analyze a given prompt and explain its functionality in a clear, concise manner.

Input: {prompt_to_analyze}

Instructions:
1. Identify the prompt's intent and goal.
2. Describe the expected output and format.
3. Explain how the prompt's instructions guide the AI's response.
4. Provide a simple example of how the prompt would work.

Output Format: A paragraph of approximately 150 words explaining the prompt's functionality. Use simple language, avoiding technical jargon.

Style: Easy-to-understand, explanatory.
Target Audience: Non-technical users"""

# Code-specific refinement template for technical prompts
TECHNICAL_REFINEMENT_TEMPLATE = """Role: Senior Software Engineering Mentor

Objective:
Transform the following technical prompt into a clear, structured prompt that will produce high-quality code and technical documentation. Focus on:
- Clear problem definition
- Specific technical requirements
- Expected output format
- Code quality standards
- Testing considerations

Original Technical Prompt:
{original_prompt}

Enhanced Technical Prompt:"""


class CoderHelperTool(BaseTool):
    """
    Tool for code-focused prompt refinement and technical explanation.
    
    This tool specializes in improving prompts for coding tasks and providing
    clear explanations of technical concepts. It uses lower temperature settings
    and technical optimization for code-related prompts.
    
    Architectural Constraints:
    - Uses shared AI client for LLM interactions
    - Stateless operations for thread safety
    - No UI framework dependencies
    - Standard BaseTool interface
    """
    
    def __init__(self, ai_client: Optional[AIClient] = None, configuration: Optional[Dict[str, Any]] = None):
        """
        Initialize coder helper tool.
        
        Args:
            ai_client: AI client for making requests
            configuration: Optional tool configuration
        """
        super().__init__(configuration)
        self._ai_client = ai_client
        
        # Default configuration optimized for code tasks
        self._default_config = {
            'model': 'gpt-4',
            'temperature': 0.2,  # Lower temperature for more consistent code output
            'max_tokens': 2000,
            'timeout': 30,
            'explainer_temperature': 0.4,  # Slightly higher for explanations
            'technical_mode': True
        }
        
        # Merge with provided configuration
        self._config = {**self._default_config, **self._configuration}
    
    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name="coder_helper",
            version="1.0.0",
            description="Code-focused prompt refinement and technical explanation tool",
            supported_operations=["refine", "explain", "technical_refine"],
            capabilities=[
                ToolCapability.AI_INTEGRATION,
                ToolCapability.TEXT_PROCESSING,
                ToolCapability.PROMPT_REFINEMENT,
                ToolCapability.CONTENT_GENERATION
            ],
            dependencies=["ai_client"],
            supported_file_types=[".txt", ".md", ".py", ".js", ".java", ".cpp"],
            author="Rebuild Framework"
        )
    
    def validate(self, tool_input: ToolInput) -> bool:
        """
        Validate tool input.
        
        Args:
            tool_input: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Use base validation
        base_errors = self._validate_input(tool_input)
        if base_errors:
            return False
        
        # Check specific requirements
        if tool_input.operation == "refine":
            if "prompt" not in tool_input.parameters:
                return False
        elif tool_input.operation == "explain":
            if "prompt" not in tool_input.parameters:
                return False
        elif tool_input.operation == "technical_refine":
            if "prompt" not in tool_input.parameters:
                return False
        
        # Check AI client availability
        if not self._ai_client:
            return False
        
        return True
    
    def execute(self, tool_input: ToolInput) -> ToolResult:
        """
        Execute coder helper operation.
        
        Args:
            tool_input: Standardized tool input
            
        Returns:
            ToolResult with operation results
        """
        start_time = time.time()
        self._update_status(ToolStatus.RUNNING)
        
        try:
            # Validate input
            if not self.validate(tool_input):
                return create_error_result(
                    errors=["Invalid input for coder helper"],
                    execution_time=time.time() - start_time
                )
            
            # Execute based on operation
            if tool_input.operation == "refine":
                result = self._refine_prompt(tool_input)
            elif tool_input.operation == "explain":
                result = self._explain_prompt(tool_input)
            elif tool_input.operation == "technical_refine":
                result = self._technical_refine(tool_input)
            else:
                return create_error_result(
                    errors=[f"Unsupported operation: {tool_input.operation}"],
                    execution_time=time.time() - start_time
                )
            
            # Add execution time
            result.execution_time = time.time() - start_time
            self._update_status(ToolStatus.SUCCESS if result.status == ToolStatus.SUCCESS else ToolStatus.ERROR)
            
            return result
            
        except Exception as e:
            self._update_status(ToolStatus.ERROR)
            return create_error_result(
                errors=[f"Execution failed: {str(e)}"],
                execution_time=time.time() - start_time
            )
    
    def _refine_prompt(self, tool_input: ToolInput) -> ToolResult:
        """
        Refine a prompt for better clarity and structure.
        
        Args:
            tool_input: Tool input with prompt to refine
            
        Returns:
            ToolResult with refined prompt
        """
        try:
            # Get the original prompt
            original_prompt = tool_input.parameters["prompt"]
            
            # Build the refinement prompt
            final_prompt = CODE_PROMPT_TEMPLATE.format(rough_prompt=original_prompt)
            
            # Create AI request with code-optimized settings
            ai_request = AIRequest(
                request_type=RequestType.CHAT,
                prompt=final_prompt,
                model=tool_input.configuration.get("model", self._config["model"]),
                temperature=tool_input.configuration.get("temperature", self._config["temperature"]),
                max_tokens=tool_input.configuration.get("max_tokens", self._config["max_tokens"])
            )
            
            # Make AI request
            ai_response = self._ai_client.make_request(ai_request)
            
            if not ai_response.success:
                return create_error_result(
                    errors=[f"AI request failed: {ai_response.error_message}"]
                )
            
            refined_prompt = ai_response.content.strip()
            
            return create_success_result(
                output={
                    "original_prompt": original_prompt,
                    "refined_prompt": refined_prompt,
                    "operation": "refine",
                    "model_used": ai_response.model_used,
                    "token_usage": ai_response.usage
                },
                metrics={
                    "response_time": ai_response.response_time,
                    "input_tokens": ai_response.usage.get("prompt_tokens", 0),
                    "output_tokens": ai_response.usage.get("completion_tokens", 0)
                }
            )
            
        except Exception as e:
            return create_error_result(
                errors=[f"Prompt refinement failed: {str(e)}"]
            )
    
    def _explain_prompt(self, tool_input: ToolInput) -> ToolResult:
        """
        Explain a prompt's functionality and purpose.
        
        Args:
            tool_input: Tool input with prompt to explain
            
        Returns:
            ToolResult with prompt explanation
        """
        try:
            # Get the prompt to explain
            prompt_to_explain = tool_input.parameters["prompt"]
            
            # Build the explanation prompt
            final_prompt = EXPLAINER_TEMPLATE.format(prompt_to_analyze=prompt_to_explain)
            
            # Create AI request with slightly higher temperature for explanations
            ai_request = AIRequest(
                request_type=RequestType.CHAT,
                prompt=final_prompt,
                model=tool_input.configuration.get("model", self._config["model"]),
                temperature=tool_input.configuration.get("explainer_temperature", self._config["explainer_temperature"]),
                max_tokens=tool_input.configuration.get("max_tokens", self._config["max_tokens"])
            )
            
            # Make AI request
            ai_response = self._ai_client.make_request(ai_request)
            
            if not ai_response.success:
                return create_error_result(
                    errors=[f"AI request failed: {ai_response.error_message}"]
                )
            
            explanation = ai_response.content.strip()
            
            return create_success_result(
                output={
                    "original_prompt": prompt_to_explain,
                    "explanation": explanation,
                    "operation": "explain",
                    "model_used": ai_response.model_used,
                    "token_usage": ai_response.usage
                },
                metrics={
                    "response_time": ai_response.response_time,
                    "input_tokens": ai_response.usage.get("prompt_tokens", 0),
                    "output_tokens": ai_response.usage.get("completion_tokens", 0)
                }
            )
            
        except Exception as e:
            return create_error_result(
                errors=[f"Prompt explanation failed: {str(e)}"]
            )
    
    def _technical_refine(self, tool_input: ToolInput) -> ToolResult:
        """
        Refine a prompt specifically for technical/coding tasks.
        
        Args:
            tool_input: Tool input with technical prompt to refine
            
        Returns:
            ToolResult with technically-enhanced prompt
        """
        try:
            # Get the original technical prompt
            original_prompt = tool_input.parameters["prompt"]
            
            # Build the technical refinement prompt
            final_prompt = TECHNICAL_REFINEMENT_TEMPLATE.format(original_prompt=original_prompt)
            
            # Create AI request with code-optimized settings
            ai_request = AIRequest(
                request_type=RequestType.CHAT,
                prompt=final_prompt,
                model=tool_input.configuration.get("model", self._config["model"]),
                temperature=tool_input.configuration.get("temperature", self._config["temperature"]),
                max_tokens=tool_input.configuration.get("max_tokens", self._config["max_tokens"])
            )
            
            # Make AI request
            ai_response = self._ai_client.make_request(ai_request)
            
            if not ai_response.success:
                return create_error_result(
                    errors=[f"AI request failed: {ai_response.error_message}"]
                )
            
            technical_prompt = ai_response.content.strip()
            
            return create_success_result(
                output={
                    "original_prompt": original_prompt,
                    "technical_prompt": technical_prompt,
                    "operation": "technical_refine",
                    "model_used": ai_response.model_used,
                    "token_usage": ai_response.usage
                },
                metrics={
                    "response_time": ai_response.response_time,
                    "input_tokens": ai_response.usage.get("prompt_tokens", 0),
                    "output_tokens": ai_response.usage.get("completion_tokens", 0)
                }
            )
            
        except Exception as e:
            return create_error_result(
                errors=[f"Technical refinement failed: {str(e)}"]
            )


# Convenience functions for common operations
def refine_code_prompt(ai_client: AIClient, prompt: str, **kwargs) -> str:
    """
    Convenience function to refine a code-related prompt.
    
    Args:
        ai_client: AI client to use
        prompt: Prompt to refine
        **kwargs: Additional configuration
        
    Returns:
        Refined prompt text
    """
    tool = CoderHelperTool(ai_client=ai_client)
    
    tool_input = ToolInput(
        operation="refine",
        parameters={"prompt": prompt},
        configuration=kwargs
    )
    
    result = tool.execute(tool_input)
    
    if result.status == ToolStatus.SUCCESS:
        return result.output.get("refined_prompt", "")
    else:
        return ""


def explain_code_prompt(ai_client: AIClient, prompt: str, **kwargs) -> str:
    """
    Convenience function to explain a prompt's functionality.
    
    Args:
        ai_client: AI client to use
        prompt: Prompt to explain
        **kwargs: Additional configuration
        
    Returns:
        Explanation text
    """
    tool = CoderHelperTool(ai_client=ai_client)
    
    tool_input = ToolInput(
        operation="explain",
        parameters={"prompt": prompt},
        configuration=kwargs
    )
    
    result = tool.execute(tool_input)
    
    if result.status == ToolStatus.SUCCESS:
        return result.output.get("explanation", "")
    else:
        return ""


def technical_refine_prompt(ai_client: AIClient, prompt: str, **kwargs) -> str:
    """
    Convenience function to technically refine a coding prompt.
    
    Args:
        ai_client: AI client to use
        prompt: Technical prompt to refine
        **kwargs: Additional configuration
        
    Returns:
        Technically refined prompt text
    """
    tool = CoderHelperTool(ai_client=ai_client)
    
    tool_input = ToolInput(
        operation="technical_refine",
        parameters={"prompt": prompt},
        configuration=kwargs
    )
    
    result = tool.execute(tool_input)
    
    if result.status == ToolStatus.SUCCESS:
        return result.output.get("technical_prompt", "")
    else:
        return ""