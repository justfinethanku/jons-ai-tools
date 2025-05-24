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