# PHASE 1: SYSTEM-WIDE DEPENDENCY MAPPING

## AUDIT OBJECTIVE
Complete analysis of import dependencies, data flow patterns, and external integrations across the entire codebase to identify coupling issues and architectural problems.

## SCOPE
- frameworks/ - Core prompt system architecture
- prompts/ - All prompt templates and components
- tools/ - Brand Builder and other tools
- resources/ - Copywriting utilities
- Root files - app.py, database creators, debug scripts

---

## 1A: COMPLETE IMPORT ANALYSIS

### Import Dependency Discovery - COMPLETED ✅

**ANALYSIS SCOPE**: 267 import statements across 50+ Python files
- Root files: 12 files (app.py, create_databases.py, debug_brand_builder.py, etc.)
- frameworks/: 8 files
- prompts/: 45+ structured components and configs  
- tools/: 16 files (Brand Builder steps + other tools)
- resources/: 4 files

## CRITICAL FINDINGS: CIRCULAR DEPENDENCIES DETECTED ⚠️

### **Major Circular Dependency Chains**
1. **refiner_framework ↔ prompt_refiner**
   - `frameworks/refiner_framework.py` imports `tools/prompt_refiner.py`
   - `tools/prompt_refiner.py` imports `frameworks/refiner_framework.py`
   - **IMPACT**: Changes to either module can break the other

2. **research_tools_framework → brand_builder**
   - `frameworks/research_tools_framework.py` imports `tools/brand_builder.py`
   - Creates framework dependency on tool implementation
   - **IMPACT**: Tool changes ripple back to framework layer

### **Cross-Package Coupling Issues**

#### **Heavy Bidirectional Dependencies**
```
frameworks/ ←→ tools/
- Frameworks import specific tools (coupling down)
- Tools import framework components (coupling up)
- Creates web of interdependencies
```

#### **Shared Dependency Clusters**
```
STREAMLIT: Used in 8+ files across all layers
NOTION CLIENT: Database code scattered across tools/
AI APIS: Multiple LLM integrations without abstraction
```

### **Deep Import Chains Creating Tight Coupling**
```
app.py → tools/brand_builder.py → frameworks/prompt_system.py → prompts/structured/configs/
```
**PROBLEM**: Changes at any level propagate through entire chain

### **Architecture Boundary Violations**
1. **Tools importing from Tools**: `tools/brand_builder.py` imports individual step modules
2. **Mixed Abstraction Levels**: Single files contain UI, API, database, and business logic
3. **Framework Leakage**: Streamlit and database code mixed with business logic

## DETAILED IMPORT MAPPING

### **ROOT FILES DEPENDENCIES**
- `app.py`: Heavy Streamlit UI + tool orchestration
- `create_databases.py`: Direct Notion API integration
- `debug_brand_builder.py`: Debugging specific to Brand Builder steps
- Test files: Isolated, good architecture

### **FRAMEWORKS/ PACKAGE ANALYSIS**
- `prompt_system.py`: Core abstractions, minimal external deps ✅
- `universal_framework.py`: Clean framework design ✅
- `refiner_framework.py`: **CIRCULAR DEPENDENCY** with tools/ ⚠️
- `research_tools_framework.py`: **COUPLES TO TOOLS** ⚠️
- `copy_generator_framework.py`: Clean separation ✅

### **TOOLS/ PACKAGE ANALYSIS**
**Brand Builder Steps (9 files):**
- All import from `prompts/structured/components/`
- All import `notion_client_manager` (good shared dependency)
- Heavy framework usage (expected)
- **NO CIRCULAR DEPS** between steps ✅

**Other Tools:**
- `prompt_refiner.py`: **CIRCULAR DEPENDENCY** ⚠️
- `social_copy_tool.py`: Clean design ✅
- `context_gatherer.py`: Framework dependent (expected)

### **PROMPTS/ PACKAGE ANALYSIS**
- Structured components: Pure data files ✅
- Configs: Import multiple components (expected)
- **NO CIRCULAR DEPENDENCIES** ✅
- Clean separation of concerns ✅

### **RESOURCES/ PACKAGE ANALYSIS**
- Minimal external dependencies ✅
- Self-contained utilities ✅
- Clean architecture ✅

## COUPLING SEVERITY ASSESSMENT

### **HIGH RISK** (Immediate Action Required)
1. **Circular Dependencies**: Prevent safe refactoring
2. **Framework→Tool Coupling**: Violates architectural layers
3. **Scattered Database Code**: No centralized data layer

### **MEDIUM RISK** (Address During Refactoring)
1. **Deep Import Chains**: Make changes unpredictable
2. **Mixed Responsibilities**: Single files doing too much
3. **Inconsistent Patterns**: Mix of import styles

### **LOW RISK** (Acceptable)
1. **Tool→Framework Dependencies**: Expected in tool layer
2. **Shared Utilities**: Good when properly abstracted
3. **Test Dependencies**: Isolated and appropriate

---

## 1B: DATA FLOW PATTERNS ANALYSIS - COMPLETED ✅

### **Primary Data Pipeline Architecture**
```
app.py → brand_builder.run_brand_builder()
    ↓
WorkflowContext (Streamlit session state)
    ↓
Step 1: Website Extractor → Company data extraction
    ↓
Step 2: Brand Analyzer → Voice analysis + Database save
    ↓
Step 3: Content Collector → Content strategy + Database save
    ↓
[Steps 4-9: Continue pattern with accumulated context]
```

### **Data Contract Analysis**

#### **CONSISTENT PATTERNS** ✅
1. **WorkflowStep.execute()** → `StepResult` dataclass
   - Standard: `{success: bool, data: dict, errors: list, warnings: list}`
   - **Used across all 9 Brand Builder steps**
   - Enables predictable workflow orchestration

2. **Database Integration Format**
   - All steps follow: `format_for_database() → save_to_X_database()`
   - Consistent `client_id` relationship linking
   - Standardized rich_text field mapping

#### **CRITICAL DATA FLOW ISSUES** ⚠️

### **Issue 1: Inconsistent Array Handling**
```python
# Some functions expect:
brand_values: list[str] = ["Innovation", "Quality"] 

# Others expect:
brand_values: str = "Innovation, Quality"

# Database storage format varies
```
**IMPACT**: Data format mismatches cause parsing failures

### **Issue 2: JSON Parsing Fragility**
```python
# Step 2 has 3 fallback parsing strategies:
1. Direct json.loads()
2. Extract JSON between {}
3. research_tools_framework.clean_json_response()
```
**IMPACT**: Indicates frequent API response failures

### **Issue 3: Context Validation Gaps**
- **Steps 2-3**: Have `validate_context()` methods ✅
- **Steps 4-9**: Missing input validation ⚠️
- **Risk**: Bad data propagates through entire workflow

### **Issue 4: Client ID Propagation**
```python
# Required for database relations but inconsistently passed
client_id = context.data.get('client_id')  # May be None
```
**IMPACT**: Database linking failures in later steps

## **State Management Analysis**

### **Streamlit Session State Usage**
- `st.session_state.tool` - Current active tool
- `st.session_state.selected_client` - Universal client selection  
- `st.session_state.generated_outputs` - Social copy results
- `st.session_state.client_page_id` - Notion client reference

**ISSUE**: Session state scattered across multiple files, no central management

### **WorkflowContext Design** ✅
- Accumulative data container across Brand Builder steps
- Serializable to JSON for workflow resumption
- Well-structured for step-by-step progression

### **Caching Mechanisms**
- `@st.cache_resource` for Notion client initialization ✅
- Component caching in prompt system ✅
- **MISSING**: Result caching for expensive API calls

## **Data Transformation Points**

### **High-Risk Transformations**
1. **Array ↔ String Conversion**: No standardized utility
2. **JSON Response Parsing**: Multiple fallback strategies needed
3. **Database Format Mapping**: Manual conversion in each step
4. **Context Building**: Variable substitution without validation

### **API Integration Patterns**
```python
# Universal Framework Pattern:
universal_framework.call_gemini_api() → str (JSON or plain text)
universal_framework.call_openai_api() → str (plain text)

# Notion Integration Pattern:
NotionClientManager.get_clients() → list[dict]
save_to_database() → bool (success/failure)
```

## **Cross-Module Data Flow Issues**

### **Prompt System Flow Problems**
```
Tools → prompt_wrappers.py → prompt_system.py
     ↓
Issue: prompt_wrappers returns (prompt, temperature) tuples
     ↓  
Issue: Not all callers handle temperature parameter
```

### **Database Integration Flow Problems**
```
Step Results → format_for_database()
           ↓
Issue: Database config may not exist (no validation)
           ↓
Notion Client → save_to_database()
           ↓
Issue: Client ID may be None (breaks relations)
```

## **DATA FLOW RISK ASSESSMENT**

### **CRITICAL RISKS** 🚨
1. **Context Validation Gaps**: Steps 4-9 missing input validation
2. **Database Config Missing**: No graceful fallback when config unavailable
3. **Array Format Inconsistency**: Causes parsing failures between components
4. **Client ID Propagation**: Database relations can break

### **HIGH RISKS** ⚠️
1. **JSON Parsing Fragility**: Multiple fallback strategies indicate unreliable APIs
2. **Session State Scatter**: No centralized state management
3. **Temperature Parameter**: Inconsistent handling across components

### **MEDIUM RISKS** ⚪
1. **Missing Result Caching**: Expensive API calls repeated unnecessarily
2. **Manual Format Conversion**: Error-prone database mapping
3. **Context Building**: Variable substitution without validation

---

## 1C: DATABASE & EXTERNAL INTEGRATIONS - COMPLETED ✅

### **EXTERNAL DEPENDENCY ARCHITECTURE**

#### **🗄️ DATABASE INTEGRATIONS**

### **Notion API Integration (CRITICAL RISK)** 🔴

**Files Affected**: `notion_client_manager.py`, `universal_framework.py`, `research_tools_framework.py`, `create_databases.py`, Brand Builder Steps 2-9

**Integration Pattern**:
```python
# Configuration Dependencies
NOTION_API_KEY = st.secrets["notion"]["NOTION_API_KEY"]
CLIENT_DATABASE_ID = st.secrets["notion"]["NOTION_DATABASE_ID"]  
CONTENT_SAMPLES_DB = st.secrets["notion"]["Content_Samples_database_ID"]
VOICE_GUIDELINES_DB = st.secrets["notion"]["voice_guidlines_database_id"]  # Typo!
```

**CRITICAL ISSUES IDENTIFIED**:

1. **Hard-Coded API Keys in Source Code** 🚨
```python
# create_databases.py contains EXPOSED API KEY:
NOTION_API_KEY = "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"
CLIENT_DATABASE_ID = "1f872022-1e76-81f2-8248-e812a9295df0"
```
**SECURITY RISK**: API keys committed to version control

2. **Cascading Failure Architecture** ⚠️
```
Step 2: Brand Analysis → MUST save to Notion → Step 3: Content Collection
                      ↓
                 If save fails → ENTIRE WORKFLOW BREAKS
```

3. **Configuration Schema Typo** ⚠️
```python
"voice_guidlines_database_id"  # Should be "guidelines"
```

4. **Multiple Database Dependencies**
- Client Database (client profiles)
- Voice Guidelines Database (Step 2 output)
- Content Samples Database (Step 3 output)
- **Each step requires ALL databases to be configured**

#### **🤖 AI/LLM API INTEGRATIONS**

### **OpenAI API (MEDIUM RISK)** 🟡
**Files**: `universal_framework.py`, `social_copy_tool.py`
```python
openai.api_key = st.secrets["openai"]["API_KEY"]
response = openai.ChatCompletion.create(model=model, messages=[...])
```

**Issues**:
- No fallback AI providers
- Basic error handling only
- No rate limiting protection

### **Google Gemini API (MEDIUM RISK)** 🟡
**Files**: `universal_framework.py`
```python
genai.configure(api_key=st.secrets["google"]["GEMINI_API_KEY"])
model = genai.GenerativeModel(model_name="gemini-2.5-flash-preview-05-20")
```

**Issues**:
- Hard-coded to specific model version
- Better error handling than OpenAI
- Structured response dependencies

#### **🌐 WEB SCRAPING INTEGRATIONS**

### **Website Content Extraction (HIGH RISK)** 🔴
**Files**: `context_gatherer.py`, `step_01_website_extractor.py`

**Dependencies**:
```python
import requests
import trafilatura  
from bs4 import BeautifulSoup

# Pattern:
downloaded = trafilatura.fetch_url(url)
response = requests.get(url, headers={...}, timeout=10)
```

**CRITICAL ISSUES**:
1. **Network Dependency**: Direct HTTP requests to external websites
2. **No Rate Limiting**: Could be blocked by target websites  
3. **Fixed Timeouts**: 10-second timeout may be insufficient
4. **Failure Cascading**: Website extraction failures break Brand Builder workflow

#### **📁 FILE SYSTEM DEPENDENCIES**

### **Streamlit Secrets Configuration (CRITICAL RISK)** 🔴

**Required Configuration Structure**:
```toml
[notion]
NOTION_API_KEY = "..."
NOTION_DATABASE_ID = "..."
Content_Samples_database_ID = "..."
voice_guidlines_database_id = "..."  # Typo in key name!

[openai]
API_KEY = "..."

[google]
GEMINI_API_KEY = "..."
```

**CRITICAL ISSUES**:
1. **Configuration Brittleness**: Multiple required keys must be exactly correct
2. **Schema Typo**: Misspelled "guidelines" breaks Voice Guidelines database
3. **No Graceful Fallback**: Application fails completely if secrets missing
4. **Dual Configuration**: Some tools check environment variables, others don't

### **Prompt System Files (MEDIUM RISK)** 🟡
**Files**: 40+ files in `prompts/` directory

**Pattern**:
```python
from prompts.structured.components import *
from prompts.structured.configs import *
```

**Issues**:
- Complex import chains for prompt components
- File system coupling for prompt loading
- No fallback if files missing

## **EXTERNAL INTEGRATION RISK ASSESSMENT**

### **🔴 CRITICAL RISKS (Immediate Action Required)**

1. **Hard-Coded API Keys**: `create_databases.py` contains exposed Notion API key
2. **Cascading Database Failures**: Brand Builder completely breaks if any database save fails
3. **Configuration Typos**: "voice_guidlines_database_id" prevents proper database linking
4. **No Graceful Degradation**: Tools fail completely rather than providing partial functionality

### **🟡 HIGH RISKS (Address During Architecture Fixes)**

1. **Website Scraping Fragility**: External website changes break content extraction
2. **Dual Configuration Systems**: Environment variables vs Streamlit secrets inconsistency
3. **No Retry Mechanisms**: Most API calls fail immediately on first error
4. **Single Provider Dependencies**: No fallback AI providers or database alternatives

### **⚪ MEDIUM RISKS (Monitor and Improve)**

1. **AI API Rate Limits**: No protection against rate limiting or quota exhaustion
2. **Model Version Dependencies**: Hard-coded AI model versions may become deprecated
3. **Network Timeout Issues**: Fixed timeouts may be insufficient for slow networks
4. **File System Prompt Loading**: Complex file-based prompt component system

## **HOUSE OF CARDS ARCHITECTURE IDENTIFIED** 🏗️💥

The analysis reveals a **"house of cards" dependency pattern** where:

```
External Website → Content Extraction → Brand Analysis → Notion Save
                                                      ↓
                                               If ANY step fails
                                                      ↓
                                             ENTIRE WORKFLOW BREAKS
```

**Key Problems**:
1. **Sequential Hard Dependencies**: Each step must succeed for next to proceed
2. **No Circuit Breakers**: No protection against repeated external failures  
3. **No Offline Mode**: Complete dependency on external services availability
4. **Configuration Brittleness**: Multiple configuration points that must be perfect

**Impact**: This architecture explains the "fix one thing, break another" pattern - any change to external integrations ripples through the entire system.
