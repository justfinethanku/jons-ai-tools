# Jon's AI Tools

## Technical Overview

AI-powered toolkit for brand research and content generation. Built with Streamlit, Python, and Google Gemini 2.5 Flash. Features modular prompt architecture, Notion database integration, and systematic workflow orchestration with clean, maintainable codebase.

---

## Core Tools

### **Brand Builder** - 9-Step Workflow System
Fully automated brand research and analysis pipeline with comprehensive Notion database integration.

**Architecture**: Consolidated workflow with step01 handling complete website extraction and analysis, while steps 02-09 provide specialized brand analysis functions.

**Key Components**:
- **Step 1**: Complete automated website extraction (sitemap discovery, content analysis, Notion integration)
- **Steps 2-9**: Specialized brand analysis modules
- **Unified Client Manager**: Sophisticated Streamlit UI with session isolation and progress tracking
- **Research Tools Framework**: Production-grade Notion database operations

**Database Integration**: 3 connected Notion databases (AI Client Library, Voice Guidelines, Content Samples)

### **Copy Generator** - Social Media Content Generation
Platform-specific content adaptation with brand voice consistency.

**Platforms**: Facebook, LinkedIn, TikTok, YouTube, Generic
**Features**: Character limits, hashtag optimization, brand voice application

### **Prompt Refiner** - Prompt Engineering Tool
Iterative prompt improvement using structured methodologies.

### **Coder Helper** - Technical Prompt Optimization
Specialized for development and technical documentation tasks.

---

## Architecture Overview

### **Clean Framework Structure**
- **`frameworks/`** - Core business logic and AI integrations
  - `research_tools_framework.py` - Production Notion database management
  - `unified_client_manager.py` - Sophisticated Streamlit UI with session isolation
  - `universal_framework.py` - AI API integrations and prompt enhancement
  - `database_manager.py` - Enterprise-grade database operations
- **`tools/`** - Main application tools
  - `brand_builder/step_01_website_extractor.py` - Complete automated extraction pipeline
  - Individual step modules for specialized analysis
- **`xfindandfixshit/`** - All testing and debugging utilities
  - `tests/` - Production test suite (unit, integration, functional)
  - `debug/` - Debug scripts organized by component
  - `legacy/` - Archived obsolete code

### **Recent Architecture Improvements**
- ✅ **Eliminated Redundancy**: Removed duplicate client management systems
- ✅ **Centralized Testing**: All tests and debug scripts moved to `xfindandfixshit/`
- ✅ **Fixed Circular Imports**: Moved workflow base classes to appropriate modules
- ✅ **Simplified Dependencies**: Removed over-engineered utility layers
- ✅ **Clean Consolidation**: Single source of truth for each functionality

---

## Setup

1. **Clone Repository**
   ```bash
   git clone [repository-url]
   cd jons-ai-tools
   ```

2. **Configure Secrets**
   ```bash
   cp .streamlit/secrets.toml.template .streamlit/secrets.toml
   # Add Gemini API key and Notion credentials
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch Application**
   ```bash
   streamlit run app.py
   ```

5. **Run Tests**
   ```bash
   cd xfindandfixshit
   pytest tests/
   ```

---

## Database Schema

### **Notion Databases (3 Connected)**
1. **AI Client Library** - Main client records with comprehensive business data
2. **Voice Guidelines** - Brand analysis results and voice characteristics
3. **Content Samples** - Content strategy data and sample analysis

### **Relationships**
- Voice Guidelines → AI Client Library (Many-to-One)
- Content Samples → AI Client Library (Many-to-One)

---

## Development Guidelines

### **Code Organization**
- **New tests** → `xfindandfixshit/tests/` (unit/integration/functional)
- **Debug scripts** → `xfindandfixshit/debug/` (organized by component)
- **Obsolete code** → `xfindandfixshit/legacy/` (archive, don't delete)
- **Business logic** → `frameworks/` and `tools/`

### **Architecture Principles**
- **Single Responsibility** - Each module has one clear purpose
- **No Circular Dependencies** - Clean import hierarchies
- **Centralized Utilities** - Common functions in appropriate frameworks
- **Session Isolation** - Per-tool state management in Streamlit
- **Error Boundary** - Comprehensive error handling and recovery

---

## Development Roadmap

### **Current Status: Production Ready**
- ✅ **Complete architecture consolidation** 
- ✅ **Eliminated all redundant systems**
- ✅ **Comprehensive testing structure in place**
- ✅ **Clean, maintainable codebase**
- 🎯 **Ready for active development and client workflows**

### **Short Term Enhancement Opportunities**
1. **Performance Optimization**: API response caching and request batching
2. **Enhanced Testing**: Expand test coverage for all workflow components
3. **UI/UX Improvements**: Enhanced Streamlit interface and user experience
4. **Monitoring**: Error tracking and performance metrics collection

### **Long Term Innovation**
1. **Scale Modular Architecture**: Apply proven patterns to other tools
2. **Multi-Model Integration**: Add support for Claude, OpenAI, and other AI providers
3. **Advanced Workflow Orchestration**: Parallel processing and complex task coordination
4. **Enterprise Features**: Advanced authentication, audit trails, and compliance

### **Technical Debt: Resolved**
- ✅ **Circular Dependencies**: Completely eliminated
- ✅ **Redundant Code**: All duplicate systems removed
- ✅ **Testing Chaos**: Centralized in `xfindandfixshit/`
- ✅ **Import Complexity**: Simplified to clear hierarchies
- ✅ **Session State Issues**: Isolated per-tool management

---

## Key Technical Files

- **`tools/brand_builder/step_01_website_extractor.py`** - Complete automated extraction pipeline
- **`frameworks/unified_client_manager.py`** - Sophisticated client management UI
- **`frameworks/research_tools_framework.py`** - Production database operations
- **`xfindandfixshit/`** - All testing and debugging utilities
- **`CLAUDE.md`** - Development session documentation and architecture decisions