# Brand Builder Removal Plan

## Overview
This document outlines the complete plan for removing the brand_builder tool from the project. NO CHANGES HAVE BEEN MADE YET - this is only an analysis and plan.

## 1. Files to Delete

### Primary Files
- `/tools/brand_builder/` - Entire directory (13 files)
  - `__init__.py` - Base classes and workflow orchestration
  - `step_01_website_extractor.py` - Website extraction step
  - `step_02_brand_analyzer.py` - Brand analysis step
  - `step_03_content_collector.py` - Content collection step
  - `step_04_voice_auditor.py` - Voice auditing step
  - `step_05_audience_definer.py` - Audience definition step
  - `step_06_voice_traits_builder.py` - Voice traits building step
  - `step_07_gap_analyzer.py` - Gap analysis step
  - `step_08_content_rewriter.py` - Content rewriting step
  - `step_09_guidelines_finalizer.py` - Guidelines finalization step
  - `__pycache__/` - Compiled Python files

### Cache Files
- `/tools/__pycache__/brand_builder.cpython-310.pyc`
- `/tools/__pycache__/brand_builder_monolith_backup.cpython-310.pyc`

### Test Files
- Test references in `.pytest_cache/v/cache/nodeids`
- Test references in `.pytest_cache/v/cache/lastfailed`
- `/xfindandfixshit/integration/__pycache__/test_brand_builder_workflow.cpython-310-pytest-8.3.5.pyc`

## 2. Files to Edit

### `/app.py`
- Remove `def run_brand_builder()` function (lines ~9-50+)
- Remove import statement: `from tools.brand_builder.step_01_website_extractor import AutomatedWebsiteExtractor, WorkflowContext`
- Remove button code: `if st.button("BRAND\nBUILDER\n\nBROKEN AS FUCK BRB", key="brand_builder_btn"...)`
- Remove function call: `run_brand_builder()`

### `/frameworks/database_manager.py`
- Remove all references to "brand_builder" in:
  - Tool flags dictionaries (multiple occurrences)
  - Tool name mappings: `"Brand_Builder_Complete": "brand_builder"`
  - Field mappings: `"brand_builder": "Brand_Builder_Complete"`

### `/frameworks/unified_client_manager.py`
- Remove import: `from tools.brand_builder import extract_website_data, analyze_brand_voice`
- Remove from tool list: `("brand_builder", "1. Brand Builder")`
- Remove from tool flags: `"brand_builder": False`

### `/README.md`
- Remove line: `└── brand_builder/`

### `/xfindandfixshit/README.md`
- Remove line: `│   └── brand_builder/   # Brand Builder debug scripts`

## 3. Framework Dependencies Used by Brand Builder

The brand_builder tool uses these framework components:
- `frameworks.universal_framework` - For API calls
- `frameworks.database_manager.NotionDatabaseManager` - For database operations
- `frameworks.logging_manager` - For logging
- `frameworks.prompt_wrappers` - For prompt management
- `frameworks.shared_utils` - For JSON parsing

**These frameworks are used by other tools and should NOT be removed.**

## 4. External Dependencies

Based on imports found, brand_builder uses standard libraries and the project's frameworks. No special external dependencies need to be removed from requirements.txt.

## 5. Potential Breaking Changes

1. **UI Impact**: The main app.py will have a missing button/function
2. **Database Schema**: References to brand_builder fields may exist in Notion database
3. **Client Manager**: Tool selection logic will need adjustment
4. **Test Suite**: Test files referencing brand_builder will fail

## 6. Shared Code Analysis

The brand_builder tool defines these base classes in its `__init__.py`:
- `StepResult` - Data class for step results
- `WorkflowContext` - Context management between steps
- `WorkflowStep` - Abstract base class for workflow steps

**These classes are ONLY used within brand_builder and can be safely removed.**

## 7. Removal Steps (In Order)

1. **Backup Current State**
   ```bash
   cp -r tools/brand_builder tools/brand_builder_backup_$(date +%Y%m%d)
   ```

2. **Remove Directory**
   ```bash
   rm -rf tools/brand_builder
   rm -f tools/__pycache__/brand_builder*.pyc
   ```

3. **Edit Python Files**
   - Remove function and imports from app.py
   - Remove all "brand_builder" references from frameworks/database_manager.py
   - Remove imports and references from frameworks/unified_client_manager.py

4. **Update Documentation**
   - Remove from README.md
   - Remove from xfindandfixshit/README.md

5. **Clean Test Cache**
   ```bash
   rm -rf .pytest_cache
   rm -rf xfindandfixshit/integration/__pycache__/*brand_builder*
   ```

6. **Test Remaining Tools**
   - Run the app to ensure other tools still work
   - Check that database operations don't break

## 8. Post-Removal Verification

1. Search for any remaining references:
   ```bash
   grep -r "brand_builder" . --exclude-dir=.git --exclude-dir=venv
   ```

2. Run the application to ensure it starts without errors

3. Test other tools to ensure no dependencies were broken

## Summary

- **Total files to delete**: ~15 files
- **Files to edit**: 5 files
- **Risk level**: MEDIUM - The tool is integrated into the UI and database schema
- **Shared code impact**: NONE - All code is isolated to brand_builder module
- **Framework impact**: NONE - Frameworks are used by other tools