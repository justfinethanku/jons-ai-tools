# Documentation Directory

## Rule: All Documentation Goes Here

**@RULE:DOCUMENTATION_LOCATION**: All project documentation, summaries, and migration reports MUST be placed in this `docs/` directory. Do NOT leave documentation files in the root of `rebuild/`. 

**@RULE:TEST_LOCATION**: Test scripts belong in the `tests/` directory, NOT in docs.

## Purpose

This directory contains all documentation for the rule-based architecture rebuild project:

- Migration summaries and reports
- Architecture documentation
- Implementation guides
- Project status reports

## Contents

### Migration Documentation
- `ALL_TOOLS_MIGRATION_COMPLETE.md` - Complete migration summary for all three tools
- `SOCIAL_COPY_MIGRATION_SUMMARY.md` - Detailed social copy tool migration report
- `PROMPT_REFACTOR_SUMMARY.md` - Prompt refactoring implementation summary
- `CODER_HELPER_MIGRATION_SUMMARY.md` - Coder helper tool migration details
- `PROMPT_REFINER_MIGRATION_SUMMARY.md` - Prompt refiner tool migration details

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