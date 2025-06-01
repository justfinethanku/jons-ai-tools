"""
@RULE:PURPOSE: Example tool package initialization with rule-based architecture
@RULE:RESPONSIBILITY: Tool package setup, public API definition, factory function
@RULE:IMPORTS_ALLOWED: typing, .tool
@RULE:IMPORTS_FORBIDDEN: ..base_tool, ...core.*, ...shared.*, main
@RULE:PUBLIC_API: create_example_tool, ExampleTool
@RULE:PRIVATE_IMPL: None (package initialization only)
@RULE:NO_CROSS_TALK: other tools, core modules, main application
@RULE:DEPENDENCY_DIRECTION: __init__ -> tool module only
@RULE:INTERFACE_RULE: Clean package interface with factory function
@RULE:ONE_PURPOSE: Single responsibility is tool package initialization
@RULE:PROMPT_MANAGEMENT: Tool uses file-based prompts from prompts/ directory
"""

# Allowed imports - tool module only
# from typing import Dict, Any, Optional
# from .tool import ExampleTool


def create_example_tool(configuration: Optional[Dict[str, Any]] = None) -> ExampleTool:
    """
    Factory function to create and configure example tool.
    
    Args:
        configuration: Optional tool configuration parameters
        
    Returns:
        Configured ExampleTool instance
    """
    # return ExampleTool(configuration)
    pass


# Public API exports
__all__ = ["create_example_tool", "ExampleTool"]