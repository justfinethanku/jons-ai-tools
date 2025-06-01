# Obsolete Tests

**@RULE:OBSOLETE_RETENTION**: Tests in this directory are preserved for historical reference but are not part of active development.

**@RULE:OBSOLETE_LIFECYCLE**: Review obsolete tests every 6 months and delete if truly no longer needed.

## Purpose

This directory contains test files that are no longer needed for ongoing development but are preserved for historical reference per the test organization rules in `../README.md`.

## Contents

### Migration Validation Tests (Completed)
These tests were used to validate one-time migrations from original frameworks to the rule-based architecture. Since migrations are complete, these tests are obsolete:

- Migration validation tests for individual tools
- Prompt refactoring validation tests
- Architecture migration validation tests

## Why Obsolete?

These tests served their purpose during the migration phase but are no longer relevant because:

1. **One-time validation**: They validated completed migrations that won't be repeated
2. **Architecture changed**: They test migration from old framework to new rule-based system
3. **Historical value only**: They're preserved for reference but don't need to run

## Current Active Tests

For ongoing development, use the active tests in the parent `tests/` directory:

- `test_integration.py` - Integration tests for rule-based architecture
- `test_rule_engine.py` - Rule engine functionality tests
- `test_rule_parser.py` - Rule parser functionality tests

## Cleanup Policy

- Keep obsolete tests for 6 months for reference
- Review periodically and delete if truly no longer needed
- Document any historical insights before deletion