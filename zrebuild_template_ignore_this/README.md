# Rule-Based Architecture Template

This template provides the complete structure and patterns for implementing rule-based architecture projects with comprehensive rules, file organization, and development practices.

## Key Features & Rules Implemented

### 📁 **File Organization Rules**

**@RULE:DOCUMENTATION_LOCATION**: All documentation goes in `docs/` directory - never in project root

**@RULE:TEST_ORGANIZATION**: Tests organized by lifecycle - active tests in main directory, obsolete tests in `tests/obsolete/`

**@RULE:PROMPT_MANAGEMENT**: Tools use file-based prompts stored in `{tool}/prompts/` directories

**@RULE:NO_CLUTTER**: Keep project root clean - documentation, tests, and temporary files properly organized

### 🏗️ **Architecture Patterns**

#### Tool Structure
Each tool follows the standardized pattern:
```
tools/
├── tool_name/
│   ├── __init__.py          # Package initialization with factory function
│   ├── tool.py              # Core business logic with rule compliance
│   ├── ui.py                # UI components with clean separation
│   └── prompts/             # File-based prompts for AI operations
│       ├── operation1.txt
│       └── operation2.txt
```

#### Rule-Based Development
- **@RULE:PURPOSE**: Every file has clear single responsibility
- **@RULE:IMPORTS_ALLOWED/FORBIDDEN**: Strict dependency control
- **@RULE:DEPENDENCY_DIRECTION**: Clean architectural layers
- **@RULE:NO_CROSS_TALK**: Modules don't cross-communicate
- **@RULE:INTERFACE_RULE**: Standardized interfaces between components

### 🔧 **Implementation Patterns**

#### Prompt Loading Pattern
```python
def _load_prompt_file(self, prompt_name: str) -> str:
    """Load prompt from file in prompts/ directory."""
    prompt_path = Path(__file__).parent / "prompts" / f"{prompt_name}.txt"
    return prompt_path.read_text(encoding='utf-8')
```

#### Tool Interface Pattern
```python
class YourTool(BaseTool):
    def execute(self, tool_input: ToolInput) -> ToolResult:
        # Standardized execution pattern
    
    def validate(self, tool_input: ToolInput) -> bool:
        # Input validation
    
    def get_metadata(self) -> ToolMetadata:
        # Tool description and capabilities
```

#### Configuration Pattern
```python
def __init__(self, configuration: Optional[Dict[str, Any]] = None):
    # Merge defaults with provided configuration
    self._default_config = {...}
    self._configuration.update(self._default_config)
    if configuration:
        self._configuration.update(configuration)
```

## Directory Structure

```
project/
├── core/                    # Core architecture modules
│   ├── llm_integrator.py   # AI client integration
│   ├── rule_engine.py      # Rule management and validation
│   └── rule_parser.py      # Rule extraction from comments
├── shared/                  # Shared utilities
│   ├── ai_client.py        # Multi-provider AI client
│   └── utils.py            # Common utility functions
├── tools/                   # Tool implementations
│   ├── base_tool.py        # Abstract base tool interface
│   └── example_tool/       # Example tool following all patterns
│       ├── __init__.py     # Factory function and public API
│       ├── tool.py         # Core business logic
│       ├── ui.py           # UI components
│       └── prompts/        # File-based prompt templates
├── tests/                   # Test organization
│   ├── README.md           # Test organization rules
│   ├── test_*.py           # Active tests for ongoing development
│   └── obsolete/           # Completed migration/validation tests
├── docs/                    # All documentation
│   └── README.md           # Documentation rules and structure
└── main.py                 # Application entry point
```

## Development Guidelines

### Creating New Tools

1. **Follow the Pattern**: Use `tools/example_tool/` as template
2. **Add Rule Comments**: Every file must have comprehensive `@RULE:` comments
3. **Implement BaseTool**: Inherit from `BaseTool` and implement all abstract methods
4. **File-Based Prompts**: Store prompts in `prompts/` directory, not hardcoded
5. **Clean Separation**: UI in `ui.py`, business logic in `tool.py`
6. **Factory Function**: Provide clean initialization in `__init__.py`

### Rule Compliance

Every file must include these core rules:
- `@RULE:PURPOSE` - Single responsibility definition
- `@RULE:RESPONSIBILITY` - Specific duties and capabilities
- `@RULE:IMPORTS_ALLOWED` - Permitted dependencies
- `@RULE:IMPORTS_FORBIDDEN` - Banned dependencies
- `@RULE:PUBLIC_API` - Exposed interface methods
- `@RULE:PRIVATE_IMPL` - Internal implementation details
- `@RULE:NO_CROSS_TALK` - Isolation requirements
- `@RULE:DEPENDENCY_DIRECTION` - Allowed dependency flow

### Test Organization

**Active Tests** (main `tests/` directory):
- Core architecture functionality
- Ongoing development features
- CI/CD pipeline tests

**Obsolete Tests** (`tests/obsolete/`):
- Completed migration validations
- One-time refactoring tests
- Historical reference tests

### Documentation Standards

**Location**: All docs in `docs/` directory
**Naming**: 
- Summaries: `{FEATURE}_SUMMARY.md`
- Guides: `{FEATURE}_GUIDE.md`
- Architecture: `{COMPONENT}_ARCHITECTURE.md`

## Benefits of This Template

✅ **Clean Architecture**: Enforced separation of concerns and dependencies
✅ **Scalable Structure**: Easy to add new tools and features
✅ **Maintainable Code**: Clear rules and patterns for consistency
✅ **Testable Design**: Organized testing with lifecycle management
✅ **Documentation**: Built-in documentation organization
✅ **Prompt Management**: Easy editing and version control of AI prompts
✅ **Rule Compliance**: Automatic architectural constraint validation

## Getting Started

1. Copy this template to your project directory
2. Update `main.py` with your application logic
3. Implement core modules (`core/` directory)
4. Create tools following the example pattern
5. Add tests following the organization rules
6. Document your features in `docs/`

This template embodies all the patterns and rules developed through practical implementation and provides a solid foundation for rule-based architecture projects.