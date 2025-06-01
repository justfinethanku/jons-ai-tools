# Documentation Directory

## Rule: All Documentation Goes Here

**@RULE:DOCUMENTATION_LOCATION**: All project documentation, summaries, and migration reports MUST be placed in this `docs/` directory. Do NOT leave documentation files in the root of the project.

**@RULE:TEST_LOCATION**: Test scripts belong in the `tests/` directory, NOT in docs.

## Purpose

This directory contains all documentation for the rule-based architecture project:

- Migration summaries and reports
- Architecture documentation
- Implementation guides
- Project status reports

## Organization Guidelines

1. **Summaries**: Use descriptive filenames ending in `_SUMMARY.md`
2. **Reports**: Use `_REPORT.md` suffix for detailed analysis documents
3. **Guides**: Use `_GUIDE.md` suffix for implementation instructions
4. **Architecture**: Use `_ARCHITECTURE.md` suffix for design documents

## Cleanup Rule

When creating documentation during development:
1. Create files in this `docs/` directory directly
2. If accidentally created in root, move them here immediately
3. Keep the project root clean and organized
4. Update this README when adding new documentation types

## File Naming Convention

- **Migration docs**: `{TOOL_NAME}_MIGRATION_SUMMARY.md`
- **Architecture docs**: `{COMPONENT}_ARCHITECTURE.md`
- **Implementation guides**: `{FEATURE}_IMPLEMENTATION_GUIDE.md`
- **Project reports**: `{PROJECT}_REPORT.md`

This ensures a clean, organized documentation structure that doesn't clutter the main project directory.