"""
Brand Builder prompt configurations using the structured 5W system
NOTE: Formerly context_gatherer_prompts.py - renamed for better tool branding
"""

from frameworks.prompt_system import prompt_system

# Register website extraction prompt
prompt_system.register(
    name="website_extraction",
    tier="structured",
    components=[
        "who.business_analyst_expert",
        "what.extract_company_data", 
        "how.using_website_content",
        "why.for_marketing_strategy",
        "format.as_json_schema"
    ],
    description="Extract structured company information from website content",
    variables=["client_name", "website_url", "content_input", "output_schema"],
    temperature=0.3,
    use_case="Step 1 of brand building process"
)

# Register brand voice analysis prompt
prompt_system.register(
    name="brand_voice_analysis", 
    tier="structured",
    components=[
        "who.brand_strategist_senior",
        "what.analyze_brand_voice",
        "how.with_structured_analysis",
        "why.for_marketing_strategy", 
        "format.as_json_schema"
    ],
    description="Comprehensive brand voice analysis using enhanced methodology",
    variables=["website_context", "existing_brand_info"],
    temperature=0.7,
    use_case="Step 2 of brand building process"
)

# Register content collection prompt (Deep Research Workflow Step 2)
prompt_system.register(
    name="content_collection",
    tier="structured", 
    components=[
        "who.content_strategist_expert",
        "what.collect_brand_communications",
        "how.identify_and_catalog_content",
        "why.for_voice_analysis",
        "format.as_content_catalog"
    ],
    description="Identify and catalog brand communications for voice analysis",
    variables=["brand_context", "industry_context", "target_channels"],
    temperature=0.5,
    use_case="Deep Research Workflow - Step 2: Content Collection"
)

# Register voice audit prompt (Deep Research Workflow Step 3)
prompt_system.register(
    name="voice_audit",
    tier="structured",
    components=[
        "who.brand_voice_analyst",
        "what.audit_voice_consistency", 
        "how.analyze_voice_patterns",
        "why.identify_voice_gaps",
        "format.as_voice_audit"
    ],
    description="Analyze content samples for voice consistency and brand alignment",
    variables=["brand_profile", "content_samples", "industry_context"],
    temperature=0.6,
    use_case="Deep Research Workflow - Step 3: Voice Audit"
)

# Register audience definer prompt (Deep Research Workflow Step 4)
prompt_system.register(
    name="audience_definer",
    tier="structured",
    components=[
        "who.audience_strategist_expert",
        "what.develop_detailed_persona",
        "how.synthesize_persona_data", 
        "why.for_voice_development",
        "format.as_detailed_persona"
    ],
    description="Develop comprehensive audience persona from multiple workflow data sources",
    variables=["brand_context", "content_insights", "voice_insights", "industry_context"],
    temperature=0.7,
    use_case="Deep Research Workflow - Step 4: Audience Persona Development"
)

# Register voice traits builder prompt (Deep Research Workflow Step 5)
prompt_system.register(
    name="voice_traits_builder",
    tier="structured",
    components=[
        "who.voice_strategist_expert",
        "what.extract_persona_driven_traits",
        "how.synthesize_for_persuasion",
        "why.for_conversion_optimization", 
        "format.as_actionable_traits"
    ],
    description="Extract persona-optimized voice traits with Do/Don't guidance for conversion",
    variables=["persona_profile", "voice_analysis", "brand_foundation", "industry_context"],
    temperature=0.8,
    use_case="Deep Research Workflow - Step 5: Voice Traits Engineering"
)

# Register competitor discovery prompt (Gap Analyzer Stage 1)
prompt_system.register(
    name="competitor_discovery",
    tier="structured",
    components=[
        "who.competitive_intelligence_analyst",
        "what.identify_strategic_competitors",
        "how.research_competitor_landscape",
        "why.for_market_positioning",
        "format.as_competitor_list"
    ],
    description="Identify and validate strategic competitors for market analysis",
    variables=["client_context", "industry_context", "target_market"],
    temperature=0.4,
    use_case="Gap Analyzer - Stage 1: Competitive Discovery"
)

# Register individual competitor analysis prompt (Gap Analyzer Stage 2)
prompt_system.register(
    name="competitor_analysis",
    tier="structured",
    components=[
        "who.competitive_intelligence_analyst",
        "what.analyze_competitor_voice",
        "how.evaluate_competitor_strategy",
        "why.for_market_positioning",
        "format.as_competitor_profile"
    ],
    description="Analyze individual competitor voice and positioning strategy",
    variables=["competitor_info", "analysis_framework", "client_context"],
    temperature=0.5,
    use_case="Gap Analyzer - Stage 2: Individual Competitor Analysis"
)

# Register strategic gap analysis prompt (Gap Analyzer Stage 3)
prompt_system.register(
    name="strategic_gap_analysis",
    tier="structured",
    components=[
        "who.strategic_positioning_expert",
        "what.synthesize_competitive_strategy",
        "how.develop_market_strategy",
        "why.for_market_positioning",
        "format.as_strategic_analysis"
    ],
    description="Synthesize competitive intelligence into strategic positioning recommendations",
    variables=["client_analysis", "competitor_profiles", "market_context", "voice_traits"],
    temperature=0.7,
    use_case="Gap Analyzer - Stage 3: Strategic Synthesis"
)

# Register content transformation analysis prompt (Content Rewriter Stage 1)
prompt_system.register(
    name="content_transformation_analysis",
    tier="structured",
    components=[
        "who.content_transformation_specialist",
        "what.analyze_content_transformation_opportunities",
        "how.analyze_content_against_insights",
        "why.demonstrate_voice_implementation",
        "format.content_transformation_analysis"
    ],
    description="Analyze content samples against voice traits and persona insights for transformation opportunities",
    variables=["content_samples", "voice_traits", "persona_insights", "competitive_positioning"],
    temperature=0.6,
    use_case="Content Rewriter - Stage 1: Transformation Analysis"
)

# Register content transformation prompt (Content Rewriter Stage 2)
prompt_system.register(
    name="content_transformation",
    tier="structured",
    components=[
        "who.content_transformation_specialist",
        "what.transform_content_samples",
        "how.transform_content_systematically",
        "why.demonstrate_voice_implementation",
        "format.transformed_content_examples"
    ],
    description="Transform content samples by applying voice traits, persona optimization, and competitive positioning",
    variables=["transformation_plan", "voice_traits", "persona_profile", "competitive_insights", "content_samples"],
    temperature=0.8,
    use_case="Content Rewriter - Stage 2: Content Transformation"
)

# Register brand voice guidelines synthesis prompt (Guidelines Finalizer)
prompt_system.register(
    name="brand_voice_guidelines_synthesis",
    tier="structured",
    components=[
        "who.brand_guidelines_synthesizer",
        "what.synthesize_brand_voice_guidelines",
        "how.synthesize_comprehensive_guidelines",
        "why.create_actionable_guidelines",
        "format.brand_voice_guidelines"
    ],
    description="Synthesize all Deep Research Workflow insights into comprehensive Brand Voice Guidelines document",
    variables=["brand_foundation", "persona_profile", "voice_traits", "competitive_analysis", "content_examples", "workflow_summary"],
    temperature=0.7,
    use_case="Guidelines Finalizer - Step 8: Complete Brand Voice Guidelines Creation"
)

# Export for easy importing
WEBSITE_EXTRACTION = "website_extraction"
BRAND_VOICE_ANALYSIS = "brand_voice_analysis"
CONTENT_COLLECTION = "content_collection"
VOICE_AUDIT = "voice_audit"
AUDIENCE_DEFINER = "audience_definer"
VOICE_TRAITS_BUILDER = "voice_traits_builder"
COMPETITOR_DISCOVERY = "competitor_discovery"
COMPETITOR_ANALYSIS = "competitor_analysis"
STRATEGIC_GAP_ANALYSIS = "strategic_gap_analysis"
CONTENT_TRANSFORMATION_ANALYSIS = "content_transformation_analysis"
CONTENT_TRANSFORMATION = "content_transformation"
BRAND_VOICE_GUIDELINES_SYNTHESIS = "brand_voice_guidelines_synthesis"