# Core Layer - Architecture Rules

## Purpose

The core layer contains the business logic and rule processing engine that drives the rebuild framework. This layer orchestrates the comment-driven development system.

## Layer Rules

### Import Rules
**Allowed imports:**
- Standard library modules
- Shared layer modules (`shared.*`)
- Other core modules within the same layer

**Forbidden imports:**
- `tools.*` - Tools depend on core, not vice versa
- `main` - Core provides services, doesn't depend on entry point
- External AI libraries directly (use shared.ai_client instead)

### Responsibility Patterns

Core modules handle:
- Rule parsing and validation
- Rule engine and enforcement
- LLM prompt generation from rules
- Code analysis and validation
- Execution environment management
- Architectural compliance checking

## Module Patterns

### #rule-engine-patterns
Rule engine characteristics:
- Rule storage and retrieval
- Conflict detection
- Hierarchy management
- Compliance evaluation
- Transactional operations

Key interfaces:
```python
class RuleEngine:
    def register_rule(rule: ArchitecturalRule) -> bool
    def evaluate_compliance(code: str) -> ComplianceResult
    def detect_conflicts(rules: List[Rule]) -> List[Conflict]
```

### #llm-integration-patterns
LLM integration provides:
- Rule-to-prompt conversion
- Context window management
- Response validation
- Iterative refinement
- Multi-provider support through shared layer

Standard pattern:
```python
class LLMIntegrator:
    def generate_prompt(rules: List[Rule]) -> str
    def validate_response(response: str) -> ValidationResult
    def refine_with_feedback(response: str, feedback: str) -> str
```

### #persistence-patterns
Persistence requirements:
- ACID compliance for rule storage
- Thread-safe database operations
- Migration support
- Backup and recovery
- Query optimization

### #validation-patterns
Validation includes:
- Syntax validation (AST parsing)
- Semantic validation (rule compliance)
- Dependency validation
- Security validation
- Performance validation

## Common Interfaces

### Rule Types
```python
@dataclass
class ArchitecturalRule:
    name: str
    category: RuleCategory
    scope: RuleScope
    constraints: List[Constraint]
    rationale: str

class RuleCategory(Enum):
    IMPORT = auto()
    INTERFACE = auto()
    DEPENDENCY = auto()
    SECURITY = auto()
```

### Result Types
```python
@dataclass
class ComplianceResult:
    compliant: bool
    violations: List[Violation]
    suggestions: List[str]
    confidence: float
```

## Processing Patterns

### #rule-processing-flow
1. Parse rules from comments/files
2. Validate rule syntax and semantics
3. Check for conflicts
4. Store in rule engine
5. Generate prompts for LLM
6. Validate generated code
7. Iteratively refine

### #context-management
Context window optimization:
- Track token usage
- Prioritize relevant rules
- Compress when needed
- Maintain coherence
- Handle overflow gracefully

## Thread Safety

Core modules ensure thread safety through:
- Read-write locks for rule engine
- Connection pooling for database
- Immutable rule objects
- Thread-local LLM contexts
- Atomic operations

## Error Handling

Core layer errors:
```python
class CoreError(Exception):
    """Base exception for core layer"""
    pass

class RuleError(CoreError):
    """Rule processing failed"""
    pass

class ValidationError(CoreError):
    """Validation failed"""
    pass

class ComplianceError(CoreError):
    """Compliance check failed"""
    pass
```

## State Management

Unlike shared layer, core modules may maintain state:
- Rule repository state
- Execution context
- Compliance history
- Performance metrics

State must be:
- Thread-safe
- Persistent where needed
- Cleanly isolated
- Well-documented

## Integration Points

Core layer provides services to:
- **Tools layer**: Through defined interfaces
- **Main application**: Through execution environment
- **External systems**: Through standardized APIs

## Testing Requirements

Core modules need:
- Integration tests with shared layer
- Rule processing tests
- Compliance validation tests
- Performance tests
- Concurrency tests

## File Organization

```
core/
├── __init__.py             # Public API exports
├── rule_parser.py          # Parse rules from comments
├── rule_engine.py          # Rule storage and enforcement
├── llm_integrator.py       # LLM interaction for rules
├── code_analyzer.py        # Analyze code for compliance
├── execution_environment.py # Manage execution context
└── CLAUDE.md              # This file
```

## Quick Reference

When working in core layer:
1. Import from shared, not tools
2. Provide clean interfaces for tools
3. Maintain thread safety
4. Handle state carefully
5. Validate all inputs/outputs
6. Document complex algorithms