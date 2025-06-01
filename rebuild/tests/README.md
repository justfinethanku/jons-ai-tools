# Tests Directory

## Rules for Test Organization

**@RULE:TEST_ORGANIZATION**: All tests must be properly categorized and organized according to their purpose and lifecycle.

**@RULE:ACTIVE_TESTS_ONLY**: Only tests that are needed for ongoing development should remain in the main `tests/` directory.

**@RULE:OBSOLETE_SEPARATION**: Tests that are no longer needed for ongoing development MUST be moved to `tests/obsolete/` with documentation explaining why they're obsolete.

**@RULE:TEST_LIFECYCLE**: When creating tests, consider their lifecycle:
- **Permanent**: Core architecture functionality tests (keep in main tests/)
- **Temporary**: One-time migration/validation tests (move to obsolete/ when complete)
- **Historical**: Tests that served their purpose but provide reference value (obsolete/)

**@RULE:NO_CLUTTER**: Do NOT leave outdated, unused, or one-time validation tests cluttering the main tests directory.

## Current Test Categories

### Active Tests (Main Directory)
Tests that are part of ongoing development and CI/CD:

- **`test_integration.py`** - End-to-end integration tests for rule-based architecture
- **`test_rule_engine.py`** - Core rule engine functionality tests
- **`test_rule_parser.py`** - Core rule parser functionality tests

### Obsolete Tests (obsolete/ Directory)
Tests that served their purpose but are preserved for reference:

- Migration validation tests (all completed)
- One-time refactoring validation tests
- Historical functionality tests

## Test Naming Conventions

**@RULE:TEST_NAMING**: Follow consistent naming patterns:
- **Core functionality**: `test_{component}.py` (e.g., `test_rule_engine.py`)
- **Integration tests**: `test_integration.py` or `test_{workflow}_integration.py`
- **Migration tests**: `test_{feature}_migration.py` (move to obsolete when complete)
- **Validation tests**: `test_{refactor}_validation.py` (move to obsolete when complete)

## Maintenance Rules

**@RULE:REGULAR_REVIEW**: Review test organization quarterly:
1. Identify tests that are no longer needed for ongoing development
2. Move completed migration/validation tests to obsolete/
3. Delete truly unnecessary tests after 6+ months in obsolete/
4. Update documentation

**@RULE:OBSOLETE_DOCUMENTATION**: When moving tests to obsolete/:
1. Add entry to `obsolete/README.md` explaining why it's obsolete
2. Include date when moved and expected retention period
3. Note any historical insights or references

## Guidelines for Contributors

### Before Adding New Tests
1. **Determine lifecycle**: Is this a permanent test or temporary validation?
2. **Choose location**: Main directory for ongoing tests, plan obsolete move for temporary tests
3. **Follow naming**: Use consistent naming conventions
4. **Document purpose**: Clear docstrings explaining test purpose and scope

### After Completing Features
1. **Review temporary tests**: Move completed migration/validation tests to obsolete/
2. **Update documentation**: Update this README and obsolete/README.md
3. **Clean up**: Remove truly unnecessary test files

This ensures the tests directory remains clean, organized, and focused on active development needs.