## Architecture

**Core Frameworks**
- `database_manager.py` - Notion database operations with retry logic and validation
- `unified_client_manager.py` - Single source of truth for client selection with session isolation
- `universal_framework.py` - AI/API integrations (OpenAI, Gemini)
- `shared_utils.py` - Common utilities (JSON parsing, text sanitization, formatting)
- `logging_manager.py` - Structured logging with operation tracking

**Deprecated/Removed**
- ~~`research_tools_framework.py`~~ - Merged into database_manager.py
- ~~`copy_generator_framework.py`~~ - Removed (dead code)
- ~~`refiner_framework.py`~~ - Cleaned up, unused params removed

**Brand Builder**
- Step 01: Website extraction pipeline (contains workflow base classes)
- Steps 02-09: Brand analysis modules

**Testing** → All in `xfindandfixshit/`
- `/tests/` - Test suite
- `/debug/` - Debug scripts  
- `/legacy/` - Archived code

## Key Rules

1. **Testing location**: Everything goes in `xfindandfixshit/`
2. **No circular imports** - Clean hierarchies only
3. **Single responsibility** - One purpose per module
4. **Unified patterns** - Use unified_client_manager for ALL client selection
5. **Structured logging** - Use logging_manager, not basic logging

## What Works Now

✅ Brand Builder Step 1 - Full extraction pipeline  
✅ Client Management - Unified system with retry logic  
✅ Testing Infrastructure - Pytest configured and working  
✅ Logging System - Structured logging with operation tracking  
✅ Database Operations - Automatic retry with exponential backoff
✅ Copy Generator - Retro gaming UI with Legacy Advisors mode
✅ UI/UX - Massive square buttons with profanity-laced easter eggs

## Recent Improvements

1. **Consolidated client selection** - No more duplicate implementations
2. **Retry logic everywhere** - All Notion API calls are resilient
3. **Structured logging** - Better debugging and monitoring
4. **Shared utilities** - No more duplicate helper functions
5. **Clean codebase** - Dead code removed, imports optimized
6. **Retro Gaming UI** - Copy Generator with neon aesthetics and centered layout
7. **Legacy Advisors Mode** - Conditional prompt enhancement for specialized content
8. **Easter Eggs** - Self-deprecating messages, warning screens, secret buttons
9. **Enhanced UX** - Massive square buttons with status indicators

## Next Up

1. Test coverage for steps 2-9
2. API response caching
3. UI performance improvements
4. Production monitoring dashboard

## Status: Production-ready, refactored architecture, zero redundancy