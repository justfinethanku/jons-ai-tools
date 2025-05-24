"""
Context building utilities for complex prompts
NOTE: These functions handle the variable-heavy sections that don't belong in reusable components
"""

import json


def build_website_extraction_context(client_name: str, website_url: str, content_input: str, schema: dict) -> str:
    """
    Build the context section for website extraction prompts
    
    Args:
        client_name: Name of the client company
        website_url: URL of the website being analyzed
        content_input: The extracted website content to analyze
        schema: JSON schema defining the expected output structure
        
    Returns:
        Formatted context string for insertion into prompt
        
    NOTE: This handles the variable substitution that was causing conflicts
    when embedded directly in prompt components
    """
    schema_str = json.dumps(schema, indent=2) if isinstance(schema, dict) else str(schema)
    
    return f"""
**COMPANY DETAILS:**
Company Name: {client_name}
Website URL: {website_url}

**CONTENT TO ANALYZE:**
{content_input}

**EXTRACTION INSTRUCTIONS:**
1. Carefully read through ALL content sections provided
2. Extract specific information for each field below
3. Use exact matches when found; avoid assumptions
4. For contact information, prioritize official/primary channels
5. For social media, extract complete URLs when available

**REQUIRED OUTPUT FORMAT - JSON ONLY:**
{schema_str}
"""


def build_brand_voice_context(client_name: str, website_data: dict, form_data: dict = None) -> str:
    """
    Build the context section for brand voice analysis prompts
    
    Args:
        client_name: Name of the client company
        website_data: Dictionary containing extracted website information
        form_data: Optional existing form data to enhance analysis
        
    Returns:
        Formatted context string for brand voice analysis
        
    NOTE: This creates rich input context for comprehensive brand analysis
    """
    # Build website context section
    website_context = f"""
**COMPANY OVERVIEW:**
- Name: {client_name}
- Industry: {website_data.get('industry', 'Unknown')}
- Description: {website_data.get('company_description', 'Not available')}
- Products/Services: {', '.join(website_data.get('key_products_services', []))}
- Target Markets: {', '.join(website_data.get('target_markets', []))}
- Geographical Presence: {website_data.get('geographical_presence', 'Not specified')}
- Company Size Indicators: {website_data.get('company_size_indicators', 'Not specified')}"""
    
    # Add existing form data if available
    if form_data:
        known_info = [f"{k.replace('_', ' ').title()}: {v}" for k, v in form_data.items() if v and k not in ['website', 'industry']]
        if known_info:
            website_context += f"\n\n**EXISTING BRAND INFORMATION TO ENHANCE:**\n" + "\n".join(known_info)
    
    # Add the output schema for brand voice
    brand_voice_schema = {
        "current_target_audience": "Detailed description of who they currently reach",
        "ideal_target_audience": "Strategic target audience recommendation",
        "brand_values": ["Core Value 1", "Core Value 2", "Core Value 3", "Core Value 4"],
        "brand_mission": "Clear, inspiring purpose statement that guides decision-making",
        "value_proposition": "Unique positioning statement - what makes them different",
        "brand_personality_traits": ["Trait 1", "Trait 2", "Trait 3", "Trait 4", "Trait 5"],
        "communication_tone": "Primary tone description",
        "voice_characteristics": ["Characteristic 1", "Characteristic 2", "Characteristic 3"],
        "language_level": "Communication complexity level",
        "desired_emotional_impact": ["Emotion 1", "Emotion 2", "Emotion 3"],
        "brand_archetypes": ["Primary Archetype", "Secondary Archetype"],
        "competitive_differentiation": "How they should stand apart from competitors",
        "content_themes": ["Theme 1", "Theme 2", "Theme 3", "Theme 4"],
        "words_tones_to_avoid": ["Avoid 1", "Avoid 2", "Avoid 3"],
        "messaging_priorities": ["Priority Message 1", "Priority Message 2", "Priority Message 3"]
    }
    
    schema_str = json.dumps(brand_voice_schema, indent=2)
    
    return f"""{website_context}

**BRAND VOICE FRAMEWORK TO DEVELOP:**

Return ONLY a valid JSON object. Do not include any explanatory text before or after the JSON.

{schema_str}

Provide strategic, actionable insights based on the company analysis."""


def build_content_collection_context(brand_context: str, industry_context: str, target_channels: list = None) -> str:
    """
    Build the context section for content collection prompts
    
    Args:
        brand_context: Brand information from previous workflow steps
        industry_context: Industry-specific context and considerations
        target_channels: Optional list of specific channels to focus on
        
    Returns:
        Formatted context string for content collection analysis
        
    NOTE: This builds context for identifying content samples across communication channels
    """
    channels_text = f"**PRIORITY CHANNELS:** {', '.join(target_channels)}" if target_channels else "**FOCUS:** All major communication channels relevant to this brand"
    
    content_schema = {
        "content_samples": [
            {
                "channel": "Communication channel or platform name",
                "content_type": "Specific type of content within that channel",
                "sample_description": "What specific content to collect or example of what to look for",
                "strategic_notes": "Why this content type is important for brand voice analysis"
            }
        ]
    }
    
    schema_str = json.dumps(content_schema, indent=2)
    
    return f"""
**BRAND CONTEXT:**
{brand_context}

**INDUSTRY CONTEXT:**
{industry_context}

{channels_text}

**CONTENT COLLECTION STRATEGY:**
1. Identify 8-12 diverse content samples across key communication channels
2. Focus on content that reveals authentic brand voice patterns and messaging
3. Include both external-facing content (website, social, marketing) and internal communication when relevant
4. Prioritize channels most important for this specific industry and brand type
5. Consider both current content and content types that should be analyzed

**REQUIRED OUTPUT FORMAT - JSON ONLY:**
{schema_str}

Extract and return ONLY the JSON object above."""


def build_voice_audit_context(brand_profile: str, content_samples: str, industry_context: str) -> str:
    """
    Build the context section for voice audit prompts
    
    Args:
        brand_profile: Brand information and voice characteristics from previous steps
        content_samples: Content samples or strategy from Content Collector 
        industry_context: Industry-specific voice considerations
        
    Returns:
        Formatted context string for voice audit analysis
        
    NOTE: This builds comprehensive context for analyzing brand voice consistency
    """
    
    voice_audit_schema = {
        "voice_audit_summary": {
            "overall_consistency": "Brief assessment of voice consistency across samples",
            "strongest_aspects": ["List of 2-3 strongest voice elements"],
            "areas_for_improvement": ["List of 2-3 key improvement areas"]
        },
        "content_analysis": [
            {
                "content_type": "Name/type of content sample",
                "channel": "Communication channel or platform",
                "voice_evaluation": "Detailed analysis of voice characteristics",
                "consistency_score": "Numerical score out of 10",
                "improvement_notes": "Specific actionable recommendations"
            }
        ],
        "voice_patterns": {
            "consistent_elements": ["Voice elements that are consistent across samples"],
            "inconsistent_elements": ["Voice elements that vary inappropriately"],
            "missing_brand_elements": ["Brand elements not reflected in content"]
        }
    }
    
    schema_str = json.dumps(voice_audit_schema, indent=2)
    
    return f"""
**BRAND PROFILE TO ANALYZE AGAINST:**
{brand_profile}

**CONTENT SAMPLES FOR ANALYSIS:**
{content_samples}

**INDUSTRY VOICE CONTEXT:**
{industry_context}

**VOICE AUDIT METHODOLOGY:**
1. Generate realistic content examples based on the content strategy provided
2. Analyze each sample against the brand profile for voice consistency
3. Evaluate tone, word choice, personality traits, and brand alignment
4. Identify patterns of consistency and inconsistency across samples
5. Provide specific, actionable recommendations for voice improvement

**REQUIRED OUTPUT FORMAT - JSON ONLY:**
{schema_str}

Analyze the voice patterns and return ONLY the JSON object above."""


def build_audience_definer_context(brand_context: str, content_insights: str, voice_insights: str, industry_context: str) -> str:
    """
    Build the context section for audience definer prompts
    
    Args:
        brand_context: Brand foundation data including basic audience info
        content_insights: Content strategy and channel recommendations from Content Collector
        voice_insights: Voice audit findings and communication patterns
        industry_context: Industry-specific considerations and context
        
    Returns:
        Formatted context string for comprehensive persona development
        
    NOTE: This synthesizes multiple data sources for detailed persona creation
    """
    
    persona_schema = {
        "persona_identity": {
            "name": "Realistic first and last name that fits the demographic",
            "title": "Specific job title based on industry and seniority level",
            "company_type": "Type and size of company they work for",
            "experience_level": "Years of experience in their role and industry"
        },
        "detailed_demographics": {
            "age_range": "Specific age range (e.g., 28-35)",
            "income_level": "Realistic salary range for their role and location",
            "location": "Geographic preferences or typical locations",
            "education": "Educational background and certifications",
            "family_status": "Personal situation that affects their priorities"
        },
        "industry_context": {
            "daily_challenges": ["List of specific work challenges they face"],
            "decision_making_process": "How they research and make business decisions",
            "success_metrics": "What defines success in their role",
            "industry_language": "Professional terminology and communication style",
            "competitive_landscape": "Their awareness of market competitors"
        },
        "communication_preferences": {
            "preferred_voice_style": "Communication tone and style they respond to best",
            "content_consumption_habits": "How, when, and where they consume content",
            "trust_building_factors": "What builds credibility and trust with them",
            "engagement_patterns": "How they prefer to interact with brands",
            "information_processing": "How they prefer to receive and process information"
        },
        "brand_relationship": {
            "current_awareness": "Current level of brand awareness and perception",
            "ideal_interaction": "How they ideally want to engage with the brand",
            "conversion_barriers": "What prevents them from taking action",
            "value_drivers": "What motivates their purchasing decisions",
            "relationship_expectations": "What they expect from brand relationships"
        }
    }
    
    schema_str = json.dumps(persona_schema, indent=2)
    
    return f"""
**BRAND FOUNDATION DATA:**
{brand_context}

**CONTENT STRATEGY INSIGHTS:**
{content_insights}

**VOICE ANALYSIS FINDINGS:**
{voice_insights}

**INDUSTRY CONTEXT:**
{industry_context}

**PERSONA DEVELOPMENT METHODOLOGY:**
1. Cross-reference all data sources to identify consistent audience patterns
2. Expand basic audience description into realistic, detailed persona
3. Incorporate industry-specific challenges, language, and decision-making patterns  
4. Align communication preferences with voice audit findings
5. Ensure persona feels like a real person with specific needs, goals, and behaviors
6. Validate consistency across all data sources and industry appropriateness

**COMPREHENSIVE PERSONA OUTPUT FORMAT - JSON ONLY:**
{schema_str}

Synthesize all data sources and return ONLY the JSON object above with a detailed, realistic persona."""


def build_voice_traits_context(persona_profile: str, voice_analysis: str, brand_foundation: str, industry_context: str) -> str:
    """
    Build the context section for voice traits builder prompts
    
    Args:
        persona_profile: Detailed audience persona from Audience Definer
        voice_analysis: Voice audit findings and communication patterns
        brand_foundation: Core brand values, mission, and personality traits
        industry_context: Industry-specific communication considerations
        
    Returns:
        Formatted context string for persona-optimized voice traits extraction
        
    NOTE: This creates context for extracting voice traits engineered for persona conversion
    """
    
    voice_traits_schema = {
        "voice_traits_summary": {
            "strategy_overview": "High-level explanation of trait selection strategy for this persona",
            "persona_connection": "How these traits specifically address persona needs and preferences",
            "differentiation_approach": "How traits differentiate from industry standard communication"
        },
        "core_voice_traits": [
            {
                "trait_name": "Descriptive name that captures the trait essence",
                "definition": "Clear explanation of what this trait means in practice",
                "do_examples": ["Specific example using persona language/context", "Another actionable do example", "Third concrete do example"],
                "dont_examples": ["What to avoid - specific counter-example", "Another specific dont example", "Third specific avoidance example"],
                "persona_connection": "Why this trait resonates with this specific persona's psychology",
                "business_impact": "How this trait drives desired persona behavior and business outcomes"
            }
        ],
        "implementation_notes": {
            "trait_prioritization": "Which traits to emphasize in different communication contexts",
            "consistency_guidelines": "How traits work together as a cohesive voice system",
            "adaptation_notes": "How to adapt traits across content types while maintaining effectiveness"
        }
    }
    
    schema_str = json.dumps(voice_traits_schema, indent=2)
    
    return f"""
**DETAILED PERSONA PROFILE:**
{persona_profile}

**VOICE ANALYSIS FINDINGS:**
{voice_analysis}

**BRAND FOUNDATION:**
{brand_foundation}

**INDUSTRY CONTEXT:**
{industry_context}

**VOICE TRAITS ENGINEERING METHODOLOGY:**
1. Analyze persona's communication preferences, decision-making patterns, trust factors, and conversion barriers
2. Cross-reference voice audit strengths (to leverage) and gaps (to address)
3. Extract 3-5 powerful traits that solve persona-specific challenges and drive desired behaviors
4. Create persona-contextualized Do/Don't examples using their language, scenarios, and motivations
5. Ensure traits differentiate from industry norms while building persona trust and credibility
6. Focus on traits that guide persona toward business outcomes and conversion actions

**PERSONA-OPTIMIZED VOICE TRAITS OUTPUT FORMAT - JSON ONLY:**
{schema_str}

Engineer voice traits for maximum persona resonance and return ONLY the JSON object above."""


def build_competitor_discovery_context(client_context: str, industry_context: str, target_market: str) -> str:
    """Build context for competitor discovery prompt"""
    
    discovery_schema = {
        "competitor_discovery": {
            "initial_research": "Overview of competitive landscape and research methodology",
            "selection_criteria": "Criteria used to select top strategic competitors",
            "market_insights": "Key observations about the competitive market"
        },
        "final_competitors": [
            {
                "name": "Competitor company name",
                "website": "Company website URL",
                "rationale": "Why this competitor is strategically important for analysis"
            }
        ]
    }
    
    schema_str = json.dumps(discovery_schema, indent=2)
    
    return f"""
**CLIENT CONTEXT:**
{client_context}

**INDUSTRY CONTEXT:**
{industry_context}

**TARGET MARKET:**
{target_market}

**COMPETITOR DISCOVERY METHODOLOGY:**
1. Identify direct competitors offering similar products/services
2. Identify indirect competitors providing alternative solutions
3. Research market leaders and emerging competitors
4. Consider companies targeting the same audience
5. Select top 5 strategically important competitors for detailed analysis
6. Focus on competitors with strong market presence and brand visibility

**COMPETITOR DISCOVERY OUTPUT FORMAT - JSON ONLY:**
{schema_str}

Identify strategic competitors and return ONLY the JSON object above."""


def build_competitor_analysis_context(competitor_info: str, analysis_framework: str, client_context: str) -> str:
    """Build context for individual competitor analysis prompt"""
    
    analysis_schema = {
        "competitor_overview": {
            "name": "Competitor company name",
            "positioning_summary": "How they position themselves in the market",
            "target_audience": "Primary audience they target",
            "value_proposition": "Their main value proposition"
        },
        "voice_analysis": {
            "communication_style": "Overall communication approach and style",
            "key_messages": ["Primary messaging themes they emphasize"],
            "tone_characteristics": "Voice and tone characteristics",
            "content_strategy": "Approach to content and communication"
        },
        "competitive_assessment": {
            "strengths": ["Communication and positioning strengths"],
            "weaknesses": ["Gaps, weaknesses, or missed opportunities"],
            "differentiation_opportunities": ["Ways client could differentiate"],
            "market_position": "Their current market positioning strength"
        }
    }
    
    schema_str = json.dumps(analysis_schema, indent=2)
    
    return f"""
**COMPETITOR TO ANALYZE:**
{competitor_info}

**ANALYSIS FRAMEWORK:**
{analysis_framework}

**CLIENT CONTEXT (for comparison):**
{client_context}

**COMPETITOR ANALYSIS METHODOLOGY:**
1. Research competitor's website, messaging, and public communications
2. Analyze their voice characteristics, tone, and communication style
3. Identify their positioning strategy and target audience approach
4. Evaluate their communication strengths and weaknesses
5. Note opportunities for client differentiation and competitive advantage
6. Consider their market position and brand presence

**COMPETITOR ANALYSIS OUTPUT FORMAT - JSON ONLY:**
{schema_str}

Analyze this competitor and return ONLY the JSON object above."""


def build_strategic_gap_analysis_context(client_analysis: str, competitor_profiles: str, market_context: str, voice_traits: str) -> str:
    """Build context for strategic gap analysis prompt"""
    
    strategic_schema = {
        "market_landscape_analysis": {
            "competitive_overview": "Summary of overall competitive landscape",
            "common_patterns": "Communication patterns most competitors share",
            "market_gaps": "Underserved areas or messaging white space in the market",
            "differentiation_potential": "Overall opportunities for standing out"
        },
        "competitive_positioning": {
            "client_vs_competitors": "How client currently compares to competitors",
            "unique_advantages": ["Client's unique strengths to leverage"],
            "competitive_disadvantages": ["Areas where competitors outperform client"],
            "positioning_opportunities": ["Strategic positioning opportunities"]
        },
        "voice_gap_recommendations": {
            "critical_voice_improvements": ["Most important voice changes to make"],
            "positioning_adjustments": ["How to adjust market positioning"],
            "messaging_priorities": ["Key messaging areas to focus on"],
            "differentiation_strategy": "Overall approach to standing out"
        },
        "implementation_strategy": {
            "immediate_actions": ["Quick wins to implement first"],
            "medium_term_goals": ["Goals for 3-6 month timeframe"],
            "long_term_strategy": "Overall competitive positioning approach",
            "success_metrics": ["How to measure competitive progress"]
        }
    }
    
    schema_str = json.dumps(strategic_schema, indent=2)
    
    return f"""
**CLIENT ANALYSIS:**
{client_analysis}

**COMPETITOR PROFILES:**
{competitor_profiles}

**MARKET CONTEXT:**
{market_context}

**CLIENT VOICE TRAITS:**
{voice_traits}

**STRATEGIC SYNTHESIS METHODOLOGY:**
1. Compare client's current position against all competitor analyses
2. Identify market landscape patterns and common competitive approaches
3. Find messaging white space and differentiation opportunities
4. Align competitive gaps with client's voice traits and positioning goals
5. Develop strategic recommendations for competitive advantage
6. Create prioritized implementation plan for market positioning

**STRATEGIC GAP ANALYSIS OUTPUT FORMAT - JSON ONLY:**
{schema_str}

Synthesize competitive intelligence into strategic recommendations and return ONLY the JSON object above."""


def build_content_transformation_analysis_context(content_samples: str, voice_traits: str, persona_insights: str, competitive_positioning: str) -> str:
    """
    Build context for content transformation analysis prompt
    
    Args:
        content_samples: Content samples from Content Collector step
        voice_traits: Voice traits and guidelines from Voice Traits Builder
        persona_insights: Detailed persona profile from Audience Definer
        competitive_positioning: Strategic positioning from Gap Analyzer
        
    Returns:
        Formatted context string for content transformation analysis
        
    NOTE: This analyzes existing content against all workflow insights for transformation opportunities
    """
    
    transformation_schema = {
        "transformation_analysis": {
            "analysis_summary": "Overall assessment of transformation opportunities",
            "content_samples_analyzed": 0,
            "total_improvements_identified": 0
        },
        "content_transformations": [
            {
                "original_content": "The exact original content sample",
                "content_type": "Type of content (email, social post, blog excerpt, etc)",
                "content_channel": "Where this content appears (website, LinkedIn, etc)",
                "improvement_opportunities": [
                    {
                        "category": "voice_trait_alignment|persona_optimization|competitive_positioning|tone_consistency",
                        "description": "What needs to be improved",
                        "current_issue": "Specific problem with current content",
                        "target_improvement": "What the improved version should achieve"
                    }
                ],
                "priority_score": 0,
                "transformation_complexity": "low|medium|high"
            }
        ],
        "strategic_recommendations": [
            {
                "theme": "Overarching improvement theme",
                "description": "Strategic recommendation for content transformation",
                "applies_to_content_types": ["list of content types this affects"],
                "implementation_priority": "high|medium|low"
            }
        ]
    }
    
    schema_str = json.dumps(transformation_schema, indent=2)
    
    return f"""
**CONTENT SAMPLES FOR ANALYSIS:**
{content_samples}

**VOICE TRAITS TO APPLY:**
{voice_traits}

**TARGET PERSONA INSIGHTS:**
{persona_insights}

**COMPETITIVE POSITIONING STRATEGY:**
{competitive_positioning}

**TRANSFORMATION ANALYSIS METHODOLOGY:**
1. Review each content sample against established voice traits for alignment gaps
2. Evaluate content optimization opportunities for target persona characteristics
3. Assess integration of competitive positioning and differentiation elements
4. Identify specific language, tone, and messaging improvement opportunities
5. Prioritize transformation opportunities by impact potential and implementation complexity
6. Provide strategic themes for systematic content improvement across all channels

**CONTENT TRANSFORMATION ANALYSIS OUTPUT FORMAT - JSON ONLY:**
{schema_str}

Analyze content transformation opportunities and return ONLY the JSON object above."""


def build_content_transformation_context(transformation_plan: str, voice_traits: str, persona_profile: str, competitive_insights: str, content_samples: str) -> str:
    """
    Build context for content transformation prompt
    
    Args:
        transformation_plan: Analysis and recommendations from transformation analysis stage
        voice_traits: Voice traits and guidelines to apply
        persona_profile: Target persona characteristics
        competitive_insights: Competitive positioning strategy
        content_samples: Original content samples to transform
        
    Returns:
        Formatted context string for content transformation execution
        
    NOTE: This transforms content samples by applying all workflow insights systematically
    """
    
    transformation_schema = {
        "transformation_results": {
            "total_content_pieces": 0,
            "successful_transformations": 0,
            "transformation_summary": "Overview of transformation outcomes"
        },
        "transformed_content": [
            {
                "content_id": "Unique identifier for tracking",
                "original_content": "The exact original content sample",
                "transformed_content": "The completely rewritten version",
                "content_type": "Type of content (email, social post, blog excerpt, etc)",
                "content_channel": "Where this content appears",
                "voice_traits_applied": [
                    {
                        "trait_name": "Name of voice trait applied",
                        "application_method": "How this trait was implemented",
                        "before_example": "Specific phrase from original",
                        "after_example": "How it was transformed"
                    }
                ],
                "persona_optimizations": [
                    {
                        "persona_element": "Aspect of persona addressed",
                        "optimization_description": "How content was optimized for persona",
                        "language_changes": "Specific language modifications made"
                    }
                ],
                "competitive_positioning": {
                    "differentiation_applied": "How competitive insights were integrated",
                    "positioning_elements": ["Key positioning concepts incorporated"]
                },
                "improvement_summary": "Overall description of transformations made",
                "quality_score": 0
            }
        ],
        "transformation_patterns": [
            {
                "pattern_name": "Type of transformation pattern identified",
                "description": "What this pattern addresses",
                "frequency": 0,
                "examples": ["List of specific examples where this pattern was applied"]
            }
        ]
    }
    
    schema_str = json.dumps(transformation_schema, indent=2)
    
    return f"""
**TRANSFORMATION PLAN:**
{transformation_plan}

**VOICE TRAITS TO IMPLEMENT:**
{voice_traits}

**TARGET PERSONA PROFILE:**
{persona_profile}

**COMPETITIVE POSITIONING INSIGHTS:**
{competitive_insights}

**ORIGINAL CONTENT SAMPLES:**
{content_samples}

**CONTENT TRANSFORMATION METHODOLOGY:**
1. Transform each content sample by systematically applying voice traits
2. Optimize language and messaging for target persona characteristics and preferences
3. Integrate competitive positioning insights and differentiation elements
4. Preserve core message intent while enhancing voice alignment and persona appeal
5. Create detailed before/after comparisons showing specific improvements made
6. Document transformation patterns for consistent application across content types
7. Ensure all transformations maintain brand authenticity while improving effectiveness

**TRANSFORMED CONTENT OUTPUT FORMAT - JSON ONLY:**
{schema_str}

Transform content samples using all insights and return ONLY the JSON object above."""


def build_brand_voice_guidelines_synthesis_context(brand_foundation: str, persona_profile: str, voice_traits: str, competitive_analysis: str, content_examples: str, workflow_summary: str) -> str:
    """
    Build context for brand voice guidelines synthesis prompt
    
    Args:
        brand_foundation: Brand foundation data from Brand Builder
        persona_profile: Detailed persona from Audience Definer
        voice_traits: Voice traits from Voice Traits Builder
        competitive_analysis: Strategic positioning from Gap Analyzer
        content_examples: Transformed content from Content Rewriter
        workflow_summary: Overview of all workflow steps and insights
        
    Returns:
        Formatted context string for comprehensive guidelines synthesis
        
    NOTE: This synthesizes ALL 7 previous workflow steps into final guidelines document
    """
    
    guidelines_schema = {
        "brand_voice_guidelines": {
            "document_overview": {
                "title": "Brand Voice Guidelines for [Client Name]",
                "version": "1.0",
                "created_date": "YYYY-MM-DD",
                "executive_summary": "Comprehensive overview of brand voice strategy",
                "usage_instructions": "How to use this document effectively"
            },
            "brand_foundation": {
                "mission_statement": "Clear brand mission",
                "core_values": ["Value 1", "Value 2", "Value 3"],
                "value_proposition": "Unique positioning statement",
                "brand_personality": ["Trait 1", "Trait 2", "Trait 3"],
                "competitive_differentiation": "How we stand apart"
            },
            "target_persona": {
                "persona_name": "Primary persona name and title",
                "demographic_summary": "Key characteristics",
                "communication_preferences": "How they prefer information",
                "decision_making_factors": "What influences choices",
                "pain_points": ["Challenge 1", "Challenge 2"],
                "success_metrics": "What defines success"
            },
            "voice_traits": [
                {
                    "trait_name": "Core voice trait name",
                    "definition": "What this trait means",
                    "do_guidelines": ["Do example 1", "Do example 2"],
                    "dont_guidelines": ["Don't example 1", "Don't example 2"],
                    "persona_rationale": "Why this resonates",
                    "application_contexts": ["When to emphasize"]
                }
            ],
            "channel_adaptations": {
                "website_content": {
                    "voice_emphasis": "Which traits to emphasize",
                    "tone_guidelines": "Tone recommendations",
                    "language_level": "Complexity level",
                    "content_themes": ["Theme 1", "Theme 2"]
                },
                "social_media": {
                    "voice_emphasis": "Social platform traits",
                    "tone_guidelines": "Social tone approach",
                    "engagement_style": "Interaction style",
                    "content_themes": ["Theme 1", "Theme 2"]
                },
                "email_marketing": {
                    "voice_emphasis": "Email-specific traits",
                    "tone_guidelines": "Email tone",
                    "personalization_approach": "Personalization method",
                    "content_themes": ["Theme 1", "Theme 2"]
                }
            },
            "competitive_positioning": {
                "market_landscape": "Competitive overview",
                "differentiation_strategy": "How voice sets us apart",
                "messaging_priorities": ["Priority 1", "Priority 2"],
                "competitive_advantages": ["Advantage 1", "Advantage 2"],
                "positioning_statements": ["Statement 1", "Statement 2"]
            },
            "reference_examples": [
                {
                    "content_type": "Content sample type",
                    "original_content": "Before transformation",
                    "improved_content": "After transformation",
                    "voice_traits_demonstrated": ["Trait 1", "Trait 2"],
                    "improvement_rationale": "Why this works better"
                }
            ],
            "implementation_framework": {
                "step_by_step_guide": [
                    {
                        "step_number": 1,
                        "step_title": "Implementation step",
                        "step_description": "Detailed instructions",
                        "deliverables": ["What to produce"]
                    }
                ],
                "quality_assurance": {
                    "voice_checklist": ["Checkpoint 1", "Checkpoint 2"],
                    "common_mistakes": ["Mistake 1", "Mistake 2"],
                    "approval_criteria": "Publication readiness"
                },
                "maintenance_guidelines": {
                    "regular_reviews": "Review frequency",
                    "update_triggers": "When to update",
                    "consistency_monitoring": "How to maintain consistency"
                }
            },
            "quick_reference": {
                "voice_traits_summary": ["Trait 1: Description", "Trait 2: Description"],
                "persona_key_points": ["Key point 1", "Key point 2"],
                "dos_and_donts": {
                    "always_do": ["Do 1", "Do 2"],
                    "never_do": ["Don't 1", "Don't 2"]
                },
                "emergency_guidelines": "Quick guidance for urgent needs"
            }
        }
    }
    
    schema_str = json.dumps(guidelines_schema, indent=2)
    
    return f"""
**BRAND FOUNDATION DATA:**
{brand_foundation}

**TARGET PERSONA PROFILE:**
{persona_profile}

**VOICE TRAITS AND GUIDELINES:**
{voice_traits}

**COMPETITIVE ANALYSIS AND POSITIONING:**
{competitive_analysis}

**CONTENT TRANSFORMATION EXAMPLES:**
{content_examples}

**DEEP RESEARCH WORKFLOW SUMMARY:**
{workflow_summary}

**GUIDELINES SYNTHESIS METHODOLOGY:**
1. Synthesize brand foundation, persona, and positioning into executive summary
2. Consolidate voice traits into clear Do/Don't framework with persona-specific examples
3. Adapt voice guidelines for different channels and content types based on workflow insights
4. Integrate competitive positioning into differentiation strategy
5. Include reference examples from content transformations as quality standards
6. Create comprehensive implementation framework with step-by-step usage guide
7. Develop quality checklist and maintenance guidelines for long-term consistency
8. Provide quick reference section for immediate decision-making support

**COMPREHENSIVE BRAND VOICE GUIDELINES OUTPUT FORMAT - JSON ONLY:**
{schema_str}

Synthesize all workflow insights into a complete, actionable guidelines document and return ONLY the JSON object above."""