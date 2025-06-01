"""
@RULE:PURPOSE: Social copy tool package initialization and public API exposure for social media content generation
@RULE:RESPONSIBILITY: Tool package setup, public API definition, version management, module exports, social media platform interface
@RULE:IMPORTS_ALLOWED: .tool, .ui, typing
@RULE:IMPORTS_FORBIDDEN: core.*, main, other tools, original framework modules, universal_framework, streamlit
@RULE:PUBLIC_API: SocialCopyTool, create_social_copy_tool, create_social_copy_ui, __version__
@RULE:PRIVATE_IMPL: package initialization, module imports
@RULE:NO_CROSS_TALK: other tools, main application, original framework
@RULE:DEPENDENCY_DIRECTION: social_copy_tool package -> tool and ui modules only
@RULE:INTERFACE_RULE: Clean package interface exposing only public tool API
@RULE:ONE_PURPOSE: Single responsibility is social copy tool package management
@RULE:VERSIONING: Semantic versioning for tool releases
@RULE:SOCIAL_MEDIA_FOCUS: Specialized tool for social media content creation across platforms
@RULE:PLATFORM_SUPPORT: Multi-platform social media copy generation
"""

# Package version
__version__ = "1.0.0"

# Public API imports
# from .tool import SocialCopyTool
# from .ui import create_social_copy_ui

# Public API definition
__all__ = [
    "SocialCopyTool",
    "create_social_copy_ui", 
    "create_social_copy_tool",
    "__version__"
]


def create_social_copy_tool(configuration=None):
    """
    Factory function to create social copy tool instance.
    
    Args:
        configuration: Optional tool configuration
        
    Returns:
        SocialCopyTool instance
    """
    # from .tool import SocialCopyTool
    # return SocialCopyTool(configuration)
    pass