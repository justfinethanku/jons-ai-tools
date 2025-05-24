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


# Global instance for easy access throughout the application
# NOTE: This single instance provides consistent fallback behavior
prompt_wrapper = PromptWrapper()