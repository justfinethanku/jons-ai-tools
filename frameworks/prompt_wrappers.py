"""
Safe wrapper functions for transitioning to new prompt system
NOTE: These maintain the exact same interface as the old system while using new components
This allows gradual migration with fallback capability
"""

import json
import logging
from typing import Tuple, Dict, Any

from frameworks.prompt_system import prompt_system, PromptValidationError
from frameworks.prompt_context_builders import build_website_extraction_context, build_brand_voice_context

# Set up logging for debugging prompt system issues
logger = logging.getLogger(__name__)


class PromptWrapper:
    """
    Safe wrapper class that provides fallback capability
    NOTE: This ensures we never break existing functionality during migration
    """
    
    def __init__(self):
        self.fallback_enabled = True
        self.fallback_prompts = self._load_fallback_prompts()
    
    def _load_fallback_prompts(self) -> Dict[str, str]:
        """
        Load original prompts as fallbacks in case new system fails
        NOTE: These are the exact prompts from the original context_gatherer.py
        """
        return {
            'website_extraction': '''You are a professional business analyst specializing in company research and data extraction. Your task is to extract structured company information from website content with high accuracy and completeness.

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
{output_schema}

Extract and return ONLY the JSON object above.''',
            
            'brand_voice_analysis': '''You are a senior brand strategist with expertise in developing comprehensive brand voice profiles. Your task is to analyze the provided company information and develop a strategic brand voice framework.

{website_context}

**ANALYSIS METHODOLOGY:**
1. **Industry Context Analysis**: Consider industry norms, competitive landscape, and communication expectations
2. **Audience Segmentation**: Identify current vs. ideal audiences with specific demographic and psychographic profiles
3. **Brand Positioning**: Determine unique value proposition and market differentiation
4. **Voice Architecture**: Develop personality traits, values, and communication guidelines
5. **Strategic Recommendations**: Provide actionable guidance for brand expression

**BRAND VOICE FRAMEWORK TO DEVELOP:**

Return ONLY a valid JSON object. Do not include any explanatory text before or after the JSON.

{output_schema}

Provide strategic, actionable insights based on the company analysis.'''
        }
    
    def get_website_extraction_prompt(self, client_name: str, website_url: str, content_input: str, schema: dict) -> Tuple[str, float]:
        """
        Get website extraction prompt with temperature
        
        Args:
            client_name: Name of the client company
            website_url: URL being analyzed
            content_input: Website content to analyze
            schema: JSON schema for output validation
            
        Returns:
            Tuple of (prompt_string, temperature)
            
        NOTE: This tries new system first, falls back to old system if issues occur
        """
        try:
            # Build the context section that contains variable data
            context_section = build_website_extraction_context(client_name, website_url, content_input, schema)
            
            # Get prompt from new system with context
            prompt, config = prompt_system.get_prompt_with_config(
                "website_extraction",
                context_section=context_section
            )
            
            logger.info("Successfully used new prompt system for website extraction")
            return prompt, config['temperature']
            
        except Exception as e:
            # Fallback to original prompt if new system fails
            if self.fallback_enabled:
                logger.warning(f"New prompt system failed, using fallback: {e}")
                fallback_prompt = self.fallback_prompts['website_extraction'].format(
                    client_name=client_name,
                    website_url=website_url,
                    content_input=content_input,
                    output_schema=json.dumps(schema, indent=2)
                )
                return fallback_prompt, 0.3  # Original temperature
            else:
                raise e
    
    def get_brand_voice_analysis_prompt(self, client_name: str, website_data: dict, form_data: dict = None) -> Tuple[str, float]:
        """
        Get brand voice analysis prompt with temperature
        
        Args:
            client_name: Name of the client company
            website_data: Extracted website information
            form_data: Optional existing form data
            
        Returns:
            Tuple of (prompt_string, temperature)
            
        NOTE: This handles the complex brand voice analysis with rich context
        """
        try:
            # Build the context section with all the variable data
            context_section = build_brand_voice_context(client_name, website_data, form_data)
            
            # Get prompt from new system
            prompt, config = prompt_system.get_prompt_with_config(
                "brand_voice_analysis",
                context_section=context_section
            )
            
            logger.info("Successfully used new prompt system for brand voice analysis")
            return prompt, config['temperature']
            
        except Exception as e:
            # Fallback to original prompt if new system fails
            if self.fallback_enabled:
                logger.warning(f"New prompt system failed, using fallback: {e}")
                
                # Build context for fallback
                website_context = build_brand_voice_context(client_name, website_data, form_data)
                
                # Brand voice schema for fallback
                brand_voice_schema = {
                    "current_target_audience": "string",
                    "ideal_target_audience": "string", 
                    "brand_values": ["array", "of", "strings"],
                    "brand_mission": "string",
                    "value_proposition": "string",
                    "brand_personality_traits": ["array", "of", "strings"],
                    "communication_tone": "string",
                    "voice_characteristics": ["array", "of", "strings"],
                    "language_level": "string",
                    "desired_emotional_impact": ["array", "of", "strings"],
                    "brand_archetypes": ["array", "of", "strings"],
                    "competitive_differentiation": "string",
                    "content_themes": ["array", "of", "strings"],
                    "words_tones_to_avoid": ["array", "of", "strings"],
                    "messaging_priorities": ["array", "of", "strings"]
                }
                
                fallback_prompt = self.fallback_prompts['brand_voice_analysis'].format(
                    website_context=website_context,
                    output_schema=json.dumps(brand_voice_schema, indent=2)
                )
                return fallback_prompt, 0.7  # Original temperature
            else:
                raise e
    
    def get_content_collection_prompt(self, brand_context: str, industry_context: str, target_channels: list = None) -> Tuple[str, float]:
        """
        Get content collection prompt for Deep Research workflow
        
        Args:
            brand_context: Brand information from previous steps
            industry_context: Industry-specific context
            target_channels: Optional list of channels to focus on
            
        Returns:
            Tuple of (prompt_string, temperature)
        """
        try:
            # Build context section for content collection
            from frameworks.prompt_context_builders import build_content_collection_context
            context_section = build_content_collection_context(brand_context, industry_context, target_channels)
            
            # Get prompt from new system
            prompt, config = prompt_system.get_prompt_with_config(
                "content_collection",
                context_section=context_section
            )
            
            logger.info("Successfully used new prompt system for content collection")
            return prompt, config['temperature']
            
        except Exception as e:
            # Fallback content collection prompt
            if self.fallback_enabled:
                logger.warning(f"New prompt system failed, using fallback: {e}")
                
                fallback_prompt = f'''You are a professional content strategist specializing in brand communication analysis and content cataloging. Your task is to identify and catalog key brand communications across multiple channels to build a comprehensive content sample library.

**BRAND CONTEXT:**
{brand_context}

**INDUSTRY CONTEXT:**
{industry_context}

**TARGET CHANNELS:**
{', '.join(target_channels) if target_channels else 'All major communication channels'}

**INSTRUCTIONS:**
1. Based on the brand context, suggest 8-12 specific content samples across key communication channels
2. For each sample, provide: channel/type, sample description, and strategic notes
3. Focus on content that would reveal authentic brand voice patterns
4. Prioritize channels most relevant to this industry and brand type
5. Include both external-facing content (website, social, ads) and internal content (emails, docs) if relevant

**OUTPUT FORMAT - JSON ONLY:**
{{
    "content_samples": [
        {{
            "channel": "Website Homepage",
            "content_type": "Hero section copy",
            "sample_description": "Main headline and value proposition text",
            "strategic_notes": "Primary brand messaging and tone establishment"
        }}
    ]
}}

Return only the JSON object.'''
                
                return fallback_prompt, 0.5
            else:
                raise e
    
    def get_voice_audit_prompt(self, brand_profile: str, content_samples: str, industry_context: str) -> Tuple[str, float]:
        """
        Get voice audit prompt for Deep Research workflow
        
        Args:
            brand_profile: Brand information and voice characteristics
            content_samples: Content samples to analyze
            industry_context: Industry-specific voice considerations
            
        Returns:
            Tuple of (prompt_string, temperature)
        """
        try:
            # Build context section for voice audit
            from frameworks.prompt_context_builders import build_voice_audit_context
            context_section = build_voice_audit_context(brand_profile, content_samples, industry_context)
            
            # Get prompt from new system
            prompt, config = prompt_system.get_prompt_with_config(
                "voice_audit",
                context_section=context_section
            )
            
            logger.info("Successfully used new prompt system for voice audit")
            return prompt, config['temperature']
            
        except Exception as e:
            # Fallback voice audit prompt
            if self.fallback_enabled:
                logger.warning(f"New prompt system failed, using fallback: {e}")
                
                fallback_prompt = f'''You are a professional brand voice analyst specializing in voice consistency evaluation. Your task is to analyze content samples against the brand profile and create a comprehensive voice audit report.

**BRAND PROFILE:**
{brand_profile}

**CONTENT SAMPLES TO ANALYZE:**
{content_samples}

**INDUSTRY CONTEXT:**
{industry_context}

**ANALYSIS INSTRUCTIONS:**
1. Evaluate each content sample against the brand profile for consistency
2. Assess tone, word choice, personality alignment, and audience fit
3. Identify voice patterns, strengths, and areas for improvement
4. Rate overall voice consistency and provide specific recommendations

**OUTPUT FORMAT - JSON ONLY:**
{{
    "voice_audit_summary": {{
        "overall_consistency": "Brief assessment of voice consistency",
        "strongest_aspects": ["Strength 1", "Strength 2"],
        "areas_for_improvement": ["Gap 1", "Gap 2"]
    }},
    "content_analysis": [
        {{
            "content_type": "Content sample name",
            "channel": "Communication channel",
            "voice_evaluation": "Detailed voice assessment",
            "consistency_score": "X/10",
            "improvement_notes": "Specific recommendations"
        }}
    ],
    "voice_patterns": {{
        "consistent_elements": ["Element 1", "Element 2"],
        "inconsistent_elements": ["Issue 1", "Issue 2"],
        "missing_brand_elements": ["Missing 1", "Missing 2"]
    }}
}}

Return only the JSON object.'''
                
                return fallback_prompt, 0.6
            else:
                raise e
    
    def get_audience_definer_prompt(self, brand_context: str, content_insights: str, voice_insights: str, industry_context: str) -> Tuple[str, float]:
        """
        Get audience definer prompt for Deep Research workflow
        
        Args:
            brand_context: Brand foundation and basic audience info
            content_insights: Content strategy and channel recommendations
            voice_insights: Voice audit findings and patterns
            industry_context: Industry-specific context and considerations
            
        Returns:
            Tuple of (prompt_string, temperature)
        """
        try:
            # Build context section for audience persona development
            from frameworks.prompt_context_builders import build_audience_definer_context
            context_section = build_audience_definer_context(brand_context, content_insights, voice_insights, industry_context)
            
            # Get prompt from new system
            prompt, config = prompt_system.get_prompt_with_config(
                "audience_definer",
                context_section=context_section
            )
            
            logger.info("Successfully used new prompt system for audience definer")
            return prompt, config['temperature']
            
        except Exception as e:
            # Fallback audience definer prompt
            if self.fallback_enabled:
                logger.warning(f"New prompt system failed, using fallback: {e}")
                
                fallback_prompt = f'''You are a professional audience strategist and persona development expert. Your task is to synthesize multiple data sources and create a comprehensive, detailed audience persona.

**BRAND FOUNDATION:**
{brand_context}

**CONTENT STRATEGY INSIGHTS:**
{content_insights}

**VOICE ANALYSIS FINDINGS:**
{voice_insights}

**INDUSTRY CONTEXT:**
{industry_context}

**PERSONA DEVELOPMENT INSTRUCTIONS:**
1. Cross-reference all data sources to identify consistent patterns and insights
2. Expand basic audience information into a detailed, realistic persona
3. Include industry-specific challenges, daily routines, and decision-making patterns
4. Develop communication preferences based on voice analysis findings
5. Create a persona that feels like a real person with specific needs and behaviors

**OUTPUT FORMAT - JSON ONLY:**
{{
    "persona_identity": {{
        "name": "Realistic first and last name",
        "title": "Specific job title",
        "company_type": "Type of company they work for",
        "experience_level": "Years of experience in their role"
    }},
    "detailed_demographics": {{
        "age_range": "Specific age range",
        "income_level": "Salary range",
        "location": "Geographic preferences",
        "education": "Educational background",
        "family_status": "Personal situation"
    }},
    "industry_context": {{
        "daily_challenges": ["Specific work challenges"],
        "decision_making_process": "How they make decisions",
        "success_metrics": "What defines success for them",
        "industry_language": "How they communicate professionally"
    }},
    "communication_preferences": {{
        "preferred_voice_style": "Communication tone they respond to",
        "content_consumption": "How and when they consume content",
        "trust_building_factors": "What builds credibility with them",
        "engagement_patterns": "How they interact with brands"
    }},
    "brand_relationship": {{
        "current_awareness": "Current relationship with brand",
        "ideal_interaction": "How they want to engage with brand",
        "conversion_barriers": "What prevents them from taking action",
        "value_drivers": "What motivates their decisions"
    }}
}}

Return only the JSON object.'''
                
                return fallback_prompt, 0.7
            else:
                raise e
    
    def get_voice_traits_builder_prompt(self, persona_profile: str, voice_analysis: str, brand_foundation: str, industry_context: str) -> Tuple[str, float]:
        """
        Get voice traits builder prompt for Deep Research workflow
        
        Args:
            persona_profile: Detailed audience persona from Audience Definer
            voice_analysis: Voice audit findings and patterns
            brand_foundation: Core brand values, mission, and personality
            industry_context: Industry-specific communication context
            
        Returns:
            Tuple of (prompt_string, temperature)
        """
        try:
            # Build context section for voice traits extraction
            from frameworks.prompt_context_builders import build_voice_traits_context
            context_section = build_voice_traits_context(persona_profile, voice_analysis, brand_foundation, industry_context)
            
            # Get prompt from new system
            prompt, config = prompt_system.get_prompt_with_config(
                "voice_traits_builder",
                context_section=context_section
            )
            
            logger.info("Successfully used new prompt system for voice traits builder")
            return prompt, config['temperature']
            
        except Exception as e:
            # Fallback voice traits builder prompt
            if self.fallback_enabled:
                logger.warning(f"New prompt system failed, using fallback: {e}")
                
                fallback_prompt = f'''You are a professional voice strategist specializing in persona-driven communication optimization. Your task is to extract powerful voice traits that specifically resonate with the target persona and create actionable guidance.

**DETAILED PERSONA PROFILE:**
{persona_profile}

**VOICE ANALYSIS FINDINGS:**
{voice_analysis}

**BRAND FOUNDATION:**
{brand_foundation}

**INDUSTRY CONTEXT:**
{industry_context}

**VOICE TRAITS EXTRACTION INSTRUCTIONS:**
1. Analyze persona's communication preferences, decision-making patterns, and trust factors
2. Cross-reference with voice audit strengths and gaps
3. Extract 3-5 powerful voice traits that solve persona-specific challenges
4. Create detailed Do/Don't examples using persona's language and scenarios
5. Ensure traits differentiate from industry norms while building persona trust
6. Focus on traits that drive the persona toward desired business outcomes

**OUTPUT FORMAT - JSON ONLY:**
{{
    "voice_traits_summary": {{
        "strategy_overview": "High-level approach for why these traits resonate with this persona",
        "persona_connection": "How traits address persona's specific needs and preferences",
        "differentiation_approach": "How traits stand out from industry standard communication"
    }},
    "core_voice_traits": [
        {{
            "trait_name": "Specific descriptive name",
            "definition": "Clear explanation of what this trait means",
            "do_examples": ["Specific example using persona context", "Another do example", "Third do example"],
            "dont_examples": ["What to avoid - specific example", "Another dont example", "Third dont example"],
            "persona_connection": "Why this trait specifically resonates with this persona",
            "business_impact": "How this trait drives desired persona behavior"
        }}
    ],
    "implementation_notes": {{
        "trait_prioritization": "Which traits to emphasize in different contexts",
        "consistency_guidelines": "How traits work together cohesively",
        "adaptation_notes": "How to adapt traits across different content types"
    }}
}}

Return only the JSON object.'''
                
                return fallback_prompt, 0.8
            else:
                raise e
    
    def get_competitor_discovery_prompt(self, client_context: str, industry_context: str, target_market: str) -> Tuple[str, float]:
        """Get competitor discovery prompt for Gap Analyzer Stage 1"""
        try:
            from frameworks.prompt_context_builders import build_competitor_discovery_context
            context_section = build_competitor_discovery_context(client_context, industry_context, target_market)
            
            prompt, config = prompt_system.get_prompt_with_config("competitor_discovery", context_section=context_section)
            logger.info("Successfully used new prompt system for competitor discovery")
            return prompt, config['temperature']
            
        except Exception as e:
            if self.fallback_enabled:
                logger.warning(f"New prompt system failed, using fallback: {e}")
                
                fallback_prompt = f'''You are a competitive intelligence analyst. Identify the top strategic competitors for this company.

**CLIENT CONTEXT:**
{client_context}

**INDUSTRY CONTEXT:**
{industry_context}

**TARGET MARKET:**
{target_market}

**INSTRUCTIONS:**
1. Identify 8-10 potential competitors (direct and indirect)
2. Consider market leaders, direct competitors, and alternative solutions
3. Select top 5 most strategically important competitors
4. Focus on companies that compete for the same target audience

**OUTPUT FORMAT - JSON ONLY:**
{{
    "competitor_discovery": {{
        "initial_research": "Overview of competitive landscape",
        "selection_criteria": "How competitors were chosen",
        "market_insights": "Key market observations"
    }},
    "final_competitors": [
        {{
            "name": "Competitor Name",
            "website": "https://example.com",
            "rationale": "Why this competitor is strategically important"
        }}
    ]
}}

Return only the JSON object.'''
                
                return fallback_prompt, 0.4
            else:
                raise e
    
    def get_competitor_analysis_prompt(self, competitor_info: str, analysis_framework: str, client_context: str) -> Tuple[str, float]:
        """Get individual competitor analysis prompt for Gap Analyzer Stage 2"""
        try:
            from frameworks.prompt_context_builders import build_competitor_analysis_context
            context_section = build_competitor_analysis_context(competitor_info, analysis_framework, client_context)
            
            prompt, config = prompt_system.get_prompt_with_config("competitor_analysis", context_section=context_section)
            logger.info("Successfully used new prompt system for competitor analysis")
            return prompt, config['temperature']
            
        except Exception as e:
            if self.fallback_enabled:
                logger.warning(f"New prompt system failed, using fallback: {e}")
                
                fallback_prompt = f'''You are a competitive intelligence analyst. Analyze this specific competitor's voice and positioning strategy.

**COMPETITOR TO ANALYZE:**
{competitor_info}

**ANALYSIS FRAMEWORK:**
{analysis_framework}

**CLIENT CONTEXT (for comparison):**
{client_context}

**ANALYSIS INSTRUCTIONS:**
1. Research the competitor's voice, messaging, and positioning
2. Identify their target audience approach and value proposition
3. Analyze their communication strengths and weaknesses
4. Note opportunities for differentiation

**OUTPUT FORMAT - JSON ONLY:**
{{
    "competitor_overview": {{
        "name": "Competitor name",
        "positioning_summary": "How they position themselves",
        "target_audience": "Who they target"
    }},
    "voice_analysis": {{
        "communication_style": "How they communicate",
        "key_messages": ["Main messaging themes"],
        "tone_characteristics": "Voice and tone description"
    }},
    "competitive_assessment": {{
        "strengths": ["What they do well"],
        "weaknesses": ["Communication gaps or weaknesses"],
        "differentiation_opportunities": ["How client could stand out"]
    }}
}}

Return only the JSON object.'''
                
                return fallback_prompt, 0.5
            else:
                raise e
    
    def get_content_transformation_analysis_prompt(self, content_samples: str, voice_traits: str, persona_insights: str, competitive_positioning: str) -> Tuple[str, float]:
        """
        Get content transformation analysis prompt for Content Rewriter workflow
        
        Args:
            content_samples: Content samples from Content Collector step
            voice_traits: Voice traits and guidelines from Voice Traits Builder  
            persona_insights: Detailed persona profile from Audience Definer
            competitive_positioning: Strategic positioning from Gap Analyzer
            
        Returns:
            Tuple of (prompt_string, temperature)
        """
        try:
            # Build context section for content transformation analysis
            from frameworks.prompt_context_builders import build_content_transformation_analysis_context
            context_section = build_content_transformation_analysis_context(content_samples, voice_traits, persona_insights, competitive_positioning)
            
            # Get prompt from new system
            prompt, config = prompt_system.get_prompt_with_config(
                "content_transformation_analysis",
                context_section=context_section
            )
            
            logger.info("Successfully used new prompt system for content transformation analysis")
            return prompt, config['temperature']
            
        except Exception as e:
            # Fallback content transformation analysis prompt
            if self.fallback_enabled:
                logger.warning(f"New prompt system failed, using fallback: {e}")
                
                fallback_prompt = f'''You are a professional content transformation specialist with expertise in brand voice implementation and content optimization. Your task is to analyze existing content samples against established voice traits, persona insights, and competitive positioning to identify transformation opportunities.

**CONTENT SAMPLES FOR ANALYSIS:**
{content_samples}

**VOICE TRAITS TO APPLY:**
{voice_traits}

**TARGET PERSONA INSIGHTS:**
{persona_insights}

**COMPETITIVE POSITIONING STRATEGY:**
{competitive_positioning}

**TRANSFORMATION ANALYSIS INSTRUCTIONS:**
1. Review each content sample against voice traits to identify alignment gaps
2. Evaluate optimization opportunities for target persona characteristics
3. Assess integration of competitive positioning and differentiation elements
4. Identify specific language, tone, and messaging improvements needed
5. Prioritize transformation opportunities by impact and complexity
6. Provide strategic recommendations for systematic content improvement

**OUTPUT FORMAT - JSON ONLY:**
{{
    "transformation_analysis": {{
        "analysis_summary": "Overall assessment of transformation opportunities",
        "content_samples_analyzed": 0,
        "total_improvements_identified": 0
    }},
    "content_transformations": [
        {{
            "original_content": "The exact original content sample",
            "content_type": "Type of content",
            "content_channel": "Where content appears",
            "improvement_opportunities": [
                {{
                    "category": "voice_trait_alignment|persona_optimization|competitive_positioning|tone_consistency",
                    "description": "What needs improvement",
                    "current_issue": "Specific problem",
                    "target_improvement": "What improved version should achieve"
                }}
            ],
            "priority_score": 0,
            "transformation_complexity": "low|medium|high"
        }}
    ],
    "strategic_recommendations": [
        {{
            "theme": "Improvement theme",
            "description": "Strategic recommendation",
            "applies_to_content_types": ["content types affected"],
            "implementation_priority": "high|medium|low"
        }}
    ]
}}

Return only the JSON object.'''
                
                return fallback_prompt, 0.6
            else:
                raise e
    
    def get_content_transformation_prompt(self, transformation_plan: str, voice_traits: str, persona_profile: str, competitive_insights: str, content_samples: str) -> Tuple[str, float]:
        """
        Get content transformation prompt for Content Rewriter workflow
        
        Args:
            transformation_plan: Analysis and recommendations from transformation analysis stage
            voice_traits: Voice traits and guidelines to apply
            persona_profile: Target persona characteristics
            competitive_insights: Competitive positioning strategy
            content_samples: Original content samples to transform
            
        Returns:
            Tuple of (prompt_string, temperature)
        """
        try:
            # Build context section for content transformation
            from frameworks.prompt_context_builders import build_content_transformation_context
            context_section = build_content_transformation_context(transformation_plan, voice_traits, persona_profile, competitive_insights, content_samples)
            
            # Get prompt from new system
            prompt, config = prompt_system.get_prompt_with_config(
                "content_transformation",
                context_section=context_section
            )
            
            logger.info("Successfully used new prompt system for content transformation")
            return prompt, config['temperature']
            
        except Exception as e:
            # Fallback content transformation prompt
            if self.fallback_enabled:
                logger.warning(f"New prompt system failed, using fallback: {e}")
                
                fallback_prompt = f'''You are a professional content transformation specialist with expertise in brand voice implementation and content optimization. Your task is to transform existing content samples by systematically applying voice traits, persona optimization, and competitive positioning insights.

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

**CONTENT TRANSFORMATION INSTRUCTIONS:**
1. Transform each content sample by applying voice traits systematically
2. Optimize language and messaging for target persona characteristics
3. Integrate competitive positioning insights and differentiation elements
4. Preserve core message intent while enhancing voice alignment
5. Create detailed before/after comparisons showing improvements
6. Document transformation patterns for consistent application
7. Ensure transformations maintain brand authenticity while improving effectiveness

**OUTPUT FORMAT - JSON ONLY:**
{{
    "transformation_results": {{
        "total_content_pieces": 0,
        "successful_transformations": 0,
        "transformation_summary": "Overview of outcomes"
    }},
    "transformed_content": [
        {{
            "content_id": "Unique identifier",
            "original_content": "Original content sample",
            "transformed_content": "Completely rewritten version",
            "content_type": "Type of content",
            "content_channel": "Where content appears",
            "voice_traits_applied": [
                {{
                    "trait_name": "Trait applied",
                    "application_method": "How implemented",
                    "before_example": "Original phrase",
                    "after_example": "Transformed phrase"
                }}
            ],
            "persona_optimizations": [
                {{
                    "persona_element": "Aspect addressed",
                    "optimization_description": "How optimized",
                    "language_changes": "Specific modifications"
                }}
            ],
            "competitive_positioning": {{
                "differentiation_applied": "How insights integrated",
                "positioning_elements": ["Key concepts incorporated"]
            }},
            "improvement_summary": "Overall transformation description",
            "quality_score": 0
        }}
    ],
    "transformation_patterns": [
        {{
            "pattern_name": "Transformation pattern type",
            "description": "What pattern addresses",
            "frequency": 0,
            "examples": ["Examples where applied"]
        }}
    ]
}}

Return only the JSON object.'''
                
                return fallback_prompt, 0.8
            else:
                raise e

    def get_brand_voice_guidelines_synthesis_prompt(self, brand_foundation: str, persona_profile: str, voice_traits: str, competitive_analysis: str, content_examples: str, workflow_summary: str) -> Tuple[str, float]:
        """
        Get brand voice guidelines synthesis prompt for Guidelines Finalizer workflow
        
        Args:
            brand_foundation: Brand foundation data from Brand Builder
            persona_profile: Detailed persona from Audience Definer
            voice_traits: Voice traits from Voice Traits Builder
            competitive_analysis: Strategic positioning from Gap Analyzer
            content_examples: Transformed content from Content Rewriter
            workflow_summary: Overview of all workflow steps and insights
            
        Returns:
            Tuple of (prompt_string, temperature)
        """
        try:
            # Build context section for guidelines synthesis
            from frameworks.prompt_context_builders import build_brand_voice_guidelines_synthesis_context
            context_section = build_brand_voice_guidelines_synthesis_context(brand_foundation, persona_profile, voice_traits, competitive_analysis, content_examples, workflow_summary)
            
            # Get prompt from new system
            prompt, config = prompt_system.get_prompt_with_config(
                "brand_voice_guidelines_synthesis",
                context_section=context_section
            )
            
            logger.info("Successfully used new prompt system for brand voice guidelines synthesis")
            return prompt, config['temperature']
            
        except Exception as e:
            # Fallback brand voice guidelines synthesis prompt
            if self.fallback_enabled:
                logger.warning(f"New prompt system failed, using fallback: {e}")
                
                fallback_prompt = f'''You are a professional brand guidelines synthesizer and documentation specialist with expertise in creating comprehensive, actionable brand voice guidelines. Your task is to synthesize all Deep Research Workflow insights into a complete, turnkey Brand Voice Guidelines document.

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

**GUIDELINES SYNTHESIS INSTRUCTIONS:**
1. Synthesize brand foundation, persona, and positioning into executive summary
2. Consolidate voice traits into clear Do/Don't framework with persona-specific examples
3. Adapt voice guidelines for different channels and content types
4. Integrate competitive positioning into differentiation strategy
5. Include reference examples from content transformations as quality standards
6. Create comprehensive implementation framework with step-by-step usage guide
7. Develop quality checklist and maintenance guidelines for long-term consistency
8. Provide quick reference section for immediate decision-making support

**OUTPUT FORMAT - JSON ONLY:**
{{
    "brand_voice_guidelines": {{
        "document_overview": {{
            "title": "Brand Voice Guidelines for [Client Name]",
            "version": "1.0",
            "created_date": "YYYY-MM-DD",
            "executive_summary": "Comprehensive overview",
            "usage_instructions": "How to use document"
        }},
        "brand_foundation": {{
            "mission_statement": "Clear mission",
            "core_values": ["Value 1", "Value 2"],
            "value_proposition": "Unique positioning",
            "brand_personality": ["Trait 1", "Trait 2"],
            "competitive_differentiation": "How we stand apart"
        }},
        "target_persona": {{
            "persona_name": "Primary persona",
            "demographic_summary": "Key characteristics",
            "communication_preferences": "Information preferences",
            "decision_making_factors": "Choice influences",
            "pain_points": ["Challenge 1", "Challenge 2"],
            "success_metrics": "Success definition"
        }},
        "voice_traits": [
            {{
                "trait_name": "Core trait name",
                "definition": "What trait means",
                "do_guidelines": ["Do example 1", "Do example 2"],
                "dont_guidelines": ["Don't example 1", "Don't example 2"],
                "persona_rationale": "Why this resonates",
                "application_contexts": ["When to emphasize"]
            }}
        ],
        "channel_adaptations": {{
            "website_content": {{
                "voice_emphasis": "Traits to emphasize",
                "tone_guidelines": "Tone recommendations",
                "language_level": "Complexity level",
                "content_themes": ["Theme 1", "Theme 2"]
            }},
            "social_media": {{
                "voice_emphasis": "Social traits",
                "tone_guidelines": "Social tone",
                "engagement_style": "Interaction style",
                "content_themes": ["Theme 1", "Theme 2"]
            }},
            "email_marketing": {{
                "voice_emphasis": "Email traits",
                "tone_guidelines": "Email tone",
                "personalization_approach": "Personalization method",
                "content_themes": ["Theme 1", "Theme 2"]
            }}
        }},
        "competitive_positioning": {{
            "market_landscape": "Competitive overview",
            "differentiation_strategy": "Voice differentiation",
            "messaging_priorities": ["Priority 1", "Priority 2"],
            "competitive_advantages": ["Advantage 1", "Advantage 2"],
            "positioning_statements": ["Statement 1", "Statement 2"]
        }},
        "reference_examples": [
            {{
                "content_type": "Content type",
                "original_content": "Before transformation",
                "improved_content": "After transformation",
                "voice_traits_demonstrated": ["Trait 1", "Trait 2"],
                "improvement_rationale": "Why this works"
            }}
        ],
        "implementation_framework": {{
            "step_by_step_guide": [
                {{
                    "step_number": 1,
                    "step_title": "Implementation step",
                    "step_description": "Detailed instructions",
                    "deliverables": ["What to produce"]
                }}
            ],
            "quality_assurance": {{
                "voice_checklist": ["Checkpoint 1", "Checkpoint 2"],
                "common_mistakes": ["Mistake 1", "Mistake 2"],
                "approval_criteria": "Publication readiness"
            }},
            "maintenance_guidelines": {{
                "regular_reviews": "Review frequency",
                "update_triggers": "When to update",
                "consistency_monitoring": "Consistency maintenance"
            }}
        }},
        "quick_reference": {{
            "voice_traits_summary": ["Trait 1: Description", "Trait 2: Description"],
            "persona_key_points": ["Key point 1", "Key point 2"],
            "dos_and_donts": {{
                "always_do": ["Do 1", "Do 2"],
                "never_do": ["Don't 1", "Don't 2"]
            }},
            "emergency_guidelines": "Quick guidance for urgent needs"
        }}
    }}
}}

Return only the JSON object.'''
                
                return fallback_prompt, 0.7
            else:
                raise e

    def get_strategic_gap_analysis_prompt(self, client_analysis: str, competitor_profiles: str, market_context: str, voice_traits: str) -> Tuple[str, float]:
        """Get strategic gap analysis prompt for Gap Analyzer Stage 3"""
        try:
            from frameworks.prompt_context_builders import build_strategic_gap_analysis_context
            context_section = build_strategic_gap_analysis_context(client_analysis, competitor_profiles, market_context, voice_traits)
            
            prompt, config = prompt_system.get_prompt_with_config("strategic_gap_analysis", context_section=context_section)
            logger.info("Successfully used new prompt system for strategic gap analysis")
            return prompt, config['temperature']
            
        except Exception as e:
            if self.fallback_enabled:
                logger.warning(f"New prompt system failed, using fallback: {e}")
                
                fallback_prompt = f'''You are a strategic positioning expert. Synthesize all competitive intelligence to develop winning positioning strategy.

**CLIENT ANALYSIS:**
{client_analysis}

**COMPETITOR PROFILES:**
{competitor_profiles}

**MARKET CONTEXT:**
{market_context}

**CLIENT VOICE TRAITS:**
{voice_traits}

**STRATEGIC SYNTHESIS INSTRUCTIONS:**
1. Compare client against all competitors to identify market patterns
2. Find messaging white space and differentiation opportunities  
3. Identify specific voice gaps that need addressing
4. Develop strategic positioning recommendations
5. Create prioritized action plan for competitive advantage

**OUTPUT FORMAT - JSON ONLY:**
{{
    "market_landscape_analysis": {{
        "competitive_overview": "Market landscape summary",
        "common_patterns": "What most competitors do similarly",
        "market_gaps": "Underserved areas or messaging white space"
    }},
    "competitive_positioning": {{
        "client_vs_competitors": "How client currently compares",
        "differentiation_opportunities": ["Specific ways to stand out"],
        "competitive_advantages": ["Client's unique strengths to leverage"]
    }},
    "voice_gap_recommendations": {{
        "critical_improvements": ["Most important voice changes"],
        "positioning_adjustments": ["How to adjust market positioning"],
        "strategic_priorities": ["What to focus on first"]
    }},
    "implementation_strategy": {{
        "immediate_actions": ["Quick wins to implement"],
        "long_term_strategy": "Overall competitive positioning approach",
        "success_metrics": "How to measure competitive progress"
    }}
}}

Return only the JSON object.'''
                
                return fallback_prompt, 0.7
            else:
                raise e


# Global instance for easy access throughout the application
# NOTE: This single instance provides consistent fallback behavior
prompt_wrapper = PromptWrapper()