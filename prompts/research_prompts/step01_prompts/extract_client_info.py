"""
Extract Client Info Prompts
Prompts for analyzing website content and extracting comprehensive business information
"""

import json

def get_comprehensive_analysis_prompt(client_name, website_url, content_summary):
    """
    Comprehensive website analysis prompt for extracting business information
    """
    schema = get_analysis_schema()
    
    return f"""You are a business analyst extracting company information from website content.

COMPANY: {client_name}
WEBSITE: {website_url}

WEBSITE CONTENT TO ANALYZE:
{content_summary}

Extract the following information as JSON:
{json.dumps(schema, indent=2)}

Rules:
- Extract exact information when found
- Use "Not found" only when information is genuinely missing
- Be accurate, not creative
- Return only valid JSON

JSON OUTPUT:"""

def get_analysis_schema():
    """
    Returns the standard schema for business analysis
    """
    return {
        "industry": "Specific business sector/industry",
        "company_description": "Clear 2-3 sentence description of what the company does",
        "key_products_services": ["Primary service/product 1", "Primary service/product 2"],
        "contact_email": "Primary business email or 'Not found'",
        "phone_number": "Primary phone number or 'Not found'",
        "address": "Complete business address or 'Not found'",
        "linkedin_url": "Full LinkedIn URL or 'Not found'",
        "twitter_url": "Full Twitter/X URL or 'Not found'",
        "facebook_url": "Full Facebook URL or 'Not found'",
        "instagram_url": "Full Instagram URL or 'Not found'",
        "youtube_url": "Full YouTube URL or 'Not found'",
        "other_social_media": ["Additional social platform URLs"],
        "brand_mission": "Company mission statement or purpose",
        "brand_values": "Core company values mentioned",
        "value_proposition": "Unique value proposition or competitive advantage",
        "target_audience": "Primary target audience or customer segments",
        "company_size_indicators": "Indicators of company size (team mentions, office locations, etc.)",
        "geographical_presence": "Locations served or office locations",
        "key_messaging": "Primary marketing messages or taglines",
        "company_culture": "Company culture or personality indicators",
        "awards_recognition": "Any awards, certifications, or recognition mentioned"
    }