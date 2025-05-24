"""
Context Gatherer Tool - First step in the research workflow.
Collects foundational client information and brand attributes.
Allows creating new clients and enhancing existing ones.
"""

import streamlit as st
import json
import requests
from bs4 import BeautifulSoup
import trafilatura
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frameworks import universal_framework, research_tools_framework

def extract_targeted_content(base_url):
    """
    Extract content from multiple targeted pages on a website
    
    Args:
        base_url (str): The base URL of the website
        
    Returns:
        dict: Dictionary containing content from different pages
    """
    content_sections = {}
    
    # Target pages to scrape
    target_pages = {
        'homepage': '',
        'about': ['/about', '/about-us', '/company', '/who-we-are'],
        'contact': ['/contact', '/contact-us', '/get-in-touch'],
        'mission': ['/mission', '/values', '/vision', '/purpose'],
        'services': ['/services', '/what-we-do', '/solutions', '/products']
    }
    
    # Normalize base URL
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'https://' + base_url
    base_url = base_url.rstrip('/')
    
    for section, paths in target_pages.items():
        content = None
        
        if section == 'homepage':
            # Extract homepage content
            content = extract_content_from_url(base_url)
        else:
            # Try different path variations
            for path in paths:
                url = base_url + path
                temp_content = extract_content_from_url(url)
                if temp_content and not temp_content.startswith("Error"):
                    content = temp_content
                    break
        
        if content and not content.startswith("Error"):
            # Limit content length per section
            if len(content) > 2000:
                content = content[:2000] + "...[truncated]"
            content_sections[section] = content
    
    return content_sections

def extract_content_from_url(url):
    """
    Extract text content from a URL
    
    Args:
        url (str): The URL to extract content from
        
    Returns:
        str: The extracted text content
    """
    try:
        # Use trafilatura for effective text extraction (handles most modern websites well)
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            # Extract with more comprehensive options to capture contact info
            extracted_text = trafilatura.extract(downloaded, 
                                               include_comments=False, 
                                               include_tables=True,  # Include tables (often contain contact info)
                                               include_links=True)   # Include links (social media)
            if extracted_text:
                # Also extract contact information patterns using BeautifulSoup
                soup = BeautifulSoup(downloaded, 'html.parser')
                
                # Look for common contact information patterns
                contact_patterns = []
                
                # Find email addresses in href attributes
                email_links = soup.find_all('a', href=True)
                for link in email_links:
                    if 'mailto:' in link['href']:
                        contact_patterns.append(f"Email found: {link['href'].replace('mailto:', '')}")
                
                # Find phone links
                phone_links = soup.find_all('a', href=True)
                for link in phone_links:
                    if 'tel:' in link['href']:
                        contact_patterns.append(f"Phone found: {link['href'].replace('tel:', '')}")
                
                # Find social media links
                social_domains = ['linkedin.com', 'twitter.com', 'facebook.com', 'instagram.com', 'youtube.com', 'tiktok.com']
                social_links = soup.find_all('a', href=True)
                for link in social_links:
                    for domain in social_domains:
                        if domain in link['href']:
                            contact_patterns.append(f"Social media found: {link['href']}")
                            break
                
                # Add contact patterns to extracted text
                if contact_patterns:
                    extracted_text += "\n\n=== EXTRACTED CONTACT INFORMATION ===\n" + "\n".join(contact_patterns)
                
                return extracted_text
        
        # Fallback to BeautifulSoup if trafilatura fails
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract() 
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines()) 
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Extract contact information patterns from text
            import re
            contact_info = []
            
            # Find email patterns in text
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            for email in set(emails):  # Remove duplicates
                contact_info.append(f"Email pattern found: {email}")
            
            # Find phone patterns
            phone_patterns = [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # XXX-XXX-XXXX or XXX.XXX.XXXX
                r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',    # (XXX) XXX-XXXX
                r'\+1[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{4}'  # +1-XXX-XXX-XXXX
            ]
            for pattern in phone_patterns:
                phones = re.findall(pattern, text)
                for phone in set(phones):  # Remove duplicates
                    contact_info.append(f"Phone pattern found: {phone}")
            
            # Find social media URLs in text
            social_patterns = [
                r'https?://(?:www\.)?linkedin\.com/[^\s]+',
                r'https?://(?:www\.)?twitter\.com/[^\s]+',
                r'https?://(?:www\.)?facebook\.com/[^\s]+',
                r'https?://(?:www\.)?instagram\.com/[^\s]+',
                r'https?://(?:www\.)?youtube\.com/[^\s]+',
                r'https?://(?:www\.)?tiktok\.com/[^\s]+'
            ]
            for pattern in social_patterns:
                social_urls = re.findall(pattern, text)
                for url in set(social_urls):  # Remove duplicates
                    contact_info.append(f"Social media URL found: {url}")
            
            if contact_info:
                text += "\n\n=== CONTACT PATTERNS DETECTED ===\n" + "\n".join(contact_info)
            
            return text
        else:
            return f"Error: Unable to access the URL (Status code: {response.status_code})"
    except Exception as e:
        return f"Error extracting content from URL: {str(e)}"

def extract_website_data(client_name, website_url):
    """
    Step 1: Extract basic company information and contact details from website using enhanced multi-content approach
    """
    try:
        # Extract targeted content from multiple pages
        content_sections = extract_targeted_content(website_url)
        
        if not content_sections:
            return False, {}, "Could not extract content from website"
        
        # Build multi-content input structure
        content_input = "=== WEBSITE CONTENT ANALYSIS ===\n\n"
        
        for section, content in content_sections.items():
            if content:
                # Clean content for each section
                clean_content = content.replace('"', "'").replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                content_input += f"=== {section.upper()} PAGE ===\n{clean_content}\n\n"
        
        # Enhanced extraction prompt with role definition and structured guidance
        prompt = f"""You are a professional business analyst specializing in company research and data extraction. Your task is to extract structured company information from website content with high accuracy and completeness.

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
{{
  "industry": "Primary business sector/industry (be specific)",
  "company_description": "Clear 2-3 sentence description of what the company does",
  "key_products_services": ["Service 1", "Service 2", "Product 3"],
  "contact_email": "Primary business email or 'Not found'",
  "phone_number": "Primary phone number or 'Not found'",
  "address": "Complete business address or 'Not found'",
  "linkedin_url": "Full LinkedIn URL or 'Not found'",
  "twitter_url": "Full Twitter/X URL or 'Not found'",
  "facebook_url": "Full Facebook URL or 'Not found'",
  "instagram_url": "Full Instagram URL or 'Not found'",
  "youtube_url": "Full YouTube URL or 'Not found'",
  "other_social_media": ["Additional social platform URLs"],
  "target_markets": ["Market 1", "Market 2"],
  "company_size_indicators": "Small/Medium/Large business indicators found",
  "geographical_presence": "Locations served or mentioned"
}}

Extract and return ONLY the JSON object above."""
        
        schema = {
            "type": "object",
            "properties": {
                "industry": {"type": "string"},
                "company_description": {"type": "string"},
                "key_products_services": {"type": "array", "items": {"type": "string"}},
                "contact_email": {"type": "string"},
                "phone_number": {"type": "string"},
                "address": {"type": "string"},
                "linkedin_url": {"type": "string"},
                "twitter_url": {"type": "string"},
                "facebook_url": {"type": "string"},
                "instagram_url": {"type": "string"},
                "youtube_url": {"type": "string"},
                "other_social_media": {"type": "array", "items": {"type": "string"}},
                "target_markets": {"type": "array", "items": {"type": "string"}},
                "company_size_indicators": {"type": "string"},
                "geographical_presence": {"type": "string"}
            },
            "required": ["industry", "company_description", "key_products_services"]
        }
        
        # Use lower temperature for extraction accuracy
        response = universal_framework.call_gemini_api(prompt, response_schema=schema, temperature=0.3)
        result_data = json.loads(response)
        return True, result_data, None
            
    except Exception as e:
        return False, {}, f"Website extraction failed: {str(e)}"

def analyze_brand_voice(client_name, website_data, form_data=None):
    """
    Step 2: Comprehensive brand voice analysis using enhanced methodology
    """
    try:
        # Build rich input from website data
        website_context = f"""
**COMPANY OVERVIEW:**
- Name: {client_name}
- Industry: {website_data.get('industry', 'Unknown')}
- Description: {website_data.get('company_description', 'Not available')}
- Products/Services: {', '.join(website_data.get('key_products_services', []))}
- Target Markets: {', '.join(website_data.get('target_markets', []))}
- Geographical Presence: {website_data.get('geographical_presence', 'Not specified')}
- Company Size Indicators: {website_data.get('company_size_indicators', 'Not specified')}"""
        
        # Enhanced brand analysis prompt with methodology guidance
        prompt = f"""You are a senior brand strategist with expertise in developing comprehensive brand voice profiles. Your task is to analyze the provided company information and develop a strategic brand voice framework.

{website_context}

**ANALYSIS METHODOLOGY:**
1. **Industry Context Analysis**: Consider industry norms, competitive landscape, and communication expectations
2. **Audience Segmentation**: Identify current vs. ideal audiences with specific demographic and psychographic profiles
3. **Brand Positioning**: Determine unique value proposition and market differentiation
4. **Voice Architecture**: Develop personality traits, values, and communication guidelines
5. **Strategic Recommendations**: Provide actionable guidance for brand expression

**BRAND VOICE FRAMEWORK TO DEVELOP:**

Return ONLY a valid JSON object. Do not include any explanatory text before or after the JSON.

{{
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
}}

Provide strategic, actionable insights based on the company analysis."""
        
        # Add existing form data if available
        if form_data:
            known_info = [f"{k.replace('_', ' ').title()}: {v}" for k, v in form_data.items() if v and k not in ['website', 'industry']]
            if known_info:
                prompt += f"\n\n**EXISTING BRAND INFORMATION TO ENHANCE:**\n" + "\n".join(known_info)
        
        schema = {
            "type": "object",
            "properties": {
                "current_target_audience": {"type": "string"},
                "ideal_target_audience": {"type": "string"},
                "brand_values": {"type": "array", "items": {"type": "string"}},
                "brand_mission": {"type": "string"},
                "value_proposition": {"type": "string"},
                "brand_personality_traits": {"type": "array", "items": {"type": "string"}},
                "communication_tone": {"type": "string"},
                "voice_characteristics": {"type": "array", "items": {"type": "string"}},
                "language_level": {"type": "string"},
                "desired_emotional_impact": {"type": "array", "items": {"type": "string"}},
                "brand_archetypes": {"type": "array", "items": {"type": "string"}},
                "competitive_differentiation": {"type": "string"},
                "content_themes": {"type": "array", "items": {"type": "string"}},
                "words_tones_to_avoid": {"type": "array", "items": {"type": "string"}},
                "messaging_priorities": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["current_target_audience", "ideal_target_audience", "brand_values", "brand_mission", "brand_personality_traits"]
        }
        
        # Use higher temperature for creative brand analysis
        response = universal_framework.call_gemini_api(prompt, response_schema=schema, temperature=0.7)
        
        # Enhanced JSON parsing with error handling
        try:
            # Clean the response
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            result_data = json.loads(clean_response)
        except json.JSONDecodeError as e:
            # Try to extract JSON from response with better pattern matching
            import re
            # Look for JSON object starting with { and ending with }
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if not json_match:
                # Fallback: look for any content between first { and last }
                start_idx = response.find('{')
                end_idx = response.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_text = response[start_idx:end_idx+1]
                    try:
                        result_data = json.loads(json_text)
                    except json.JSONDecodeError:
                        return False, {}, f"Invalid JSON structure: {str(e)}"
                else:
                    return False, {}, f"No JSON structure found in response: {response[:200]}..."
            else:
                try:
                    result_data = json.loads(json_match.group())
                except json.JSONDecodeError:
                    return False, {}, f"Invalid JSON format: {str(e)}"
        
        # Combine with website data
        final_data = {**website_data, **result_data}
        return True, final_data, None
            
    except Exception as e:
        return False, {}, f"Brand voice analysis failed: {str(e)}"

def comprehensive_client_analysis(client_name, industry, website_url=None, form_data=None, optimize_content=True):
    """
    Two-step analysis process: Extract website data, then analyze brand voice
    
    Args:
        client_name: The name of the client
        industry: The industry of the client 
        website_url: Optional URL to the client's website
        form_data: Optional existing form data to fill gaps
        optimize_content: Whether to optimize content for next steps
        
    Returns:
        tuple: (success: bool, result_data: dict, error_message: str)
    """
    try:
        # Step 1: Extract website data if URL provided
        website_data = {}
        if website_url:
            with st.spinner("Step 1: Extracting company data from website..."):
                step1_success, website_data, step1_error = extract_website_data(client_name, website_url)
                if not step1_success:
                    return False, {}, f"Step 1 failed: {step1_error}"
                st.success("✅ Step 1 complete: Company data extracted")
        
        # Step 2: Analyze brand voice
        with st.spinner("Step 2: Analyzing brand voice and strategy..."):
            step2_success, final_data, step2_error = analyze_brand_voice(client_name, website_data, form_data)
            if not step2_success:
                return False, website_data, f"Step 2 failed: {step2_error}"
            st.success("✅ Step 2 complete: Brand voice analysis finished")
        
        return True, final_data, None
        
    except Exception as e:
        return False, {}, f"Analysis failed: {str(e)}"

def update_client_with_retry(db_manager, client_page_id, notion_data, max_retries=3):
    """
    Update client profile in Notion with retry logic
    
    Args:
        db_manager: NotionDatabaseManager instance
        client_page_id: ID of the client page
        notion_data: Data to update
        max_retries: Maximum number of retry attempts
        
    Returns:
        tuple: (success: bool, error_message: str)
    """
    for attempt in range(max_retries):
        try:
            success = db_manager.update_client_profile(client_page_id, notion_data)
            if success:
                return True, None
            else:
                error_msg = f"Update failed on attempt {attempt + 1}/{max_retries}"
                if attempt == max_retries - 1:
                    return False, "Failed to update client profile after all retry attempts"
        except Exception as e:
            error_msg = f"Exception on attempt {attempt + 1}/{max_retries}: {str(e)}"
            if attempt == max_retries - 1:
                return False, f"Failed to update client profile: {str(e)}"
            st.warning(f"Retrying update... ({attempt + 1}/{max_retries})")
    
    return False, "Unexpected error in retry logic"

def get_fixed_context_gatherer_schema():
    """
    Get a fixed schema for Context Gatherer structured output
    (without the propertyOrdering field that causes issues)
    """
    return {
        "type": "object",
        "properties": {
            "business_name": {"type": "string", "description": "The name of the business"},
            "website": {"type": "string", "description": "The website URL of the business"},
            "industry": {"type": "string", "description": "The industry sector of the business"},
            "product_service_description": {"type": "string", "description": "Description of what the client offers"},
            "current_target_audience": {"type": "string", "description": "Who the client currently reaches"},
            "ideal_target_audience": {"type": "string", "description": "Who the client ideally wants to reach"},
            "brand_values": {"type": "string", "description": "Core principles that guide the brand (comma-separated)"},
            "brand_mission": {"type": "string", "description": "The brand's purpose or reason for existing"},
            "desired_emotional_impact": {"type": "string", "description": "How audience should feel (comma-separated)"},
            "brand_personality": {"type": "string", "description": "3-5 adjectives describing the brand as a person"},
            "words_tones_to_avoid": {"type": "string", "description": "Language or topics to stay away from"},
            "contact_email": {"type": "string", "description": "Primary contact email address"},
            "phone_number": {"type": "string", "description": "Primary phone number"},
            "address": {"type": "string", "description": "Physical business address"},
            "linkedin_url": {"type": "string", "description": "LinkedIn profile or company page"},
            "twitter_url": {"type": "string", "description": "Twitter/X profile"},
            "facebook_url": {"type": "string", "description": "Facebook page"},
            "instagram_url": {"type": "string", "description": "Instagram profile"},
            "other_social_media": {"type": "string", "description": "Other social media profiles"}
        },
        "required": [
            "business_name", 
            "industry",  
            "product_service_description",
            "current_target_audience",
            "ideal_target_audience",
            "brand_values", 
            "brand_mission",
            "desired_emotional_impact", 
            "brand_personality" 
        ]
    }

def run_context_gatherer():
    st.title("Context Gatherer")
    st.write("Collect foundational client information and brand attributes")
    
    # Initialize Notion database manager
    db_manager = research_tools_framework.NotionDatabaseManager()
    
    # Client selector sidebar with option to create new clients
    client_page_id, selected_client, status = research_tools_framework.client_selector_sidebar(
        db_manager=db_manager, 
        allow_new_client=True
    )
    
    if not client_page_id:
        st.info("Please select a client from the sidebar or create a new one to get started.")
        
        # Show instructions for new users
        with st.expander("How to use the Context Gatherer"):
            st.markdown("""
            ### Getting Started
            
            The Context Gatherer is the first step in developing a client's brand voice. Here's how to use it:
            
            1. **Create a new client** using the sidebar dropdown
            2. **Fill in the client information** form with as much detail as possible
            3. **Generate a context summary** to save the information to Notion
            4. **Review and save** the generated content to Notion
            
            This tool helps establish the foundation for all subsequent brand voice research steps.
            """)
        return
    
    try:
        # Pre-fill form with existing data if available
        client_profile = db_manager.get_client_profile(client_page_id)
        
        # Initialize default form values from existing data
        default_values = {
            "product_service": client_profile.get("Product_Service_Description", ""),
            "current_audience": client_profile.get("Current_Target_Audience", ""),
            "ideal_audience": client_profile.get("Ideal_Target_Audience", ""),
            "brand_values": research_tools_framework.format_list_for_display(client_profile.get("Brand_Values", "")),
            "brand_mission": client_profile.get("Brand_Mission", ""),
            "emotional_impact": research_tools_framework.format_list_for_display(client_profile.get("Desired_Emotional_Impact", "")),
            "brand_personality": research_tools_framework.format_list_for_display(client_profile.get("Brand_Personality", "")),
            "avoid_topics": client_profile.get("Words_Tones_To_Avoid", ""),
            "website_url": client_profile.get("Website", ""),
            "contact_email": client_profile.get("Contact_Email", ""),
            "phone_number": client_profile.get("Phone_Number", ""),
            "address": client_profile.get("Address", ""),
            "linkedin_url": client_profile.get("LinkedIn_URL", ""),
            "twitter_url": client_profile.get("Twitter_URL", ""),
            "facebook_url": client_profile.get("Facebook_URL", ""),
            "instagram_url": client_profile.get("Instagram_URL", ""),
            "other_social_media": client_profile.get("Other_Social_Media", "")
        }
        
        # Research section
        st.subheader("Research Options")
        
        # Website URL input
        website_url = st.text_input(
            "Client Website URL (optional)", 
            value=default_values["website_url"],
            help="Enter the URL to the client's website to extract information automatically"
        )
        
        # Analysis buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🌐 Re-extract Website Data", key="reextract_website", 
                        help="Step 1: Extract fresh company data from website"):
                if not website_url:
                    st.error("Please enter a website URL first")
                else:
                    step1_success, website_data, step1_error = extract_website_data(selected_client, website_url)
                    if step1_success:
                        # Update database with extracted data
                        notion_data = {
                            "Website": website_url,
                            "Industry": website_data.get("industry", ""),
                            "Product_Service_Description": website_data.get("company_description", ""),
                            "Contact_Email": website_data.get("contact_email", ""),
                            "Phone_Number": website_data.get("phone_number", ""),
                            "Address": website_data.get("address", ""),
                            "LinkedIn_URL": website_data.get("linkedin_url", ""),
                            "Twitter_URL": website_data.get("twitter_url", ""),
                            "Facebook_URL": website_data.get("facebook_url", ""),
                            "Instagram_URL": website_data.get("instagram_url", ""),
                            "Other_Social_Media": ', '.join(website_data.get("other_social_media", []))
                        }
                        update_success, error_msg = update_client_with_retry(db_manager, client_page_id, notion_data)
                        if update_success:
                            st.success("✅ Website data extracted and saved!")
                            st.rerun()
                        else:
                            st.error(f"Failed to save data: {error_msg}")
                    else:
                        st.error(f"Extraction failed: {step1_error}")
        
        with col2:
            if st.button("🎯 Re-analyze Brand Voice", key="reanalyze_brand", 
                        help="Step 2: Analyze brand voice using current data"):
                current_form_data = {
                    "industry": client_profile.get("Industry", ""),
                    "company_description": client_profile.get("Product_Service_Description", "")
                }
                website_data = {
                    "industry": client_profile.get("Industry", ""),
                    "company_description": client_profile.get("Product_Service_Description", "")
                }
                step2_success, analysis_result, step2_error = analyze_brand_voice(selected_client, website_data, current_form_data)
                if step2_success:
                    # Update database with brand voice data
                    notion_data = {
                        "Current_Target_Audience": analysis_result.get("current_target_audience", ""),
                        "Ideal_Target_Audience": analysis_result.get("ideal_target_audience", ""),
                        "Brand_Values": ', '.join(analysis_result.get("brand_values", [])) if isinstance(analysis_result.get("brand_values"), list) else analysis_result.get("brand_values", ""),
                        "Brand_Mission": analysis_result.get("brand_mission", ""),
                        "Desired_Emotional_Impact": ', '.join(analysis_result.get("desired_emotional_impact", [])) if isinstance(analysis_result.get("desired_emotional_impact"), list) else analysis_result.get("desired_emotional_impact", ""),
                        "Brand_Personality": ', '.join(analysis_result.get("brand_personality_traits", [])) if isinstance(analysis_result.get("brand_personality_traits"), list) else analysis_result.get("brand_personality", ""),
                        "Words_Tones_To_Avoid": ', '.join(analysis_result.get("words_tones_to_avoid", [])) if isinstance(analysis_result.get("words_tones_to_avoid"), list) else analysis_result.get("words_tones_to_avoid", "")
                    }
                    update_success, error_msg = update_client_with_retry(db_manager, client_page_id, notion_data)
                    if update_success:
                        st.success("✅ Brand voice analysis complete and saved!")
                        st.rerun()
                    else:
                        st.error(f"Failed to save data: {error_msg}")
                else:
                    st.error(f"Analysis failed: {step2_error}")
        
        with col3:
            if st.button("🔍 Full Re-analysis", key="full_reanalysis", 
                        help="Both steps: Extract website data + analyze brand voice"):
                if not website_url:
                    st.error("Please enter a website URL first")
                else:
                    # Use the comprehensive analysis function which does both steps
                    current_form_data = {
                        "product_service_description": default_values["product_service"],
                        "current_target_audience": default_values["current_audience"],
                        "ideal_target_audience": default_values["ideal_audience"],
                        "brand_values": default_values["brand_values"],
                        "brand_mission": default_values["brand_mission"],
                        "desired_emotional_impact": default_values["emotional_impact"],
                        "brand_personality": default_values["brand_personality"],
                        "words_tones_to_avoid": default_values["avoid_topics"]
                    }
                    
                    success, analysis_result, error_msg = comprehensive_client_analysis(
                        selected_client,
                        client_profile.get("Industry", ""),
                        website_url,
                        current_form_data,
                        optimize_content=True
                    )
                    
                    if success:
                        # Map results to Notion fields and save
                        notion_data = {
                            "Website": website_url,
                            "Industry": analysis_result.get("industry", ""),
                            "Product_Service_Description": analysis_result.get("company_description", ""),
                            "Current_Target_Audience": analysis_result.get("current_target_audience", ""),
                            "Ideal_Target_Audience": analysis_result.get("ideal_target_audience", ""),
                            "Brand_Values": ', '.join(analysis_result.get("brand_values", [])) if isinstance(analysis_result.get("brand_values"), list) else analysis_result.get("brand_values", ""),
                            "Brand_Mission": analysis_result.get("brand_mission", ""),
                            "Desired_Emotional_Impact": ', '.join(analysis_result.get("desired_emotional_impact", [])) if isinstance(analysis_result.get("desired_emotional_impact"), list) else analysis_result.get("desired_emotional_impact", ""),
                            "Brand_Personality": ', '.join(analysis_result.get("brand_personality_traits", [])) if isinstance(analysis_result.get("brand_personality_traits"), list) else analysis_result.get("brand_personality", ""),
                            "Words_Tones_To_Avoid": ', '.join(analysis_result.get("words_tones_to_avoid", [])) if isinstance(analysis_result.get("words_tones_to_avoid"), list) else analysis_result.get("words_tones_to_avoid", ""),
                            "Contact_Email": analysis_result.get("contact_email", ""),
                            "Phone_Number": analysis_result.get("phone_number", ""),
                            "Address": analysis_result.get("address", ""),
                            "LinkedIn_URL": analysis_result.get("linkedin_url", ""),
                            "Twitter_URL": analysis_result.get("twitter_url", ""),
                            "Facebook_URL": analysis_result.get("facebook_url", ""),
                            "Instagram_URL": analysis_result.get("instagram_url", ""),
                            "Other_Social_Media": ', '.join(analysis_result.get("other_social_media", [])) if isinstance(analysis_result.get("other_social_media"), list) else analysis_result.get("other_social_media", "")
                        }
                        update_success, error_msg = update_client_with_retry(db_manager, client_page_id, notion_data)
                        if update_success:
                            st.success("✅ Full re-analysis complete and saved!")
                            st.rerun()
                        else:
                            st.error(f"Failed to save data: {error_msg}")
                    else:
                        st.error(f"Full analysis failed: {error_msg}")
        
        # Form for client information
        with st.form("context_form"):
            st.subheader("Client Information")
            
            # Name is read-only, but Industry can be edited
            st.text_input("Business Name", value=client_profile.get("Name", ""), disabled=True)
            
            # Website URL field
            website_input = st.text_input(
                "Website URL", 
                value=default_values["website_url"],
                help="Company website URL for reference"
            )
            
            # Industry selection with custom option
            current_industry = client_profile.get("Industry", "Other")
            industry_options = [
                "Technology", "Healthcare", "Finance", "Education", 
                "Retail", "Manufacturing", "Services", "Non-profit",
                "Entertainment", "Food & Beverage", "Real Estate", 
                "Marketing & Advertising", "Legal", "Consulting",
                "Transportation", "Energy", "Agriculture", "Media",
                "Construction", "Automotive", "Telecommunications",
                "Custom (enter below)"
            ]
            
            # If current industry is not in the predefined list, add it
            if current_industry not in industry_options and current_industry != "Other":
                industry_options.insert(-1, current_industry)  # Add before "Custom" option
                selected_industry_option = current_industry
            elif current_industry in industry_options:
                selected_industry_option = current_industry
            else:
                selected_industry_option = "Other"
            
            selected_industry_option = st.selectbox("Industry", industry_options, 
                                                   index=industry_options.index(selected_industry_option) if selected_industry_option in industry_options else 0)
            
            # If "Custom" is selected, show text input
            if selected_industry_option == "Custom (enter below)":
                industry_value = st.text_input("Enter custom industry:", value="" if current_industry == "Other" else current_industry)
            else:
                industry_value = selected_industry_option
            
            # Editable fields using default values
            product_service = st.text_area(
                "Product/Service Description", 
                value=default_values["product_service"],
                help="Describe what the client offers in 1-3 sentences."
            )
            
            current_audience = st.text_area(
                "Current Target Audience", 
                value=default_values["current_audience"],
                help="Who does the client currently reach? Include demographics, interests, and pain points."
            )
            
            ideal_audience = st.text_area(
                "Ideal Target Audience", 
                value=default_values["ideal_audience"],
                help="Who would the client ideally like to reach? May differ from current audience."
            )
            
            brand_values = st.text_input(
                "Brand Values (comma-separated)", 
                value=default_values["brand_values"],
                help="Core principles that guide the brand (e.g., Innovation, Sustainability, Community)"
            )
            
            brand_mission = st.text_area(
                "Brand Mission", 
                value=default_values["brand_mission"],
                help="The brand's purpose or reason for existing."
            )
            
            emotional_impact = st.text_input(
                "Desired Emotional Impact (comma-separated)", 
                value=default_values["emotional_impact"],
                help="How should audience feel after engaging with the brand? (e.g., Inspired, Confident, Relieved)"
            )
            
            brand_personality = st.text_input(
                "Brand Personality (comma-separated)", 
                value=default_values["brand_personality"],
                help="3-5 adjectives that describe the brand as if it were a person"
            )
            
            avoid_topics = st.text_area(
                "Words/Tones/Topics to Avoid", 
                value=default_values["avoid_topics"],
                help="Language, topics, or approaches the brand wishes to stay away from"
            )
            
            # Contact Information Section
            st.subheader("Contact Information")
            
            col1, col2 = st.columns(2)
            with col1:
                contact_email = st.text_input(
                    "Contact Email", 
                    value=default_values["contact_email"],
                    help="Primary contact email address"
                )
                
                phone_number = st.text_input(
                    "Phone Number", 
                    value=default_values["phone_number"],
                    help="Primary phone number"
                )
                
                linkedin_url = st.text_input(
                    "LinkedIn URL", 
                    value=default_values["linkedin_url"],
                    help="LinkedIn profile or company page"
                )
                
                facebook_url = st.text_input(
                    "Facebook URL", 
                    value=default_values["facebook_url"],
                    help="Facebook page or profile"
                )
            
            with col2:
                address = st.text_area(
                    "Address", 
                    value=default_values["address"],
                    help="Physical business address"
                )
                
                twitter_url = st.text_input(
                    "Twitter/X URL", 
                    value=default_values["twitter_url"],
                    help="Twitter or X profile"
                )
                
                instagram_url = st.text_input(
                    "Instagram URL", 
                    value=default_values["instagram_url"],
                    help="Instagram profile"
                )
                
                other_social_media = st.text_area(
                    "Other Social Media", 
                    value=default_values["other_social_media"],
                    help="Other social media profiles (YouTube, TikTok, etc.)"
                )
            
            # Advanced options expander
            with st.expander("Advanced Options"):
                optimize_content = st.checkbox("Optimize content for next steps", value=True,
                                             help="Rewrite content to make it more useful for brand voice development")
            
            # Style the submit button
            st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 0.5em 1em;
            }
            </style>
            """, unsafe_allow_html=True)
            
            submit_button = st.form_submit_button("Generate Context Summary")
        
        if submit_button:
            # Validate custom industry field if needed
            if selected_industry_option == "Custom (enter below)" and not industry_value.strip():
                st.error("Please enter a custom industry name.")
                return
            
            # Collect all form data
            form_data = {
                "website": website_input,
                "industry": industry_value,
                "product_service_description": product_service,
                "current_target_audience": current_audience,
                "ideal_target_audience": ideal_audience,
                "brand_values": brand_values,
                "brand_mission": brand_mission,
                "desired_emotional_impact": emotional_impact,
                "brand_personality": brand_personality,
                "words_tones_to_avoid": avoid_topics,
                "contact_email": contact_email,
                "phone_number": phone_number,
                "address": address,
                "linkedin_url": linkedin_url,
                "twitter_url": twitter_url,
                "facebook_url": facebook_url,
                "instagram_url": instagram_url,
                "other_social_media": other_social_media
            }
            
            # Perform analysis if optimization is requested
            if optimize_content:
                with st.spinner("Performing comprehensive analysis..."):
                    success, analysis_result, error_msg = comprehensive_client_analysis(
                        selected_client,
                        industry_value,
                        website_url if website_url else None,
                        form_data,
                        optimize_content=True
                    )
                    
                    if success:
                        # Use optimized data (analysis may have refined the industry)
                        parsed_data = {
                            "business_name": selected_client,
                            "industry": analysis_result.get("industry", industry_value),
                            **{k: v for k, v in analysis_result.items() if k != "industry"}
                        }
                    else:
                        st.error(f"Analysis failed: {error_msg}")
                        return
            else:
                # Use form data directly
                parsed_data = {
                    "business_name": selected_client,
                    **form_data
                }
            
            # Display summary
            st.subheader("Context Summary")
            property_order = [
                "business_name", "website", "industry", "product_service_description",
                "current_target_audience", "ideal_target_audience", "brand_values",
                "brand_mission", "desired_emotional_impact", "brand_personality",
                "words_tones_to_avoid", "contact_email", "phone_number", "address",
                "linkedin_url", "twitter_url", "facebook_url", "instagram_url", "other_social_media"
            ]
            
            md_table = "| Field | Value |\n|-------|-------|\n"
            for key in property_order:
                if key in parsed_data:
                    display_key = " ".join(word.capitalize() for word in key.split("_"))
                    md_table += f"| {display_key} | {parsed_data.get(key, '')} |\n"
            st.markdown(md_table)
            
            # Prepare Notion data
            key_mapping = {
                "business_name": "Name", "website": "Website", "industry": "Industry",
                "product_service_description": "Product_Service_Description",
                "company_description": "Product_Service_Description",
                "current_target_audience": "Current_Target_Audience",
                "ideal_target_audience": "Ideal_Target_Audience",
                "brand_values": "Brand_Values", "brand_mission": "Brand_Mission",
                "desired_emotional_impact": "Desired_Emotional_Impact",
                "brand_personality": "Brand_Personality",
                "brand_personality_traits": "Brand_Personality",
                "words_tones_to_avoid": "Words_Tones_To_Avoid",
                "contact_email": "Contact_Email", "phone_number": "Phone_Number",
                "address": "Address", "linkedin_url": "LinkedIn_URL",
                "twitter_url": "Twitter_URL", "facebook_url": "Facebook_URL",
                "instagram_url": "Instagram_URL", "other_social_media": "Other_Social_Media"
            }
            
            notion_data = {}
            for json_key, notion_key in key_mapping.items():
                if json_key in parsed_data:
                    value = parsed_data[json_key]
                    # Convert arrays to comma-separated strings for Notion
                    if isinstance(value, list):
                        notion_data[notion_key] = ', '.join(value)
                    else:
                        notion_data[notion_key] = value
            
            # Update with retry logic
            with st.spinner("Updating client profile..."):
                success, error_msg = update_client_with_retry(db_manager, client_page_id, notion_data)
                
                if success:
                    db_manager.mark_tool_complete(client_page_id, "context_gatherer")
                    st.success("✅ Client profile updated in Notion database")
                    st.info("**Next step:** Use the Content Collector tool to gather content samples across channels.")
                else:
                    st.error(f"❌ {error_msg}")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please make sure your Notion database is properly set up and refresh the page.")

def parse_context_output(response):
    """Parse Context Gatherer output from GPT-4"""
    parsed_data = {}
    
    # Use the shared function to parse markdown tables
    table_data = research_tools_framework.parse_markdown_table(response)
    
    if not table_data:
        return parsed_data
    
    # Map the table fields to the correct database properties
    field_mapping = {
        "Business Name": "business_name",
        "Industry": "industry",
        "Product/Service Description": "product_service_description",
        "Current Target Audience": "current_target_audience",
        "Ideal Target Audience": "ideal_target_audience",
        "Brand Values": "brand_values",
        "Brand Mission": "brand_mission",
        "Desired Emotional Impact on Audience": "desired_emotional_impact",
        "Brand Personality": "brand_personality",
        "Words/Tones/Topics to Avoid": "words_tones_to_avoid"
    }
    
    # Extract data from table
    for row in table_data:
        if "Field" in row and "Value" in row:
            field = row["Field"]
            value = row["Value"]
            
            if field in field_mapping and value:
                parsed_data[field_mapping[field]] = value
    
    return parsed_data


if __name__ == "__main__":
    run_context_gatherer()