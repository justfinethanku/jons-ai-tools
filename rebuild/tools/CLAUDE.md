# Tools Layer - Architecture Rules

## Purpose

The tools layer contains user-facing tools that implement specific functionality. All tools follow the BaseTool interface and leverage core and shared layers.

## Layer Rules

### Import Rules
**Allowed imports:**
- Standard library modules
- Shared layer modules (`shared.*`)
- Core layer modules (`core.*`)
- Base tool interface (`.base_tool`)

**Forbidden imports:**
- Other tools (no cross-tool dependencies)
- `main` - Tools are invoked, don't invoke
- UI frameworks directly (Streamlit, Flask, etc.)

### Responsibility Patterns

Tools handle:
- Specific user operations (refine, generate, analyze)
- Input validation for tool-specific needs
- Output formatting for tool-specific formats
- Integration with AI through shared layer
- Metrics collection and reporting

## Tool Patterns

### #base-tool-patterns
All tools must:
- Inherit from `BaseTool` abstract class
- Implement required methods
- Follow standardized lifecycle
- Return standardized results
- Handle errors consistently

Required methods:
```python
class MyTool(BaseTool):
    def get_metadata() -> ToolMetadata
    def execute(input: ToolInput) -> ToolResult
    def validate(input: ToolInput) -> bool
```

### #tool-lifecycle
Standard tool execution flow:
1. Validate input
2. Update status to RUNNING
3. Execute operation
4. Collect metrics
5. Format output
6. Return result
7. Update status to SUCCESS/ERROR

### #ai-integration-patterns
Tools integrate with AI through:
- Shared AI client (never direct)
- Standardized prompts
- Response validation
- Error handling
- Retry logic

Example:
```python
from shared.ai_client import AIClient

client = AIClient()
response = client.make_request(prompt, temperature=0.7)
```

### #stateless-patterns
Tools must be stateless:
- No instance variables for user data
- All state in ToolInput/ToolResult
- Thread-safe execution
- Concurrent execution support
- No global variables

## Common Tool Types

### Refinement Tools
- Take input, return improved version
- Iterative improvement support
- Version tracking
- Diff generation

### Generation Tools
- Create new content from specifications
- Multiple output formats
- Template support
- Customization options

### Analysis Tools
- Examine input, return insights
- Metrics calculation
- Pattern detection
- Recommendation generation

## Tool Interface Standards

### Input Structure
```python
@dataclass
class ToolInput:
    operation: str              # What to do
    parameters: Dict[str, Any]  # How to do it
    context: Dict[str, Any]     # Additional context
    configuration: Dict[str, Any] # Tool config
```

### Output Structure
```python
@dataclass
class ToolResult:
    status: ToolStatus
    output: Dict[str, Any]     # Main results
    metrics: Dict[str, float]  # Performance metrics
    errors: List[str]          # Any errors
    warnings: List[str]        # Any warnings
```

### Metadata Structure
```python
@dataclass
class ToolMetadata:
    name: str
    version: str
    description: str
    supported_operations: List[str]
    capabilities: List[ToolCapability]
```

## Error Handling

Tools should handle errors gracefully:
```python
try:
    result = perform_operation()
except ValidationError as e:
    return create_error_result([f"Validation failed: {e}"])
except APIError as e:
    return create_error_result([f"API error: {e}"])
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return create_error_result(["An unexpected error occurred"])
```

## Performance Considerations

- Minimize AI calls (batch when possible)
- Cache results where appropriate
- Stream large outputs
- Provide progress indicators
- Set reasonable timeouts

## Testing Requirements

Tool tests should cover:
- All supported operations
- Error conditions
- Edge cases
- Performance benchmarks
- Integration with AI client
- Concurrent execution

## Adding a New Tool

1. Create new file in tools/
2. Import BaseTool
3. Implement required methods
4. Add to tools/__init__.py
5. Write comprehensive tests
6. Document supported operations

Template:
```python
"""
@RULE:LAYER: tools/my_new_tool
@RULE:FORBIDDEN: other tools, main, UI frameworks
@SEE: tools/CLAUDE.md#base-tool-patterns
New tool for specific purpose
"""

from .base_tool import BaseTool, ToolMetadata, ToolResult
from shared.ai_client import AIClient

class MyNewTool(BaseTool):
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="my_new_tool",
            version="1.0.0",
            description="Does something useful",
            supported_operations=["operation1", "operation2"]
        )
    
    def execute(self, tool_input: ToolInput) -> ToolResult:
        # Implementation
        pass
    
    def validate(self, tool_input: ToolInput) -> bool:
        # Validation logic
        pass
```

## File Organization

```
tools/
├── __init__.py         # Tool exports and registration
├── base_tool.py        # BaseTool interface
├── prompt_refiner.py   # Prompt refinement tool
├── social_copy_tool.py # Social media copy generator
├── coder_helper.py     # Code-focused helper
└── CLAUDE.md          # This file
```

## Quick Reference

When creating tools:
1. Inherit from BaseTool
2. Keep tools stateless
3. Use shared AI client
4. Validate all inputs
5. Return standardized results
6. Handle errors gracefully
7. Write comprehensive tests
8. Document operations clearly