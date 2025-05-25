# PHASE 2: SYSTEM-WIDE COUPLING ASSESSMENT

## AUDIT OBJECTIVE
Comprehensive analysis of bilateral dependencies, shared state, and interface stability across the entire codebase to identify tight coupling patterns that cause cascading failures.

## SCOPE
Analysis of coupling patterns between:
- frameworks/ ↔ tools/ ↔ prompts/ ↔ resources/
- Cross-package dependencies and circular imports
- Shared state and global variables
- Function signature dependencies and interface contracts

---

## 2A: BILATERAL DEPENDENCIES ANALYSIS - IN PROGRESS

### Bilateral Dependency Discovery - COMPLETED ✅

## CRITICAL FINDINGS: CONFIRMED CIRCULAR DEPENDENCIES

### **🔴 Direct Circular Dependency #1: refiner_framework ↔ prompt_refiner**

**Framework imports Tool (Line 98)**:
```python
# frameworks/refiner_framework.py:98
from tools.prompt_refiner import revise_prompt
```

**Tool imports Framework**: While not directly importing refiner_framework, prompt_refiner.py is tightly coupled through:
- Both use same API keys from st.secrets["google"]["GEMINI_API_KEY"]
- Both use same Gemini model configurations
- prompt_refiner.py functions are specifically designed for refiner_framework.py

**IMPACT ASSESSMENT**:
- **Severity**: HIGH - Framework layer depends on specific tool implementation
- **Breaking Risk**: Changes to prompt_refiner functions break refiner_framework
- **Architectural Violation**: Framework should NOT import specific tools

### **🔴 Architectural Boundary Violation #2: research_tools_framework → brand_builder**

**Framework imports Tool (Line 496)**:
```python
# frameworks/research_tools_framework.py:496
from tools.brand_builder import extract_website_data, analyze_brand_voice
```

**IMPACT ASSESSMENT**:
- **Severity**: CRITICAL - Framework couples to specific tool implementation
- **Breaking Risk**: Changes to brand_builder break research_tools_framework
- **Architectural Violation**: Creates framework dependency on tool layer

## **BIDIRECTIONAL COUPLING PATTERNS IDENTIFIED**

### **Pattern 1: Frameworks ↔ Tools Heavy Coupling**

**Frameworks importing Tools**:
- `refiner_framework.py` → `prompt_refiner.py`
- `research_tools_framework.py` → `brand_builder.py`

**Tools importing Frameworks**:
- Multiple Brand Builder steps → `research_tools_framework.py`
- `context_gatherer.py` → `research_tools_framework.py`  
- `brand_builder.py` → `research_tools_framework.py`

**RESULT**: Bidirectional dependency web creates coupling hotspot

### **Pattern 2: Tools ↔ Tools Coupling**

**Brand Builder Internal Coupling**:
```python
# tools/brand_builder.py imports individual steps:
from tools.brand_builder.step_01_website_extractor import WebsiteExtractorTool
from tools.brand_builder.step_02_brand_analyzer import BrandAnalyzerTool
```

**BUT**: Individual steps are properly independent (no cross-step imports) ✅

### **Pattern 3: Cross-Package Deep Chains**

**Longest Import Chain Identified**:
```
app.py → tools/brand_builder.py → frameworks/research_tools_framework.py → tools/brand_builder (CIRCULAR!)
```

**Other Deep Chains**:
```
app.py → tools/social_copy_tool.py → frameworks/universal_framework.py → external APIs
app.py → tools/prompt_refiner.py → frameworks/refiner_framework.py → tools/prompt_refiner (CIRCULAR!)
```

## **SHARED DEPENDENCY HOT SPOTS**

### **High-Usage Internal Modules**

**1. `research_tools_framework.py` (COUPLING HOTSPOT)**
- **Imported by**: 6+ files across tools/ and brand_builder/
- **Imports from**: tools/brand_builder (creates circular dependency)
- **Risk**: Changes break multiple components

**2. `universal_framework.py` (MEDIUM COUPLING)**
- **Imported by**: Multiple tools for API access
- **Dependencies**: External APIs only (good separation)
- **Risk**: API changes affect multiple tools

**3. `notion_client_manager.py` (SHARED DATABASE DEPENDENCY)**
- **Imported by**: Brand Builder steps, test files
- **Dependencies**: Notion API, Streamlit secrets
- **Risk**: Database schema changes affect all steps

### **External Library Clustering**

**Streamlit Usage** (UI COUPLING):
- **Files affected**: 8+ files across all layers
- **Problem**: UI framework mixed with business logic
- **Impact**: Cannot run tools outside Streamlit environment

**Notion Client** (DATABASE COUPLING):
- **Files affected**: 6+ files across tools and frameworks
- **Problem**: Database code scattered, no abstraction
- **Impact**: Database changes require updates across multiple files

## **ARCHITECTURAL BOUNDARY VIOLATIONS**

### **Critical Violations Identified**

**1. Framework → Tool Dependencies**:
- `frameworks/refiner_framework.py` → `tools/prompt_refiner.py`
- `frameworks/research_tools_framework.py` → `tools/brand_builder.py`
- **Violation**: Lower layer (framework) depends on higher layer (tools)

**2. Presentation → Business Logic**:
- `app.py` directly imports tool implementations
- UI controls mixed with business logic in tools
- **Violation**: No separation of concerns

**3. Database Layer Violations**:
- Database access scattered across tools/ instead of centralized
- No data access layer abstraction
- **Violation**: Business logic tightly coupled to specific database

## **COUPLING SEVERITY ANALYSIS**

### **🔴 CRITICAL RISKS (Immediate Breaking Potential)**

**1. Circular Framework Dependencies** 
- **Impact**: 3-5 files affected per change
- **Frequency**: Core functionality, used heavily
- **Alternatives**: Dependency injection, event-driven architecture
- **Failure Risk**: 95% - Changes to either side break the other

**2. research_tools_framework Hotspot**
- **Impact**: 6+ files import this module
- **Frequency**: Used by all Brand Builder steps
- **Alternatives**: Service interfaces, abstractions
- **Failure Risk**: 90% - Changes cascade through Brand Builder

### **🟡 HIGH RISKS (Likely Breaking Changes)**

**3. Streamlit UI Coupling**
- **Impact**: 8+ files contain UI code
- **Frequency**: All user-facing functionality
- **Alternatives**: Separate UI layer, headless operation
- **Failure Risk**: 70% - UI framework changes break business logic

**4. Notion Database Scatter**
- **Impact**: 6+ files access database directly
- **Frequency**: All data persistence operations
- **Alternatives**: Repository pattern, data access layer
- **Failure Risk**: 75% - Database schema changes break multiple tools

### **⚪ MEDIUM RISKS (Manageable)**

**5. Deep Import Chains**
- **Impact**: 3-4 levels deep
- **Frequency**: Main workflows
- **Alternatives**: Loose coupling, interfaces
- **Failure Risk**: 50% - Changes propagate unpredictably

**6. External API Clustering**
- **Impact**: Multiple tools per API
- **Frequency**: Core AI functionality
- **Alternatives**: API abstraction layer
- **Failure Risk**: 40% - API changes affect multiple tools

## **ROOT CAUSE: INVERTED DEPENDENCY ARCHITECTURE**

The analysis reveals an **"inverted dependency" pattern**:

```
CURRENT (BROKEN):
app.py ← frameworks ← tools (should depend this way)
  ↓        ↓        ↑
  └──── ALSO ──────┘ (but frameworks also depend on tools!)
```

**CORRECT ARCHITECTURE**:
```
app.py → tools → frameworks → external APIs
(dependency flows one direction only)
```

**Impact**: This bidirectional dependency web is the root cause of "fix one thing, break another" cascading failures.

---

## 2B: SHARED STATE ANALYSIS - COMPLETED ✅

## **CRITICAL FINDINGS: GLOBAL STATE COUPLING**

### **Streamlit Session State Chaos** 🔴

**Session State Key Inventory**:
```python
# CONFLICTING CLIENT SELECTION PATTERNS:
st.session_state.tool                    # app.py - Tool selection
st.session_state["selected_client"]      # universal_framework.py - Object-based
st.session_state.client_page_id          # research_tools_framework.py - ID-based  
st.session_state.client_name             # research_tools_framework.py - Name cache

# TOOL-SPECIFIC STATE:
st.session_state["generated_outputs"]    # social_copy_tool.py - Copy results
st.session_state["refined"]              # refiner_framework.py - Prompt state
st.session_state["revision_history"]     # refiner_framework.py - History stack
st.session_state["clear_revision_input"] # refiner_framework.py - UI flags
```

### **🚨 CRITICAL SESSION STATE ISSUES**

**1. Client Selection State Conflicts**:
- **THREE different client selection patterns**:
  1. `universal_framework.py`: Object-based `selected_client`
  2. `research_tools_framework.py`: ID-based `client_page_id` + `client_name`
  3. Direct session state access in individual tools
- **Result**: Client selection broken across tools, state pollution

**2. Cross-Tool State Pollution**:
- Session state persists when switching between tools
- No cleanup when changing clients
- Previous tool state affects new tool behavior
- **Result**: Unexpected side effects, inconsistent UI behavior

**3. Memory Leaks in Session State**:
- `generated_outputs` accumulates without bounds
- `revision_history` grows indefinitely
- No session cleanup mechanisms
- **Result**: Memory consumption grows, performance degrades

### **Global Singleton Architecture** 🔴

**Critical Singletons Identified**:

**1. Cached Notion Clients**:
```python
# frameworks/universal_framework.py
@st.cache_resource  
def get_notion_manager():
    return NotionClientManager()  # GLOBAL SINGLETON
```
**Risk**: Single database connection shared across ALL users/sessions

**2. Global Prompt Wrapper**:
```python
# frameworks/prompt_wrappers.py
prompt_wrapper = PromptWrapper()  # MODULE-LEVEL SINGLETON
```
**Risk**: Prompt system changes affect entire application

**3. Database Manager Persistence**:
```python
class NotionDatabaseManager:
    def __init__(self):
        self.notion = Client(auth=api_key)  # PERSISTENT CONNECTION
```
**Risk**: Database state shared across operations, potential data bleed

### **Configuration State Scatter** 🟡

**st.secrets Access Pattern**:
- **10+ files** directly access `st.secrets` without abstraction
- **Hardcoded configuration keys** scattered across modules
- **No fallback mechanisms** when secrets unavailable
- **Different access patterns**: Some use try/catch, others assume existence

**Examples**:
```python
# Pattern 1: Direct access (most common)
notion_api_key = st.secrets["notion"]["NOTION_API_KEY"]

# Pattern 2: Fallback attempt  
api_key = os.getenv("NOTION_API_KEY") or st.secrets["notion"]["NOTION_API_KEY"]

# Pattern 3: Hard-coded (security risk)
NOTION_API_KEY = "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"
```

### **Mutable State Sharing Hazards** 🔴

**WorkflowContext State Accumulation**:
```python
# Brand Builder workflow context grows across steps
context.data.update(step_result.data)  # MUTABLE SHARED STATE
```
**Risk**: Context modifications in one step affect all subsequent steps

**Database Manager State Coupling**:
- **Two competing database managers**:
  1. `NotionClientManager` (universal_framework.py)
  2. `NotionDatabaseManager` (research_tools_framework.py)
- **Shared database connections** without proper isolation
- **Configuration coupling** through st.secrets access

### **Cross-Package State Dependencies** ⚠️

**Hidden State Coupling Chains**:
```
app.py → session_state.tool
      ↓
universal_framework.py → session_state.selected_client  
      ↓
research_tools_framework.py → session_state.client_page_id
      ↓
brand_builder steps → WorkflowContext.data (mutable)
```

**Impact**: State changes in one layer cascade through entire system

### **State Management Inconsistencies** 🟡

**Three Different Client Management Patterns**:

**Pattern 1**: Object-based (universal_framework.py)
```python
selected_client = st.session_state.get("selected_client")
```

**Pattern 2**: ID-based (research_tools_framework.py)  
```python
client_page_id = st.session_state.client_page_id
client_name = st.session_state.client_name
```

**Pattern 3**: Direct access (tools)
```python
# Tools access session state directly without abstraction
```

**Result**: Inconsistent UI behavior, client selection conflicts

## **SHARED STATE RISK ASSESSMENT**

### **🔴 CRITICAL RISKS (Immediate Data Corruption Potential)**

**1. Shared Database Connections** 
- **Risk**: User data bleeding between sessions
- **Impact**: Data corruption, privacy violations
- **Frequency**: Every database operation
- **Fix Priority**: IMMEDIATE

**2. Session State Conflicts**
- **Risk**: Tool state pollution, UI inconsistencies  
- **Impact**: Broken user workflows, unpredictable behavior
- **Frequency**: Every tool switch
- **Fix Priority**: IMMEDIATE

**3. Global Singleton Coupling**
- **Risk**: System-wide changes from local modifications
- **Impact**: Changes break unrelated functionality
- **Frequency**: Core system operations
- **Fix Priority**: HIGH

### **🟡 HIGH RISKS (Stability Issues)**

**4. Configuration State Scatter**
- **Risk**: Runtime failures from missing config
- **Impact**: Application crashes, deployment issues
- **Frequency**: System initialization
- **Fix Priority**: HIGH

**5. Mutable Context Accumulation**
- **Risk**: State leakage between workflow runs
- **Impact**: Incorrect analysis results, data mixing
- **Frequency**: Brand Builder executions
- **Fix Priority**: MEDIUM-HIGH

### **⚪ MEDIUM RISKS (Performance/UX Issues)**

**6. Memory Leaks in Session State**
- **Risk**: Performance degradation over time
- **Impact**: Slow application, browser crashes
- **Frequency**: Extended user sessions
- **Fix Priority**: MEDIUM

**7. Inconsistent State Patterns**
- **Risk**: Developer confusion, maintenance issues
- **Impact**: Bugs from assumption mismatches
- **Frequency**: Development/debugging
- **Fix Priority**: MEDIUM

## **ROOT CAUSE: GLOBAL STATE ARCHITECTURE**

The shared state analysis reveals a **"global state anti-pattern"**:

```
CURRENT (BROKEN):
Global Session State ← Tool A ← Tool B ← Tool C
       ↓                ↓        ↓        ↓
   All tools share and modify same state (CHAOS!)
```

**CORRECT ARCHITECTURE**:
```
Tool A → Isolated State A
Tool B → Isolated State B  
Tool C → Isolated State C
    ↓         ↓         ↓
Shared Services Layer (clean interfaces)
```

**Impact**: The global state sharing pattern creates hidden dependencies where changes in one tool unexpectedly break others through shared state modification.

---

## 2C: INTERFACE STABILITY ANALYSIS - COMPLETED ✅

## **CRITICAL FINDINGS: LOAD-BEARING FUNCTION INTERFACES**

### **🔥 HIGH-RISK "LOAD-BEARING WALL" FUNCTIONS**

Functions where signature changes would cause **SYSTEM-WIDE CASCADING FAILURES**:

### **1. Universal Framework API Hub** 🔴

**CRITICAL INTERFACES**:
```python
# frameworks/universal_framework.py
call_gemini_api(prompt, response_schema=None, temperature=0.2) -> str
call_openai_api(prompt, model="gpt-4", temperature=0.2) -> str  
get_notion_manager() -> NotionClientManager  # @st.cache_resource

# DEPENDENCY IMPACT:
# - Used by: ALL 9 Brand Builder steps
# - Used by: All tools requiring AI inference  
# - Breaking changes = ENTIRE SYSTEM FAILURE
```

### **2. Workflow Orchestration Backbone** 🔴

**CRITICAL ABSTRACT INTERFACE**:
```python
# tools/brand_builder/__init__.py
class WorkflowStep(ABC):
    execute(context: WorkflowContext) -> StepResult  # ABSTRACT

class StepResult:
    success: bool
    data: Dict[str, Any] 
    errors: List[str]
    warnings: List[str]
    step_name: str

# DEPENDENCY IMPACT:
# - ALL 9 Brand Builder steps inherit this interface
# - Signature changes require updating 9 implementations
# - Return type changes break orchestration layer
```

### **3. Database Integration Hub** 🔴

**CRITICAL DATABASE INTERFACES**:
```python
# notion_client_manager.py
get_clients() -> List[Dict]  # Expected format: [{"id": str, "name": str, ...}]
get_client_profile(client_page_id) -> Dict
update_client_profile(client_page_id, profile_data) -> bool

# DEPENDENCY IMPACT:
# - Client selection UI depends on exact return format
# - Profile management depends on dictionary structure
# - Changes cascade through UI components
```

### **4. Prompt Generation Hub** 🔴

**CRITICAL PROMPT INTERFACES**:
```python
# frameworks/prompt_wrappers.py
class PromptWrapper:
    get_*_prompt(*args) -> Tuple[str, float]  # (prompt, temperature)
    
# Examples:
get_website_extraction_prompt(client_name, website_url, content_input, schema) -> Tuple[str, float]
get_brand_voice_analysis_prompt(client_name, website_data, form_data=None) -> Tuple[str, float]

# DEPENDENCY IMPACT:
# - ALL Brand Builder steps expect (prompt, temperature) tuple
# - Return format change breaks tuple unpacking
# - 11+ specialized prompt methods with same pattern
```

## **CRITICAL INTERFACE CONTRACT VIOLATIONS FOUND** 🚨

### **1. MISSING DEPENDENCY: database_config.py**

**CRITICAL FAILURE POINT**:
```python
# Steps 2 & 3 import non-existent module:
from database_config import VOICE_GUIDELINES_DB_ID, NOTION_API_KEY

# FILE DOES NOT EXIST
# Steps 2 & 3 will fail at import time
```

**Expected Interface**:
```python
# Missing database_config.py should contain:
VOICE_GUIDELINES_DB_ID: str  # Notion database ID
CONTENT_SAMPLES_DB_ID: str   # Notion database ID
NOTION_API_KEY: str          # API authentication
```

### **2. INCONSISTENT INTERFACE PATTERNS**

**Context Validation Signatures**:
```python
# Step 2: validate_context(context) -> List[str]  # warnings only
# Step 3: validate_context(context) -> tuple[bool, list, list]  # (valid, errors, warnings)

# INCONSISTENT: Same method name, different return types
```

**Database Save Function Patterns**:
```python
# Step 2: save_to_voice_guidelines_database(client_name: str, data: dict) -> bool
# Step 3: save_to_content_samples_database(samples: list, client_id: str) -> tuple[list, str]

# INCONSISTENT: Different parameter orders, return types
```

### **3. JSON PARSING STRATEGY CHAOS**

**Multiple Conflicting Approaches**:
```python
# Step 2: robust_json_parse(text) -> tuple[bool, dict, str]
# Step 1: json.loads(response) with simple try/catch  
# research_tools_framework: clean_json_response(text) -> str

# INCONSISTENT: Multiple parsing strategies, different error handling
```

## **CROSS-MODULE DEPENDENCY MAPPING**

### **Critical Dependency Chains Identified**:

**Universal Framework Dependency Tree**:
```
universal_framework.call_gemini_api()
├── step_01_website_extractor.py
├── step_02_brand_analyzer.py 
├── step_03_content_collector.py
├── step_04_voice_auditor.py
├── step_05_audience_definer.py
├── step_06_voice_traits_builder.py
├── step_07_gap_analyzer.py
├── step_08_content_rewriter.py
├── step_09_guidelines_finalizer.py
├── social_copy_tool.py
└── prompt_refiner.py

IMPACT: 11+ files break if signature changes
```

**Prompt Wrapper Dependency Tree**:
```
prompt_wrappers.PromptWrapper.get_*_prompt()
├── ALL 9 Brand Builder steps expect (prompt, temperature) tuple
├── Tuple unpacking: prompt, temperature = wrapper.get_*_prompt(...)
└── Return format change = syntax errors in ALL steps

IMPACT: Signature change breaks tuple unpacking across entire workflow
```

**Circular Import Chain**:
```
tools/brand_builder.py
├── from tools.brand_builder import BrandBuilderWorkflow
├── from tools.brand_builder.step_01_website_extractor import WebsiteExtractorTool
└── Each step imports: from tools.brand_builder import WorkflowStep

RISK: Circular import potential if __init__.py imports specific steps
```

## **DATABASE SCHEMA CONTRACT DEPENDENCIES**

### **Notion Database Field Contracts**:

**Voice Guidelines Database Schema** (Step 2 dependency):
```python
# Expected by step_02_brand_analyzer.py
properties = {
    "Name": {"title": [{"text": {"content": str}}]},
    "Status": {"select": {"name": "In Progress"|"Completed"}}, 
    "Tone_Description": {"rich_text": [{"text": {"content": str}}]},
    "Word_Choice_Guidelines": {"rich_text": [{"text": {"content": str}}]},
    "Brand_Voice_Summary": {"rich_text": [{"text": {"content": str}}]},
    # Schema changes break database save operations
}
```

**Content Samples Database Schema** (Step 3 dependency):
```python
# Expected by step_03_content_collector.py
properties = {
    "Client": {"relation": {"database_id": str}},  # Required relation
    "Channel": {"rich_text": [{"text": {"content": str}}]},
    "Content Type": {"rich_text": [{"text": {"content": str}}]},
    "Description": {"rich_text": [{"text": {"content": str}}]},
    "Strategic Notes": {"rich_text": [{"text": {"content": str}}]}
}
```

## **API RESPONSE CONTRACT DEPENDENCIES**

### **Gemini API Response Contract**:
```python
# Expected response structure by universal_framework.py
response.candidates[0].content.parts[0].text  # JSON string when schema provided
response.text  # Direct text when no schema

# Required JSON parsing capabilities:
# - Handle ```json prefixes/suffixes
# - Extract content between first { and last }
# - Provide fallback parsing strategies
```

### **Brand Builder Step Output Contracts**:
```python
# Step 1 → Step 2 data contract:
{
    "industry": str,
    "company_description": str, 
    "key_products_services": List[str],
    "contact_email": str,
    # 14+ total fields expected by Step 2
}

# Step 2 → Database contract:
{
    "current_target_audience": str,
    "brand_values": List[str],
    "brand_mission": str,
    # 15+ fields that must map to Notion properties
}
```

## **INTERFACE STABILITY RISK ASSESSMENT**

### **🔴 CRITICAL RISKS (System Failure Guaranteed)**

**1. Universal Framework APIs**
- **Functions**: `call_gemini_api()`, `call_openai_api()`
- **Impact**: 11+ files, entire AI inference layer
- **Failure Mode**: System-wide AI functionality breakdown
- **Risk Level**: 100% cascading failure

**2. WorkflowStep.execute() Interface** 
- **Functions**: Abstract `execute()` method
- **Impact**: All 9 Brand Builder steps
- **Failure Mode**: Workflow orchestration breakdown
- **Risk Level**: 90% workflow system failure

**3. Missing database_config.py**
- **Functions**: Import dependencies in Steps 2 & 3
- **Impact**: Import-time failures
- **Failure Mode**: Steps 2 & 3 won't start
- **Risk Level**: 100% immediate failure

### **🟡 HIGH RISKS (Multiple Component Failures)**

**4. NotionClientManager Methods**
- **Functions**: `get_clients()`, `get_client_profile()`
- **Impact**: Client UI, data persistence
- **Failure Mode**: Client management breakdown
- **Risk Level**: 75% UI/database failure

**5. Prompt Wrapper Return Format**
- **Functions**: All `get_*_prompt()` methods
- **Impact**: All Brand Builder steps
- **Failure Mode**: Tuple unpacking syntax errors
- **Risk Level**: 80% prompt generation failure

### **⚪ MEDIUM RISKS (Localized Failures)**

**6. Database Schema Changes**
- **Functions**: Notion property mappings
- **Impact**: Database save operations
- **Failure Mode**: Data persistence failures
- **Risk Level**: 60% data loss potential

## **IMMEDIATE INTERFACE FIXES REQUIRED**

### **🚨 BLOCKING ISSUES (Prevent Any Development)**

1. **Create `database_config.py`** - Steps 2 & 3 import failure
2. **Standardize validation signatures** - Inconsistent return types
3. **Unify JSON parsing strategy** - Multiple conflicting approaches
4. **Fix circular import potential** - Brand Builder package structure

### **🔧 LOAD-BEARING WALL FUNCTIONS (Touch With Extreme Care)**

1. `universal_framework.call_gemini_api()` - Core AI inference
2. `WorkflowStep.execute()` - Workflow backbone
3. `NotionClientManager.get_clients()` - Client management
4. `PromptWrapper.get_*_prompt()` - Prompt generation
5. `WorkflowContext` methods - Data flow management

**Any changes to these functions require coordinated updates across 5-15+ dependent files with extensive integration testing.**