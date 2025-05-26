import json

# Schema remains the same as in your original code
def get_analysis_schema_optimized():
    """
    Returns the enhanced schema for comprehensive business analysis
    """
    return {
        # Basic Information
        "industry": "Specific business sector/industry (be precise, e.g., 'B2B SaaS for Healthcare' not just 'Technology', 'Wedding and Portrait Photography' not just 'Photography')",
        "company_description": "Comprehensive 3-4 sentence description capturing what they do, who they do it for, how they do it, and what makes them unique. Synthesize from all available text.",
        "key_products_services": [{"service_name": "Name of Service/Product", "description": "Brief 1-2 sentence description"}], # List ALL primary services/products

        # Contact Information
        "contact_email": "Primary business email (e.g., info@, contact@, hello@). Prioritize generic over personal if multiple found.",
        "phone_number": "Primary phone with country/area code. Standardize format if possible (e.g., +1-XXX-XXX-XXXX).",
        "address": "Complete physical address including street, city, state/province, postal code, country. If multiple, list primary or headquarters.",

        # Social Media Presence
        "linkedin_url": "Full LinkedIn company page URL (e.g., https://www.linkedin.com/company/companyname).",
        "twitter_url": "Full Twitter/X URL (e.g., https://twitter.com/username or https://x.com/username).",
        "facebook_url": "Full Facebook page URL (e.g., https://www.facebook.com/pagename).",
        "instagram_url": "Full Instagram URL (e.g., https://www.instagram.com/username).",
        "youtube_url": "Full YouTube channel URL (e.g., https://www.youtube.com/channel/UC... or /c/... or /user/...).",
        "other_social_media": [{"platform_name": "e.g., Pinterest, TikTok", "url": "Full URL"}],

        # Brand Identity
        "brand_mission": "Exact mission statement or clearly stated purpose. Quote if possible. If not explicit, infer and note as 'Inferred Mission:'.",
        "brand_values": [{"value_name": "Core Value Name", "description": "Any accompanying description or examples provided."}], # List each core value
        "value_proposition": "Unique value proposition - what specific problem(s) they solve for their customers and how they do it better or differently. Synthesize if not explicit.",
        "brand_personality_traits": ["List 3-5 adjectives based on language, tone, and imagery (e.g., 'Elegant', 'Playful', 'Authoritative', 'Empathetic', 'Innovative', 'Reliable'). Provide brief justification if not obvious."],

        # Target Market
        "target_audience": {
            "primary": "Describe the main target customer/client with specifics (e.g., 'Engaged couples in the Pacific Northwest seeking documentary-style wedding photography', 'Small to medium-sized e-commerce businesses needing payment processing').",
            "secondary": "Secondary audiences if clearly mentioned or strongly implied.",
            "pain_points_addressed": ["List specific problems, frustrations, or desires of the target audience that the company's offerings solve. (e.g., 'Fear of awkward, posed photos', 'Difficulty finding a reliable photographer', 'Desire for timeless memories')."]
        },

        # Company Details (Infer if not explicitly stated)
        "company_size_indicators": {
            "employee_count": "Specific number (e.g., '15 employees') or range (e.g., '1-10 employees', 'Solo entrepreneur'). Infer from language like 'our team', 'we', 'I'.",
            "office_locations": ["List all mentioned physical office or studio locations. If home-based or service-area based, note that (e.g., 'Serves the Austin, TX area')."],
            "years_in_business": "Founded year, date, or number of years operating. (e.g., 'Founded in 2015', 'Over 10 years of experience')."
        },

        # Messaging & Tone
        "key_messaging_themes": { # Renamed from key_messaging for clarity
            "tagline_slogan": "Main tagline or slogan if present. Look in headers, hero sections.",
            "recurring_phrases_keywords": ["List distinctive phrases or keywords used repeatedly that define their brand or offerings."],
            "unique_terminology_or_brand_names": ["Industry-specific jargon they use, or unique names for their services/processes."]
        },

        # Voice & Style Indicators
        "communication_style": {
            "formality_level": "Choose one: Formal / Semi-formal / Casual / Conversational. Justify briefly.",
            "technical_level": "Choose one: Highly technical / Moderate / Accessible to layperson. Justify briefly.",
            "overall_tone": ["List 2-3 dominant emotional tones conveyed (e.g., 'Empathetic', 'Confident', 'Playful', 'Reassuring', 'Professional', 'Passionate')."]
        },

        # Credibility Markers
        "awards_recognition_affiliations": ["List specific awards, certifications, publications featured in, or professional affiliations mentioned."],
        "testimonial_themes_or_keywords": ["Common positive themes, keywords, or outcomes mentioned in client testimonials or reviews if present/summarized. (e.g., 'Easy to work with', 'High-quality results', 'Professionalism')."],
        "key_differentiators_claimed": ["What do they explicitly state makes them different or better than competitors? (e.g., 'Our unique artistic style', '24/7 customer support', 'Sustainable practices'). Synthesize if necessary."]
    }

def get_comprehensive_analysis_prompt(client_name, website_url, full_website_text):
    """
    Optimized comprehensive website analysis prompt for extracting business information,
   
    IMPORTANT: full_website_text should be the *aggregated text content* from key pages
    (About, Services, Contact, etc.), not just a brief summary.
    """
    schema = get_analysis_schema_optimized()
    
    # --- FEW-SHOT EXAMPLE (Illustrative - for a hypothetical Photography Website) ---
    # This helps llm understand the desired level of detail and how to handle "Not found"
    few_shot_example_text = """
    // --- START OF FEW-SHOT EXAMPLE (Content for a hypothetical 'Lumina Photography') ---
    // {
    //   "industry": "Wedding and Family Photography Services",
    //   "company_description": "Lumina Photography, led by Jane Doe, specializes in capturing authentic, light-filled moments for weddings and families in the Northern California region. We believe in telling your unique story through timeless, emotive imagery. Our approach is personal and collaborative, ensuring a relaxed experience and beautiful, natural photographs.",
    //   "key_products_services": [
    //     {"service_name": "Wedding Photography", "description": "Full-day coverage, from getting ready to the final dance. Includes an online gallery and high-resolution images. Engagement sessions available."},
    //     {"service_name": "Family Portraits", "description": "Outdoor or in-home lifestyle sessions for families, newborns, and maternity. Focus on capturing genuine interactions."}
    //   ],
    //   "contact_email": "hello@luminaphoto.com",
    //   "phone_number": "+1-555-123-4567",
    //   "address": "Serves Northern California (Based in Sacramento, CA)",
    //   "linkedin_url": "Not found",
    //   "twitter_url": "Not found",
    //   "facebook_url": "https://www.facebook.com/LuminaPhotographyPage",
    //   "instagram_url": "https://www.instagram.com/luminaphoto_jane",
    //   "youtube_url": "Not found",
    //   "other_social_media": [],
    //   "brand_mission": "To artfully capture the genuine joy and connection of life's most cherished milestones.",
    //   "brand_values": [
    //      {"value_name": "Authenticity", "description": "We strive for real moments, not forced poses."},
    //      {"value_name": "Connection", "description": "Building a rapport with our clients is key to our process."}
    //   ],
    //   "value_proposition": "Lumina Photography offers a personalized and stress-free experience, delivering natural, light-filled wedding and family photos that authentically tell your story.",
    //   "brand_personality_traits": ["Warm", "Artistic", "Authentic", "Personal"],
    //   "target_audience": {
    //     "primary": "Engaged couples and young families in Northern California (e.g., Sacramento, Bay Area) who value candid, emotional, and high-quality photography and prefer a personal, boutique experience.",
    //     "secondary": "Individuals seeking maternity or newborn lifestyle portraits.",
    //     "pain_points_addressed": ["Fear of awkward or cheesy photos", "Wanting a photographer who is easy to work with and understands their vision", "Desire for timeless images that capture real emotions"]
    //   },
    //   "company_size_indicators": {
    //     "employee_count": "Solo entrepreneur (Jane Doe) potentially with occasional second shooters/assistants.",
    //     "office_locations": ["Based in Sacramento, CA; Serves Northern California."],
    //     "years_in_business": "Established in 2018"
    //   },
    //   "key_messaging_themes": {
    //     "tagline_slogan": "Capturing Light, Telling Stories.",
    //     "recurring_phrases_keywords": ["authentic moments", "natural light", "timeless imagery", "storytelling", "cherished memories"],
    //     "unique_terminology_or_brand_names": ["Lumina Experience (implied for their client interaction)"]
    //   },
    //   "communication_style": {
    //     "formality_level": "Semi-formal to Conversational. Professional yet warm and approachable.",
    //     "technical_level": "Accessible to layperson. Explains photographic concepts simply if at all.",
    //     "overall_tone": ["Warm", "Emotive", "Reassuring", "Passionate"]
    //   },
    //   "awards_recognition_affiliations": ["Featured on 'The Knot'", "Member of PPA (Professional Photographers of America) - Inferred if PPA logo present"],
    //   "testimonial_themes_or_keywords": ["Made us feel comfortable", "Captured the day perfectly", "Beautiful photos", "Professional and friendly"],
    //   "key_differentiators_claimed": ["Focus on authentic emotion over trends", "Use of natural light", "Personalized client experience"]
    // }
    // --- END OF FEW-SHOT EXAMPLE ---
    """

    return f"""You are an expert AI Business Analyst. Your mission is to meticulously extract and synthesize comprehensive business information from the provided website content to construct a detailed brand profile. You are exceptionally skilled at deep analysis, inference, and pattern recognition.

COMPANY: {client_name}
WEBSITE URL (for context): {website_url}

WEBSITE CONTENT TO ANALYZE (This is the FULL TEXT from key pages like About, Services, Contact, etc.):
<WEBSITE_CONTENT_START>
{full_website_text}
<WEBSITE_CONTENT_END>

EXTRACTION SCHEMA AND INSTRUCTIONS:
Your output MUST be a single, valid JSON object matching the schema below.
Every key from the schema MUST be present in your output.

AGGRESSIVE INFORMATION SEEKING & INFERENCE RULES:
1.  **Exhaustive Search:** Scrutinize ALL provided `WEBSITE CONTENT TO ANALYZE`. Information might be in headers, footers, body text, image captions (if text available), or testimonials.
2.  **Implicit Information:** Do not just look for explicit statements. INFER information from language, tone, examples, structure, and imagery descriptions (if available).
    *   Example: If they only show photos of weddings and describe wedding packages, `industry` includes "Wedding Photography".
    *   Example: If language is "we" and "our team," `employee_count` is likely not "Solo." If "I" and "my," it's likely "Solo."
3.  **"Not found" as Last Resort:** Use "Not found" ONLY if, after an exhaustive search and genuine attempt at inference, the information is TRULY ABSENT or COMPLETELY UNINFERABLE.
    *   For optional fields or list items where nothing is found, use an empty string `""` for single text fields, an empty list `[]` for lists of strings/objects, or appropriate null-like values if the schema implies (e.g. `null` for some object sub-fields if truly nothing). However, the schema provided above prefers empty strings/lists.
4.  **Specificity is Key:** Be as precise as possible. For `industry`, "Luxury Wedding Photography in New York" is better than "Photography."
5.  **Capture Actual Language:** For fields like `brand_mission`, `recurring_phrases_keywords`, quote directly when possible or paraphrase closely.
6.  **Social Media URLs:** Extract FULL URLs. Look for common patterns:
    *   LinkedIn: `linkedin.com/company/...` or `linkedin.com/in/...` (prioritize company)
    *   Twitter/X: `twitter.com/...` or `x.com/...`
    *   Facebook: `facebook.com/...`
    *   Instagram: `instagram.com/...`
    *   YouTube: `youtube.com/channel/...`, `youtube.com/c/...`, `youtube.com/user/...`
7.  **Contact Information:** Find primary contact details. Standardize phone numbers if possible (e.g., +1-XXX-XXX-XXXX). If multiple emails, prioritize generic ones (info@, contact@) over personal ones for the main `contact_email`.
8.  **Synthesize:** For fields like `company_description` or `value_proposition`, synthesize information from multiple parts of the text into a coherent statement.
9.  **Fault Tolerance for Schema:**
    *   If a field expects a list (e.g., `key_products_services`) and no items are found, return an empty list: `[]`.
    *   If a field expects a string and nothing is found after all efforts, use "Not found".
    *   Ensure all fields from the schema are present.

OUTPUT SCHEMA (Pay close attention to data types - string, list of strings, list of objects, nested objects):
{json.dumps(schema, indent=2)}

FEW-SHOT EXAMPLE (This demonstrates the desired output style and detail for a hypothetical photography business. Adapt its principles to the current company):
{few_shot_example_text}

Provide ONLY the single, valid JSON object containing all extracted information. Do not include any explanatory text before or after the JSON.
"""