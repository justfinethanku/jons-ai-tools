"""
@RULE:PURPOSE: Prompt refiner tool package initialization and public API exposure
@RULE:RESPONSIBILITY: Tool package setup, public API definition, version management, module exports
@RULE:IMPORTS_ALLOWED: .tool, .ui, typing
@RULE:IMPORTS_FORBIDDEN: core.*, main, other tools, original framework modules
@RULE:PUBLIC_API: PromptRefinerTool, create_prompt_refiner, __version__
@RULE:PRIVATE_IMPL: package initialization, module imports
@RULE:NO_CROSS_TALK: other tools, main application, original framework
@RULE:DEPENDENCY_DIRECTION: prompt_refiner package -> tool and ui modules only
@RULE:INTERFACE_RULE: Clean package interface exposing only public tool API
@RULE:ONE_PURPOSE: Single responsibility is prompt refiner tool package management
@RULE:VERSIONING: Semantic versioning for tool releases
"""

# Package version
__version__ = "1.0.0"

# Public API imports
# from .tool import PromptRefinerTool
# from .ui import create_prompt_refiner_ui

# Public API definition
__all__ = [
    "PromptRefinerTool",
    "create_prompt_refiner_ui", 
    "__version__"
]


def create_prompt_refiner(configuration=None):
    """
    Factory function to create prompt refiner tool instance.
    
    Args:
        configuration: Optional tool configuration
        
    Returns:
        PromptRefinerTool instance
    """
    # from .tool import PromptRefinerTool
    # return PromptRefinerTool(configuration)
    pass