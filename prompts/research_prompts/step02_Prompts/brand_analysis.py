"""
Brand Analysis Prompts for Step 2
Deep brand voice and personality analysis based on website data
"""

def get_brand_analysis_prompt(client_name, website_data, extracted_content):
    """
    Generate comprehensive brand analysis prompt
    
    Args:
        client_name: Name of the client
        website_data: Extracted website analysis from Step 1
        extracted_content: Raw content extracted from website
    
    Returns:
        str: Formatted prompt for brand analysis
    """
    
    # Convert complex data to readable format
    industry = website_data.get("Industry", "Not specified")
    company_description = website_data.get("Company_Description", "Not available")
    brand_mission = website_data.get("Brand_Mission", "Not specified")
    brand_values = website_data.get("Brand_Values", "Not specified")
    target_audience = website_data.get("Target_Audience", "Not specified")
    products_services = website_data.get("Product_Service_Description", "Not specified")
    
    prompt = f"""
You are an expert brand strategist and voice analyst. Analyze the following company data and website content to create a comprehensive brand voice profile.

COMPANY: {client_name}

CURRENT DATA FROM WEBSITE:
- Industry: {industry}
- Company Description: {company_description}
- Brand Mission: {brand_mission}
- Brand Values: {brand_values}
- Target Audience: {target_audience}
- Products/Services: {products_services}

WEBSITE CONTENT SAMPLES:
{extracted_content[:5000]}  # Limit to first 5000 chars

TASK: Analyze this information to create a deep brand voice profile. Focus on:
1. How they currently communicate
2. Their brand personality traits
3. Emotional tone and impact
4. Language patterns and characteristics
5. What makes their voice unique

PROVIDE YOUR ANALYSIS IN THIS JSON FORMAT:
{{
    "brand_voice_analysis": {{
        "current_voice_description": "Comprehensive description of how they currently communicate",
        "formality_level": "Formal/Semi-formal/Casual/Conversational",
        "technical_level": "Highly technical/Moderate/Accessible to layperson",
        "overall_tone": ["List", "3-5", "dominant", "tones"]
    }},
    
    "brand_personality": {{
        "primary_traits": ["List", "5-7", "personality", "traits"],
        "brand_archetype": "Primary archetype (e.g., Hero, Sage, Creator, etc.)",
        "personality_description": "How the brand comes across to audiences"
    }},
    
    "communication_characteristics": {{
        "voice_attributes": ["List", "key", "voice", "characteristics"],
        "language_patterns": "Description of language patterns and style",
        "signature_phrases": ["Any", "recurring", "phrases", "or", "expressions"],
        "vocabulary_level": "Simple/Moderate/Advanced/Technical"
    }},
    
    "emotional_impact": {{
        "desired_emotions": ["Emotions", "they", "aim", "to", "evoke"],
        "emotional_journey": "How they guide audience emotions",
        "connection_strategy": "How they build emotional connection"
    }},
    
    "differentiation": {{
        "unique_voice_elements": "What makes their voice distinctive",
        "competitive_positioning": "How their voice sets them apart",
        "memorable_aspects": ["Most", "memorable", "voice", "characteristics"]
    }},
    
    "content_themes": {{
        "primary_themes": ["Main", "content", "themes"],
        "messaging_priorities": ["Key", "messages", "they", "emphasize"],
        "avoided_topics": ["Topics", "or", "tones", "they", "avoid"]
    }},
    
    "recommendations": {{
        "voice_strengths": ["Current", "voice", "strengths"],
        "improvement_areas": ["Areas", "for", "enhancement"],
        "consistency_notes": "Notes on voice consistency across content"
    }}
}}

Ensure your analysis is based on actual evidence from the content provided. Be specific and actionable.
"""
    
    return prompt


def get_brand_synthesis_prompt(brand_analysis, website_data):
    """
    Create synthesis prompt to combine brand analysis with existing data
    
    Args:
        brand_analysis: Results from brand voice analysis
        website_data: Original website extraction data
    
    Returns:
        str: Synthesis prompt
    """
    
    prompt = f"""
Synthesize the following brand analysis with existing company data to create a unified brand profile.

BRAND ANALYSIS:
{brand_analysis}

EXISTING DATA:
{website_data}

Create a cohesive brand profile that combines both analyses into actionable brand guidelines.
Focus on practical application and consistency.

Return a JSON object with synthesized brand guidelines.
"""
    
    return prompt