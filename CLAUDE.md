# CLAUDE.md - AI Tools Project Philosophy

## Tiered Prompt Architecture Philosophy

### Core Problem Solved
Not all prompts are created equal. Some need rigorous structure (research), others need simplicity (validation), and some need creative freedom (brainstorming). This tiered system matches the right architecture to the right use case.

## **Three-Tier System**

### **Tier 1: STRUCTURED (5W System)**
**Use for:** Complex analysis, research, content generation, data extraction

**Philosophy:** WHO-WHAT-HOW-WHY-FORMAT mandatory completeness for professional AI interactions

**File Structure:**
```
prompts/
├── structured/
│   ├── components/
│   │   ├── who_[persona]_[expertise].py      # Roles & personas
│   │   ├── what_[action]_[object].py         # Tasks & objectives  
│   │   ├── how_[method]_[approach].py        # Instructions & methodology
│   │   ├── why_[purpose]_[context].py        # Context & motivation
│   │   └── format_[structure]_[type].py      # Output specifications
│   └── configs/
│       ├── research_prompts.py               # Prompt compositions
│       └── analysis_prompts.py
```

**Component Content Format:**
```python
# prompts/structured/components/who_business_analyst_expert.py
CONTENT = "WHO: You are a professional business analyst specializing in company research and data extraction."
```

**Validation Rules:**
- All 5 components (who/what/how/why/format) must be present
- Prefix-first naming convention enforced
- Build fails if components missing
- Automatic completeness checking

### **Tier 2: SIMPLE (Template System)**
**Use for:** Utilities, validations, quick operations, system messages

**Philosophy:** Minimal overhead, fast execution, template substitution

**File Structure:**
```
├── simple/
│   ├── templates/
│   │   ├── validate_email_format.py         # "Check if {email} is valid"
│   │   ├── confirm_action.py                # "Are you sure you want to {action}?"
│   │   └── format_output.py                 # "Format this as {format_type}"
│   └── one_liners.py                        # Quick reference prompts
```

**Usage Pattern:**
```python
validate_prompt = PromptBuilder.simple(
    "Check if this email is valid: {email}",
    email="test@example.com"
)
```

### **Tier 3: CREATIVE (Flexible Components)**
**Use for:** Brainstorming, ideation, free-form content, experimental prompts

**Philosophy:** Mix-and-match creativity with loose structure

**File Structure:**
```
└── creative/
    ├── starters/       # Opening inspiration ("Imagine if...", "What would happen...")
    ├── contexts/       # Situational framing ("In a startup environment...")
    ├── constraints/    # Creative boundaries ("Under 100 words", "Using only questions")
    └── styles/         # Tone and approach ("Enthusiastic", "Professional", "Humorous")
```

**Usage Pattern:**
```python
brainstorm_prompt = PromptBuilder.creative(
    "starters.imagine_if",
    "contexts.startup_environment", 
    "constraints.under_100_words",
    "styles.enthusiastic_tone"
)
```

## **Tool Classification Matrix**

### **STRUCTURED (5W) Tools:**
- ✅ Brand Builder - Complex client research
- ✅ Brand Voice Analyzer - Multi-step analysis  
- ✅ Content Collector - Structured data gathering
- ✅ Competitor Research - Comprehensive analysis
- ✅ Report Generation - Professional documentation

### **SIMPLE (Template) Tools:**
- ✅ Email Validation - Quick format checks
- ✅ Data Transformation - Format conversions
- ✅ API Response Parsing - Standard operations
- ✅ Error Messages - System communications
- ✅ Confirmation Dialogs - User interactions

### **CREATIVE (Flexible) Tools:**
- ✅ Brainstorming Sessions - Open ideation
- ✅ Creative Copy Generation - Artistic content
- ✅ Ideation Workshops - Collaborative thinking
- ✅ Free-form Writing - Unstructured content
- ✅ Experimental Prompts - R&D testing

## **Universal PromptBuilder Implementation**

```python
# frameworks/prompt_builder.py
class PromptBuilder:
    @classmethod
    def structured(cls, components):
        """5W system with mandatory validation"""
        return StructuredPrompt(components)
    
    @classmethod  
    def simple(cls, template, **vars):
        """Quick template substitution"""
        return SimplePrompt(template, **vars)
    
    @classmethod
    def creative(cls, *flexible_components):
        """Mix and match creative elements"""
        return CreativePrompt(*flexible_components)
```

## **Selection Guidelines**

**Choose STRUCTURED when:**
- Multiple steps required
- Professional output needed
- Data extraction/analysis involved
- Consistency is critical
- Quality validation needed

**Choose SIMPLE when:**
- Single operation
- Quick validation needed
- System message required
- Template substitution sufficient
- Speed over structure preferred

**Choose CREATIVE when:**
- Brainstorming or ideation
- Artistic/creative content
- Experimental approaches
- Flexible requirements
- Innovation over consistency

## **Benefits of Tiered Approach**

### **Maintainability**
- Right tool for right job
- No over-engineering simple tasks
- Clear upgrade path (Simple → Structured)

### **Performance**
- Simple prompts execute faster
- Structured prompts ensure quality
- Creative prompts enable innovation

### **Developer Experience**
- Intuitive selection criteria
- Clear patterns to follow
- Reduced cognitive overhead

### **Quality Assurance**
- Structured tier prevents incomplete prompts
- Simple tier reduces bugs in utilities
- Creative tier encourages experimentation

## **Implementation Priority**

1. **Phase 1:** Implement Structured tier for Brand Builder
2. **Phase 2:** Create Simple tier for utility functions
3. **Phase 3:** Build Creative tier for brainstorming tools
4. **Phase 4:** Universal PromptBuilder with tier detection

## **Migration Strategy**

**Existing Tools:**
- Audit current prompts for complexity
- Migrate research tools to Structured tier
- Convert utilities to Simple tier
- Flag creative opportunities for Creative tier

**New Tools:**
- Classify during planning phase
- Use appropriate tier from start
- Document tier choice reasoning

This architecture ensures optimal prompt structure without sacrificing flexibility or over-engineering simple operations.

---

## **Recent Development Session Summary**

### **Brand Builder Systematic Audit (Current Session)**
- **Problem Identified**: Brand Builder steps had critical database integration failures and schema mismatches
- **Solution Approach**: Systematic audit of all 9 Brand Builder steps to fix Notion integration and data flow
- **Files Created**: 
  - `brand_builder_audit_plan.md` - Comprehensive audit framework and review checklist
  - `step_02_audit_results.md` - Detailed Step 2 analysis and fixes
  - `step_03_audit_results.md` - Step 3 critical issues identification
- **Step 2 Fixes Completed**: ✅ Added Notion database integration, context validation, output schema fixes
- **Step 3 Fixes In Progress**: 🔄 Added database integration, validation, but testing incomplete

### **Current State**
- ✅ Step 1: Website Analyzer - Previously working
- ✅ Step 2: Brand Analyzer - **FULLY FIXED** (database integration, validation, schema alignment)
- 🔄 Step 3: Content Collector - **PARTIALLY FIXED** (database integration added, needs testing)
- ❓ Steps 4-9: Awaiting systematic audit and fixes

### **Critical Issues Fixed in Step 2**
1. **Database Integration**: Added Voice Guidelines database saving with proper field mapping
2. **Context Validation**: Implemented comprehensive input validation with warnings
3. **Schema Alignment**: Fixed output format to match database rich_text requirements
4. **Testing**: 4/4 tests passed with successful database saving confirmed

### **Critical Issues Identified in Step 3**
1. **Missing Database Integration**: Content Samples database connection was completely missing
2. **Schema Mismatch**: Output didn't match Content Samples database structure
3. **No Context Validation**: Missing validation could cause poor analysis quality
4. **Legacy Prompt System**: Still using old prompt wrapper instead of modular 5W

### **Step 3 Fixes Implemented (Needs Testing)**
- ✅ Added Content Samples database integration and Notion client imports
- ✅ Implemented `save_to_content_samples_database()` with proper field mapping
- ✅ Added `validate_context()` method with errors/warnings system
- ✅ Added client_id relationship for proper database linking
- ⚠️ **INCOMPLETE**: Testing and validation of fixes still needed

### **Next Session Priorities**
1. **IMMEDIATE**: Test Step 3 fixes and complete Content Collector validation
2. **HIGH**: Continue systematic audit of Steps 4-9 following the audit plan
3. **MEDIUM**: Integration testing of sequential workflows (1→2→3→4)
4. **FUTURE**: Full workflow testing and optimization

### **Key Files to Review Next Session**
- `tools/brand_builder/step_03_content_collector.py` - Verify fixes work correctly
- `brand_builder_audit_plan.md` - Continue with Step 4: Voice Auditor audit
- Database configurations and Content Samples schema validation

### **Sitemap Enhancement Implementation Plan**

Phase 1: Research & Design (High Priority)
- Research current Step 1 and existing Notion schemas
- Design Website Pages database with proper client_id relationships

Phase 2: Core Implementation (High Priority)
- Build cascading URL discovery (sitemap → robots.txt → navigation)
- Integrate Notion database saving functionality

Phase 3: Intelligence Layer (Medium Priority)
- Add blog detection and AI-generated content analysis
- Update downstream steps (3,4,6,8) to leverage stored website data

Phase 4: Validation (Medium Priority)
- End-to-end testing with real client data

This approach ensures we:
1. Don't break existing functionality by researching first
2. Design proper data relationships before implementation
3. Build incrementally with core features first
4. Maximize value by enhancing multiple Brand Builder steps