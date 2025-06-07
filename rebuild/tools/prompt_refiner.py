"""
@RULE:LAYER: tools/prompt_refiner
@RULE:FORBIDDEN: core.*, main, streamlit, frameworks.*
@SEE: tools/CLAUDE.md#base-tool-patterns
AI-powered prompt refinement and improvement tool
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


# Built-in meta prompt for prompt refinement
META_PROMPT = """# Role & Objective  
You are a Prompt Refinement Assistant. Your mission is to analyze a given prompt and rewrite it as a clear, powerful version optimized for AI.

# Instructions  
1. Analyze  
   • Identify the prompts intent, goals, target audience, and assumptions.  
2. Apply Best Practices    
   • Assign a role (e.g., Expert Data Analyst).  
   • Define output format, style, and length.  
   • Break complex requests into logical subtasks.  
   • Use chain-of-thought to outline your reasoning.  
   • Add examples or few-shot templates when helpful.  
3. Output  
   • **Analysis:** 1 or 2 sentence summary of your findings.  
   • **Refined Prompt:** The rewritten, optimized prompt text.

# Note  
The given prompt to refine is included below inside [ ] brackets.

# Output Format  
Analysis: <your 1 or 2 sentence summary>


Refined Prompt:
# Example  
**Original:** "Summarize climate change."  
**Analysis:** The user wants a concise, expert overview of climate change for non-specialists.  
**Refined Prompt:**  
Role: Environmental Scientist  
Objective: Provide a 300-word summary of climate change.  
Instructions:  
• Cover natural and human drivers.  
• Explain key environmental and societal impacts.  
• Suggest two actionable mitigation strategies.  
Format: Three paragraphs, max 100 words each."""

# Built-in revision prompt for prompt iterations
REVISION_PROMPT = """You are an expert prompt engineer specializing in prompt revisions.

Your task: Modify the current prompt based on the user's specific feedback, keeping what works well and improving only what they've requested.

CURRENT PROMPT:
{current_prompt}

USER'S REVISION REQUEST:
{revision_request}

INSTRUCTIONS:
- Keep the core structure and good elements
- Focus only on the specific changes requested
- Don't over-engineer - make targeted improvements
- Maintain the original intent while incorporating the feedback
- Return ONLY the revised prompt, no explanation

REVISED PROMPT:"""


class PromptRefinerTool(BaseTool):
    """
    Tool for refining and improving prompts using AI assistance.
    
    This tool takes rough or basic prompts and uses AI to analyze them
    and create improved, more effective versions. It supports iterative
    refinement through revision requests.
    
    Architectural Constraints:
    - Uses shared AI client for LLM interactions
    - Stateless operations for thread safety
    - No UI framework dependencies
    - Standard BaseTool interface
    """
    
    def __init__(self, ai_client: Optional[AIClient] = None, configuration: Optional[Dict[str, Any]] = None):
        """
        Initialize prompt refiner tool.
        
        Args:
            ai_client: AI client for making refinement requests
            configuration: Optional tool configuration
        """
        super().__init__(configuration)
        self._ai_client = ai_client
        
        # Default configuration
        self._default_config = {
            'model': 'gpt-4',
            'temperature': 0.3,
            'max_tokens': 2000,
            'timeout': 30
        }
        
        # Merge with provided configuration
        self._config = {**self._default_config, **self._configuration}
    
    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name="prompt_refiner",
            version="1.0.0",
            description="AI-powered prompt refinement and improvement tool",
            supported_operations=["refine", "revise", "analyze"],
            capabilities=[
                ToolCapability.AI_INTEGRATION,
                ToolCapability.TEXT_PROCESSING,
                ToolCapability.PROMPT_REFINEMENT,
                ToolCapability.CONTENT_GENERATION
            ],
            dependencies=["ai_client"],
            supported_file_types=[".txt", ".md"],
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
        elif tool_input.operation == "revise":
            if "current_prompt" not in tool_input.parameters or "revision_request" not in tool_input.parameters:
                return False
        elif tool_input.operation == "analyze":
            if "prompt" not in tool_input.parameters:
                return False
        
        # Check AI client availability
        if not self._ai_client:
            return False
        
        return True
    
    def execute(self, tool_input: ToolInput) -> ToolResult:
        """
        Execute prompt refinement operation.
        
        Args:
            tool_input: Standardized tool input
            
        Returns:
            ToolResult with refinement results
        """
        start_time = time.time()
        self._update_status(ToolStatus.RUNNING)
        
        try:
            # Validate input
            if not self.validate(tool_input):
                return create_error_result(
                    errors=["Invalid input for prompt refinement"],
                    execution_time=time.time() - start_time
                )
            
            # Execute based on operation
            if tool_input.operation == "refine":
                result = self._refine_prompt(tool_input)
            elif tool_input.operation == "revise":
                result = self._revise_prompt(tool_input)
            elif tool_input.operation == "analyze":
                result = self._analyze_prompt(tool_input)
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
        Refine a prompt using AI analysis and improvement.
        
        Args:
            tool_input: Tool input with prompt to refine
            
        Returns:
            ToolResult with refined prompt
        """
        try:
            # Get the rough prompt
            rough_prompt = tool_input.parameters["prompt"]
            
            # Build the refinement prompt
            final_prompt = f"{META_PROMPT}\n\n[ {rough_prompt} ]"
            
            # Create AI request
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
            
            # Parse the response
            refined_content = ai_response.content.strip()
            
            # Extract analysis and refined prompt if structured response
            analysis = ""
            refined_prompt = refined_content
            
            if "Analysis:" in refined_content and "Refined Prompt:" in refined_content:
                parts = refined_content.split("Refined Prompt:", 1)
                if len(parts) == 2:
                    analysis_part = parts[0].replace("Analysis:", "").strip()
                    refined_prompt = parts[1].strip()
                    analysis = analysis_part
            
            return create_success_result(
                output={
                    "original_prompt": rough_prompt,
                    "refined_prompt": refined_prompt,
                    "analysis": analysis,
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
    
    def _revise_prompt(self, tool_input: ToolInput) -> ToolResult:
        """
        Revise a prompt based on user feedback.
        
        Args:
            tool_input: Tool input with current prompt and revision request
            
        Returns:
            ToolResult with revised prompt
        """
        try:
            # Get parameters
            current_prompt = tool_input.parameters["current_prompt"]
            revision_request = tool_input.parameters["revision_request"]
            
            # Build the revision prompt
            final_prompt = REVISION_PROMPT.format(
                current_prompt=current_prompt,
                revision_request=revision_request
            )
            
            # Create AI request
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
            
            revised_prompt = ai_response.content.strip()
            
            return create_success_result(
                output={
                    "original_prompt": current_prompt,
                    "revision_request": revision_request,
                    "revised_prompt": revised_prompt,
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
                errors=[f"Prompt revision failed: {str(e)}"]
            )
    
    def _analyze_prompt(self, tool_input: ToolInput) -> ToolResult:
        """
        Analyze a prompt without refinement.
        
        Args:
            tool_input: Tool input with prompt to analyze
            
        Returns:
            ToolResult with prompt analysis
        """
        try:
            prompt = tool_input.parameters["prompt"]
            
            # Simple analysis prompt
            analysis_prompt = f"""Analyze the following prompt and provide:
1. Intent and goals
2. Strengths and weaknesses  
3. Improvement suggestions

Prompt to analyze:
{prompt}

Provide a structured analysis."""
            
            # Create AI request
            ai_request = AIRequest(
                request_type=RequestType.CHAT,
                prompt=analysis_prompt,
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
            
            return create_success_result(
                output={
                    "original_prompt": prompt,
                    "analysis": ai_response.content.strip(),
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
                errors=[f"Prompt analysis failed: {str(e)}"]
            )


# Convenience functions for common operations
def refine_prompt(ai_client: AIClient, prompt: str, **kwargs) -> str:
    """
    Convenience function to refine a prompt.
    
    Args:
        ai_client: AI client to use
        prompt: Prompt to refine
        **kwargs: Additional configuration
        
    Returns:
        Refined prompt text
    """
    tool = PromptRefinerTool(ai_client=ai_client)
    
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


def revise_prompt(ai_client: AIClient, current_prompt: str, revision_request: str, **kwargs) -> str:
    """
    Convenience function to revise a prompt.
    
    Args:
        ai_client: AI client to use
        current_prompt: Current prompt to revise
        revision_request: Revision instructions
        **kwargs: Additional configuration
        
    Returns:
        Revised prompt text
    """
    tool = PromptRefinerTool(ai_client=ai_client)
    
    tool_input = ToolInput(
        operation="revise",
        parameters={
            "current_prompt": current_prompt,
            "revision_request": revision_request
        },
        configuration=kwargs
    )
    
    result = tool.execute(tool_input)
    
    if result.status == ToolStatus.SUCCESS:
        return result.output.get("revised_prompt", "")
    else:
        return ""