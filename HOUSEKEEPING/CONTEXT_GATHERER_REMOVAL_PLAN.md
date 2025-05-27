# Context Gatherer Removal Plan

## Overview
Context Gatherer is a standalone tool (987 lines) that appears to be part of the old brand builder workflow. It's designed to collect client information from websites and populate Notion databases.

## Analysis

### Purpose
- Extracts content from websites (homepage, about, contact, mission pages)
- Analyzes brand voice and attributes
- Updates Notion database with client information
- Marks "context_gatherer" as complete in tool tracking

### Dependencies
1. **Imports used:**
   - `frameworks.universal_framework`
   - `frameworks.database_manager` (NotionDatabaseManager, client_selector_sidebar)
   - `frameworks.prompt_wrappers`
   - `prompts.structured.configs.context_gatherer_prompts`
   - External: BeautifulSoup, trafilatura, requests

2. **No incoming dependencies:**
   - Not imported by any other Python files
   - Not referenced in app.py
   - Runs standalone with `if __name__ == "__main__"`

3. **Database interactions:**
   - Updates client profiles in Notion
   - Marks "context_gatherer" tool as complete
   - Uses client_selector_sidebar for UI

## Impact Assessment

### Low Risk
- Not integrated into main app UI
- No other tools depend on it
- Self-contained functionality

### Potential Issues
1. **Prompt configs:** May have associated prompts in `prompts/structured/configs/`
2. **Database field:** "context_gatherer" completion tracking in Notion
3. **README reference:** Listed in README as a tool

## Removal Steps

### 1. Check for prompt configurations
```bash
find prompts/ -name "*context_gatherer*" -type f
```

### 2. Remove the main file
```bash
rm tools/context_gatherer.py
```

### 3. Remove any prompt configurations
```bash
# After finding them in step 1
rm prompts/structured/configs/context_gatherer_prompts.py  # if exists
```

### 4. Update README.md
- Remove any references to context_gatherer from tools list

### 5. Clean up database references (optional)
- Comment out "context_gatherer" in database_manager.py tool tracking (if present)
- Similar to what was done for brand_builder

### 6. Clear cache
```bash
find . -name "*context_gatherer*.pyc" -delete
```

## Verification Steps

1. **Check for remaining references:**
   ```bash
   grep -r "context_gatherer" . --include="*.py" --exclude-dir=venv
   ```

2. **Run the application:**
   ```bash
   streamlit run app.py
   ```

3. **Test remaining tools** to ensure nothing broke

## Alternative: Keep for Reference
Since this tool is standalone and not causing issues, you could alternatively:
1. Move it to `HOUSEKEEPING/legacy_tools/`
2. Remove from README
3. Keep code for potential future reference

## Recommendation
**REMOVE** - This appears to be part of the brand builder workflow and serves no purpose without it. It's not integrated into the current UI and removal poses minimal risk.