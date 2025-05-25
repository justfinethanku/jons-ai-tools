# CLAUDE.md - AI Tools Project Development Context

## Current Project Status (May 25, 2025)

The AI Tools project has undergone major architectural consolidation and cleanup. The codebase is now **production-ready** with clean, maintainable architecture.

## Recent Major Changes (This Session)

### ✅ Architecture Consolidation Completed
1. **Eliminated Redundant Systems**:
   - Deleted `tools/brand_builder.py` (redundant with step01)
   - Deleted `frameworks/shared_utilities.py` (over-engineered utility layer)
   - Deleted `notion_client_manager.py` (superseded by unified_client_manager)

2. **Fixed Circular Dependencies**:
   - Moved workflow base classes (`WorkflowContext`, `StepResult`, `WorkflowStep`) from brand_builder.py to step_01_website_extractor.py
   - Updated all imports to use proper hierarchies
   - Eliminated circular import failures

3. **Centralized Testing & Debugging**:
   - **ALL tests and debug scripts** moved to `xfindandfixshit/` package
   - Structure: `tests/` (unit/integration/functional), `debug/` (by component), `legacy/` (obsolete code)
   - Updated pytest configuration for new structure

### ✅ Current Clean Architecture

**Core Framework Structure**:
- `frameworks/research_tools_framework.py` - Production Notion database operations
- `frameworks/unified_client_manager.py` - Sophisticated Streamlit UI with session isolation  
- `frameworks/universal_framework.py` - AI API integrations and prompt enhancement
- `frameworks/database_manager.py` - Enterprise-grade database operations

**Brand Builder**:
- `tools/brand_builder/step_01_website_extractor.py` - Complete automated extraction pipeline
- Steps 02-09 - Specialized brand analysis modules
- Contains workflow base classes (no external dependencies)

**Testing & Debugging**:
- `xfindandfixshit/tests/` - Production test suite (unit/integration/functional)
- `xfindandfixshit/debug/` - Debug scripts organized by component
- `xfindandfixshit/legacy/` - Archived obsolete code

## Development Guidelines

### **CRITICAL RULE**: All new tests and debug scripts MUST go in `xfindandfixshit/` subdirectories
- **Tests** → `xfindandfixshit/tests/` (unit/integration/functional)
- **Debug scripts** → `xfindandfixshit/debug/` (organized by component: general, frameworks, tools, brand_builder)
- **Obsolete code** → `xfindandfixshit/legacy/` (archive, don't delete)

### Architecture Principles
- **Single Responsibility** - Each module has one clear purpose
- **No Circular Dependencies** - Clean import hierarchies maintained
- **Session Isolation** - Per-tool state management in Streamlit via unified_client_manager
- **Error Boundaries** - Comprehensive error handling and recovery

## Current Client Management System

**Three-tier system** (cleaned and consolidated):
1. **database_manager.py** - Enterprise backend operations (retry logic, validation, health checks)
2. **unified_client_manager.py** - Sophisticated Streamlit UI (session isolation, progress tracking, website analysis)
3. **research_tools_framework.py** - Production client data management (CRUD operations, tool tracking)

## Known Working Functionality

### ✅ Brand Builder Step 1
- Complete automated website extraction
- Sitemap discovery and content analysis  
- Notion database integration
- Contains workflow base classes for steps 2-9

### ✅ Testing Infrastructure
- Pytest configuration in `xfindandfixshit/pytest.ini`
- Working test files in `xfindandfixshit/tests/unit/` and `tests/integration/`
- Debug utilities in `xfindandfixshit/debug/general/`

### ✅ Client Management
- Unified client manager provides sophisticated UI
- Research tools framework handles database operations
- Universal framework integrates with unified client manager

## Next Development Priorities

1. **Expand Test Coverage** - Add tests for remaining Brand Builder steps
2. **Performance Optimization** - API caching and request batching
3. **Enhanced UI/UX** - Improve Streamlit interface experience
4. **Monitoring** - Error tracking and performance metrics

## Development Context for Future Sessions

The codebase is now **clean and production-ready**. All redundant systems have been eliminated, circular dependencies resolved, and testing infrastructure centralized. The architecture follows clear separation of concerns with single responsibility modules.

**Key for future developers**: This project now has a solid foundation for rapid, reliable development without technical debt obstacles.