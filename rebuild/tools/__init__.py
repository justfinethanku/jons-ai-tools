"""
@RULE:LAYER: tools/__init__
@RULE:FORBIDDEN: core.*, main
@SEE: tools/CLAUDE.md#tool-interface-standards
Tools package initialization and public API export
"""

from .base_tool import (
    BaseTool, ToolMetadata, ToolInput, ToolResult, ToolStatus,
    ToolCapability, ExecutionContext, 
    create_tool_input, create_success_result, create_error_result
)

__version__ = "1.0.0"

__all__ = [
    "BaseTool",
    "ToolMetadata", 
    "ToolInput",
    "ToolResult",
    "ToolStatus",
    "ToolCapability",
    "ExecutionContext",
    "create_tool_input",
    "create_success_result", 
    "create_error_result",
    "__version__"
]