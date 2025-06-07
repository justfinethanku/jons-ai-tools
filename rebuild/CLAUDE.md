# Rebuild Framework - Architecture Rules

## Overview

This document defines the architectural rules and patterns for the rebuild framework. All code in this project follows a **comment-driven architecture** where rules guide development and maintain consistency.

## How to Use This Document

1. **Before writing code**: Check the relevant layer's CLAUDE.md
2. **In code files**: Look for `@SEE:` references pointing to specific sections
3. **When adding features**: Follow the patterns defined here
4. **For violations**: Understand the rationale before requesting exceptions

## Architecture Layers

```
┌─────────────────────────────────────┐
│           TOOLS LAYER               │
│  User-facing tools implementing     │
│  BaseTool interface                 │
├─────────────────────────────────────┤
│            CORE LAYER               │
│  Business logic and rule processing │
├─────────────────────────────────────┤
│           SHARED LAYER              │
│  Common utilities and AI clients    │
└─────────────────────────────────────┘
```

## Dependency Flow Rules

**CRITICAL**: Dependencies flow downward only. Never upward or sideways.

- `tools` → can import from `shared` and `core`
- `core` → can import from `shared` only
- `shared` → cannot import from `tools` or `core`

## Universal Rules

These rules apply to **ALL** files in the rebuild framework:

### 1. Purpose and Responsibility
- Every file has ONE clear purpose
- Single Responsibility Principle strictly enforced
- No "kitchen sink" modules

### 2. Import Rules
- **ALWAYS FORBIDDEN**: 
  - Circular imports
  - Cross-layer imports (e.g., shared importing from core)
  - Direct main.py imports from any module
  
### 3. API Design
- Clear separation between public API and private implementation
- Public functions/classes explicitly documented
- Private functions prefixed with underscore

### 4. Interface Patterns
- Consistent interfaces within each layer
- Standardized input/output structures
- Error handling follows layer conventions

### 5. No Cross-Talk Rule
- Modules at the same level don't directly communicate
- Communication happens through defined interfaces
- Use dependency injection for flexibility

## Quick Start for New Files

When creating a new file:

```python
"""
@RULE:LAYER: [shared|core|tools]/module_name
@RULE:FORBIDDEN: [specific forbidden imports]
@SEE: [layer]/CLAUDE.md#relevant-section
Brief description of module purpose
"""
```

## Rule Categories

### Structural Rules
- `PURPOSE`: Single sentence describing why this file exists
- `RESPONSIBILITY`: Detailed list of what this file handles
- `ONE_PURPOSE`: Reinforcement of single responsibility

### Import Management
- `IMPORTS_ALLOWED`: Explicit whitelist of allowed imports
- `IMPORTS_FORBIDDEN`: Blacklist of forbidden imports
- `DEPENDENCY_DIRECTION`: How this module fits in the flow

### Interface Design
- `PUBLIC_API`: List of public functions/classes
- `PRIVATE_IMPL`: List of private implementations
- `INTERFACE_RULE`: Specific interface constraints

### Operational Rules
- `NO_CROSS_TALK`: Isolation requirements
- `THREAD_SAFETY`: Concurrency considerations
- `STATELESS`: State management rules

## Validation Checklist

Before committing code, ensure:

- [ ] File has `@RULE:LAYER` declaration
- [ ] Critical forbidden imports listed in `@RULE:FORBIDDEN`
- [ ] `@SEE:` reference points to relevant CLAUDE.md section
- [ ] No upward or cross-layer dependencies
- [ ] Single responsibility maintained
- [ ] Public API clearly defined

## Rationale

This architecture ensures:
1. **Maintainability**: Clear boundaries prevent spaghetti code
2. **Testability**: Isolated modules are easier to test
3. **Scalability**: New tools can be added without affecting core
4. **Clarity**: Developers immediately understand module purpose
5. **Safety**: Architectural violations are caught early

For layer-specific patterns, see:
- [shared/CLAUDE.md](shared/CLAUDE.md) - Shared utilities patterns
- [core/CLAUDE.md](core/CLAUDE.md) - Core layer patterns  
- [tools/CLAUDE.md](tools/CLAUDE.md) - Tools layer patterns