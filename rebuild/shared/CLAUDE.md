# Shared Layer - Architecture Rules

## Purpose

The shared layer provides common utilities and infrastructure used by all other layers. This is the foundation of the rebuild framework.

## Layer Rules

### Import Rules
**Allowed imports:**
- Standard library modules (typing, dataclasses, enum, logging, pathlib, json, etc.)
- External libraries (openai, anthropic, google.generativeai)
- No imports from core or tools layers

**Forbidden imports:**
- `core.*` - Would create circular dependencies
- `tools.*` - Would violate dependency direction
- `main` - Shared utilities must not depend on application entry point

### Responsibility Patterns

Modules in the shared layer handle:
- Common utility functions
- AI client interfaces
- Data validation and formatting
- File operations
- Configuration management
- Security and sanitization

## Module Patterns

### #utility-patterns
Utility modules characteristics:
- Pure functions with no side effects
- Input validation and sanitization
- Consistent error handling
- Thread-safe implementations
- Comprehensive type hints

Example utilities:
- `validate_file_path()` - Validates file paths
- `sanitize_input()` - Cleans user input
- `format_output()` - Standardizes output format
- `calculate_metrics()` - Computes performance metrics

### #ai-client-patterns
AI client modules provide:
- Provider-agnostic interfaces
- Retry logic with exponential backoff
- Rate limiting
- Request/response formatting
- Error handling and fallbacks

Standard AI client interface:
```python
class AIClient:
    def make_request(prompt: str, **kwargs) -> str
    def parse_response(response: Any) -> Dict
    def handle_error(error: Exception) -> str
```

### #security-patterns
Security considerations:
- API key management through environment/secrets
- Input sanitization to prevent injection
- Path validation to prevent directory traversal
- Rate limiting to prevent abuse
- Secure error messages (no sensitive data)

### #performance-patterns
Performance optimizations:
- Minimal overhead in utility functions
- Efficient string operations
- Lazy loading where appropriate
- Caching for expensive operations
- Async support where beneficial

## Common Interfaces

### Error Handling
```python
class SharedError(Exception):
    """Base exception for shared layer"""
    pass

class ValidationError(SharedError):
    """Input validation failed"""
    pass

class APIError(SharedError):
    """External API call failed"""
    pass
```

### Result Types
```python
@dataclass
class Result:
    success: bool
    data: Optional[Any]
    error: Optional[str]
```

## Anti-Patterns to Avoid

1. **State Management**: Shared utilities should be stateless
2. **Business Logic**: Keep business logic in core layer
3. **UI Concerns**: No UI/presentation logic
4. **Direct Tool References**: Never reference specific tools

## Thread Safety

All shared utilities must be thread-safe:
- No global mutable state
- Use thread-local storage if needed
- Immutable data structures preferred
- Document any thread-safety constraints

## Testing Guidelines

Shared layer modules require:
- Unit tests for all public functions
- Edge case coverage
- Error condition testing
- Performance benchmarks for critical paths
- Mock external dependencies

## File Organization

```
shared/
├── __init__.py         # Public API exports
├── ai_client.py        # AI provider interfaces
├── utils.py            # Common utilities
└── CLAUDE.md          # This file
```

## Quick Reference

When working in shared layer:
1. Check imports - no core/tools imports allowed
2. Keep functions pure and stateless
3. Validate all inputs
4. Handle errors gracefully
5. Document thread-safety guarantees
6. Export public API through __init__.py