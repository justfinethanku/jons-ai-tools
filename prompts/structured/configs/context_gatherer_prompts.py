"""
Context Gatherer prompt configurations using the structured 5W system
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
    use_case="Step 1 of context gathering process"
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
    use_case="Step 2 of context gathering process"
)

# Export for easy importing
WEBSITE_EXTRACTION = "website_extraction"
BRAND_VOICE_ANALYSIS = "brand_voice_analysis"