# Jon's AI Tools

## Technical Overview

AI-powered toolkit for brand research and content generation. Built with Streamlit, Python, and Google Gemini 2.5 Flash. Features modular prompt architecture, Notion database integration, and systematic workflow orchestration.

**Current Status**: Undergoing systematic Brand Builder audit and database integration fixes.

---

## Core Tools

### **Brand Builder** - 9-Step Workflow System
Modular brand research and analysis pipeline with Notion database integration.

**Architecture**: WorkflowStep base class with individual step files, CLI interfaces, and workflow orchestration.

**Steps**:
1. **Website Analyzer** - Multi-page content extraction and processing
2. **Brand Analyzer** - ✅ Fixed (database integration, validation, schema alignment)
3. **Content Collector** - 🔄 Partial fixes (database integration added, testing needed)
4. **Voice Auditor** - ❓ Pending audit
5. **Audience Definer** - ❓ Pending audit
6. **Voice Traits Builder** - ❓ Pending audit
7. **Gap Analyzer** - ❓ Pending audit
8. **Content Rewriter** - ❓ Pending audit
9. **Final Report Generator** - ❓ Pending audit

**Database Integration**: 4 connected Notion databases (AI Client Library, Voice Guidelines, Content Samples, Project Tracker)

### **Copy Generator** - Social Media Content Generation
Platform-specific content adaptation with brand voice consistency.

**Platforms**: Facebook, LinkedIn, TikTok, YouTube, Generic
**Features**: Character limits, hashtag optimization, brand voice application

### **Prompt Refiner** - Prompt Engineering Tool
Iterative prompt improvement using structured methodologies.

### **Coder Helper** - Technical Prompt Optimization
Specialized for development and technical documentation tasks.

---

## Prompt Architecture

### **Tiered System**
- **Structured (5W)**: Complex analysis, research (WHO-WHAT-HOW-WHY-FORMAT components)
- **Simple**: Quick operations, validations (template substitution)
- **Creative**: Brainstorming, ideation (flexible mix-and-match)

### **Current Implementation**
- Brand Builder uses structured 5W system with modular prompt components
- Fallback systems ensure reliability when new architecture fails
- Temperature optimization per component type (0.3 extraction, 0.7 analysis)

### **Component Library**
```
prompts/structured/components/
├── who_business_analyst_expert.py
├── what_extract_company_data.py
├── how_using_website_content.py
├── why_for_marketing_strategy.py
└── format_as_json_schema.py
```

---

## Current Development Status

### **Systematic Brand Builder Audit (In Progress)**

**Problem**: Critical database integration failures and schema mismatches across Brand Builder steps.

**Solution**: Systematic audit and fix of all 9 workflow steps.

### **Completed Fixes**
- ✅ **Step 2: Brand Analyzer** - Full database integration, context validation, schema alignment
  - Added Voice Guidelines database saving
  - Implemented comprehensive input validation
  - Fixed rich_text field formatting
  - All tests passing with successful database saving

### **In Progress**
- 🔄 **Step 3: Content Collector** - Database integration added, testing needed
  - Added Content Samples database connection
  - Implemented save_to_content_samples_database() function
  - Added context validation and client relationship linking
  - Requires testing and validation

### **Pending Audit**
- ❓ **Steps 4-9**: Voice Auditor, Audience Definer, Voice Traits Builder, Gap Analyzer, Content Rewriter, Final Report Generator

### **Critical Issues Resolved**
1. **JSON Parsing Errors**: Fixed max_output_tokens causing response truncation
2. **Database Schema Mismatches**: Aligned output formats with Notion field types
3. **Missing Database Integration**: Added proper Notion client connections
4. **Context Validation**: Implemented comprehensive input validation systems

### **Files Created/Modified**
- `brand_builder_audit_plan.md` - Comprehensive audit framework
- `step_02_audit_results.md` - Step 2 analysis and fixes
- `step_03_audit_results.md` - Step 3 critical issues identification
- `tools/brand_builder/step_02_brand_analyzer.py` - Full database integration
- `tools/brand_builder/step_03_content_collector.py` - Partial fixes implemented

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

---

## Database Schema

### **Notion Databases (4 Connected)**
1. **AI Client Library** - Main client records
2. **Voice Guidelines** - Brand analysis results (Step 2 output)
3. **Content Samples** - Content strategy data (Step 3 output)
4. **Project Tracker** - Workflow progress tracking

### **Relationships**
- Voice Guidelines → AI Client Library (Many-to-One)
- Content Samples → AI Client Library (Many-to-One)
- Project Tracker → AI Client Library (Many-to-One)

---

## Development Roadmap

### **Immediate (Next Session)**
1. Test Step 3: Content Collector fixes
2. Complete Step 3 validation and database saving verification
3. Begin Step 4: Voice Auditor audit

### **Short Term**
1. Complete systematic audit of Steps 4-9
2. Fix database integration issues across all steps
3. Implement integration testing for sequential workflows

### **Long Term**
1. Scale modular prompt system to Copy Generator and Prompt Refiner
2. Implement Simple tier for utility functions
3. Build Creative tier for brainstorming tools
4. Performance optimization and error handling improvements

---

## Key Technical Files

- `tools/brand_builder/` - Modular workflow steps
- `prompts/structured/components/` - 5W prompt component library
- `frameworks/` - Universal prompt framework and AI integrations
- `database_config.py` - Centralized Notion database configuration
- `brand_builder_audit_plan.md` - Systematic review framework
- `CLAUDE.md` - Development session documentation and architecture philosophy