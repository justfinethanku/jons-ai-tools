"""
Brand Builder Tool - First step in the research workflow.
Collects foundational client information and brand attributes.
Allows creating new clients and enhancing existing ones.

REFACTORING NOTE: This tool has been updated to use the new modular prompt system.
- Prompts are now stored in prompts/structured/components/ for better maintainability
- Uses prompt_wrapper for safe transition with fallback capability
- Temperature and configuration are managed through prompt registry
- All existing functionality maintained while improving scalability

RENAME NOTE: Formerly known as "Context Gatherer" - renamed to "Brand Builder" 
for better clarity about the tool's purpose and more appealing branding.
"""

import streamlit as st
import json
import requests
from bs4 import BeautifulSoup
import trafilatura
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frameworks import universal_framework, research_tools_framework, prompt_wrappers
# NOTE: Import new prompt wrapper system for modular prompt management
from frameworks.prompt_wrappers import prompt_wrapper
# NOTE: Load prompt configurations to ensure they're registered
from prompts.structured.configs import brand_builder_prompts


def robust_json_parse(response_text):
    """
    Robust JSON parsing with multiple fallback strategies
    
    Args:
        response_text: The raw response text from API
        
    Returns:
        tuple: (success: bool, data: dict, error_msg: str)
    """
    # Strategy 1: Direct parsing after basic cleanup
    try:
        clean_response = response_text.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        result_data = json.loads(clean_response)
        return True, result_data, None
        
    except json.JSONDecodeError:
        pass  # Continue to Strategy 2
    
    # Strategy 2: Extract content between first { and last }
    try:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
            return False, {}, f"No valid JSON brackets found in response: {response_text[:200]}..."
            
        json_text = response_text[start_idx:end_idx+1]
        result_data = json.loads(json_text)
        return True, result_data, None
        
    except json.JSONDecodeError:
        pass  # Continue to Strategy 3
    
    # Strategy 3: Try research_tools_framework.clean_json_response
    try:
        cleaned = research_tools_framework.clean_json_response(response_text)
        result_data = json.loads(cleaned)
        return True, result_data, None
        
    except:
        pass  # Continue to final fallback
    
    # Final fallback: Return detailed error
    return False, {}, f"All JSON parsing strategies failed. Response starts with: {response_text[:100]}... Response ends with: {response_text[-100:]}"

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
    
    MODULAR ARCHITECTURE: This function now delegates to the modular step system.
    Individual step can be tested independently: 
        python -m tools.brand_builder.step_01_website_extractor --website URL --client NAME
    """
    # MODULAR ARCHITECTURE: Delegate to the individual step
    from tools.brand_builder.step_01_website_extractor import WebsiteExtractorTool
    from tools.brand_builder import WorkflowContext
    
    context = WorkflowContext({
        'client_name': client_name,
        'website_url': website_url
    })
    
    step = WebsiteExtractorTool()
    result = step.execute(context)
    
    return result.success, result.data, result.errors[0] if result.errors else None

def analyze_brand_voice(client_name, website_data, form_data=None):
    """
    Step 2: Comprehensive brand voice analysis using enhanced methodology
    
    MODULAR ARCHITECTURE: This function now delegates to the modular step system.
    Individual step can be tested independently: 
        python -m tools.brand_builder.step_02_brand_analyzer --client NAME --input data.json
    """
    # MODULAR ARCHITECTURE: Delegate to the individual step
    from tools.brand_builder.step_02_brand_analyzer import BrandAnalyzerTool
    from tools.brand_builder import WorkflowContext
    
    # Prepare context data
    context_data = {'client_name': client_name}
    context_data.update(website_data or {})
    context_data.update(form_data or {})
    
    context = WorkflowContext(context_data)
    
    step = BrandAnalyzerTool()
    result = step.execute(context)
    
    return result.success, result.data, result.errors[0] if result.errors else None

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

def run_content_collector_step(db_manager, client_page_id, client_name, brand_data):
    """
    Content Collector - Deep Research Workflow Step 2
    Identifies and catalogs brand communications across channels
    """
    try:
        # Data validation
        if not brand_data:
            st.error("Brand data is required for content collection. Please complete Brand Builder first.")
            return False, {}
        
        if not client_name:
            st.error("Client name is required for content collection.")
            return False, {}
        # Build context from brand data
        brand_context = f"""
**BRAND OVERVIEW:**
- Company: {client_name}
- Industry: {brand_data.get('industry', 'Unknown')}
- Description: {brand_data.get('product_service_description', brand_data.get('company_description', ''))}
- Mission: {brand_data.get('brand_mission', 'Not specified')}
- Values: {brand_data.get('brand_values', 'Not specified')}
- Target Audience: {brand_data.get('ideal_target_audience', brand_data.get('current_target_audience', 'Not specified'))}
- Brand Personality: {brand_data.get('brand_personality', brand_data.get('brand_personality_traits', 'Not specified'))}"""
        
        industry_context = f"Industry: {brand_data.get('industry', 'General')} - Consider industry-specific communication channels and content types."
        
        # Get the prompt using the wrapper system
        prompt, temperature = prompt_wrapper.get_content_collection_prompt(
            brand_context=brand_context, 
            industry_context=industry_context,
            target_channels=None  # Let AI suggest optimal channels
        )
        
        # Define schema for API validation
        api_schema = {
            "type": "object",
            "properties": {
                "content_samples": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "channel": {"type": "string"},
                            "content_type": {"type": "string"},
                            "sample_description": {"type": "string"},
                            "strategic_notes": {"type": "string"}
                        },
                        "required": ["channel", "content_type", "sample_description", "strategic_notes"]
                    }
                }
            },
            "required": ["content_samples"]
        }
        
        # Call the AI
        response = universal_framework.call_gemini_api(prompt, response_schema=api_schema, temperature=temperature)
        result_data = json.loads(response)
        
        # Save to workflow
        success = db_manager.save_deep_research_step(client_page_id, "content_collector", result_data)
        
        if success:
            # Display results
            st.subheader("📄 Content Collection Strategy")
            st.write("**Recommended content samples to collect for voice analysis:**")
            
            # Create a nice table display
            content_samples = result_data.get("content_samples", [])
            if content_samples:
                for i, sample in enumerate(content_samples, 1):
                    with st.expander(f"{i}. {sample.get('channel', 'Unknown')} - {sample.get('content_type', 'Unknown')}"):
                        st.write(f"**Sample to collect:** {sample.get('sample_description', 'No description')}")
                        st.write(f"**Strategic value:** {sample.get('strategic_notes', 'No notes')}")
            
            st.success("✅ Content collection strategy complete!")
            return True, result_data
        else:
            st.error("Failed to save content collection results")
            return False, {}
            
    except Exception as e:
        st.error(f"Content collection failed: {str(e)}")
        return False, {}


def run_voice_auditor_step(db_manager, client_page_id, client_name, brand_data, content_data):
    """
    Voice Auditor - Deep Research Workflow Step 3
    Analyzes content samples for voice consistency and brand alignment
    """
    try:
        # Data validation
        if not brand_data:
            st.error("Brand data is required for voice audit. Please complete Brand Builder first.")
            return False, {}
        
        if not content_data or not content_data.get("content_samples"):
            st.error("Content samples are required for voice audit. Please complete Content Collector first.")
            return False, {}
        # Build brand profile context
        brand_profile = f"""
**BRAND PROFILE:**
- Company: {client_name}
- Industry: {brand_data.get('industry', 'Unknown')}
- Mission: {brand_data.get('brand_mission', 'Not specified')}
- Values: {brand_data.get('brand_values', 'Not specified')}
- Personality Traits: {brand_data.get('brand_personality', brand_data.get('brand_personality_traits', 'Not specified'))}
- Communication Tone: {brand_data.get('communication_tone', 'Professional')}
- Target Audience: {brand_data.get('ideal_target_audience', brand_data.get('current_target_audience', 'Not specified'))}
- Voice Characteristics: {brand_data.get('voice_characteristics', 'Not specified')}
- Desired Emotional Impact: {brand_data.get('desired_emotional_impact', 'Not specified')}"""

        # Build content samples context from Content Collector results
        content_samples = "**CONTENT STRATEGY FOR ANALYSIS:**\n"
        if content_data and 'content_samples' in content_data:
            for i, sample in enumerate(content_data['content_samples'], 1):
                content_samples += f"{i}. {sample.get('channel', 'Unknown')} - {sample.get('content_type', 'Unknown')}: {sample.get('sample_description', 'No description')}\n"
        else:
            content_samples += "No specific content strategy available - use general brand communication samples"

        # Industry context
        industry_context = f"Industry: {brand_data.get('industry', 'General')} - Consider industry-specific voice patterns and communication norms while maintaining brand differentiation."

        # Get the prompt using the wrapper system
        prompt, temperature = prompt_wrapper.get_voice_audit_prompt(
            brand_profile=brand_profile,
            content_samples=content_samples,
            industry_context=industry_context
        )

        # Define schema for API validation
        api_schema = {
            "type": "object",
            "properties": {
                "voice_audit_summary": {
                    "type": "object",
                    "properties": {
                        "overall_consistency": {"type": "string"},
                        "strongest_aspects": {"type": "array", "items": {"type": "string"}},
                        "areas_for_improvement": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["overall_consistency", "strongest_aspects", "areas_for_improvement"]
                },
                "content_analysis": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content_type": {"type": "string"},
                            "channel": {"type": "string"},
                            "voice_evaluation": {"type": "string"},
                            "consistency_score": {"type": "string"},
                            "improvement_notes": {"type": "string"}
                        },
                        "required": ["content_type", "channel", "voice_evaluation", "consistency_score"]
                    }
                },
                "voice_patterns": {
                    "type": "object",
                    "properties": {
                        "consistent_elements": {"type": "array", "items": {"type": "string"}},
                        "inconsistent_elements": {"type": "array", "items": {"type": "string"}},
                        "missing_brand_elements": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "required": ["voice_audit_summary", "content_analysis", "voice_patterns"]
        }

        # Call the AI
        response = universal_framework.call_gemini_api(prompt, response_schema=api_schema, temperature=temperature)
        result_data = json.loads(response)

        # Save to workflow
        success = db_manager.save_deep_research_step(client_page_id, "voice_auditor", result_data)

        if success:
            # Display results
            st.subheader("🎯 Voice Audit Results")
            
            # Summary
            audit_summary = result_data.get("voice_audit_summary", {})
            if audit_summary:
                st.write("**Overall Assessment:**", audit_summary.get("overall_consistency", "No summary available"))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**✅ Strongest Aspects:**")
                    for aspect in audit_summary.get("strongest_aspects", []):
                        st.write(f"• {aspect}")
                
                with col2:
                    st.write("**🔄 Areas for Improvement:**")
                    for area in audit_summary.get("areas_for_improvement", []):
                        st.write(f"• {area}")

            # Content Analysis Details
            content_analysis = result_data.get("content_analysis", [])
            if content_analysis:
                st.write("**Content Sample Analysis:**")
                for analysis in content_analysis:
                    with st.expander(f"{analysis.get('content_type', 'Unknown')} ({analysis.get('channel', 'Unknown')}) - Score: {analysis.get('consistency_score', 'N/A')}"):
                        st.write(f"**Voice Evaluation:** {analysis.get('voice_evaluation', 'No evaluation')}")
                        if analysis.get('improvement_notes'):
                            st.write(f"**Improvement Notes:** {analysis.get('improvement_notes')}")

            # Voice Patterns
            voice_patterns = result_data.get("voice_patterns", {})
            if voice_patterns:
                st.write("**Voice Pattern Analysis:**")
                if voice_patterns.get("consistent_elements"):
                    st.write("**Consistent Elements:**", ", ".join(voice_patterns["consistent_elements"]))
                if voice_patterns.get("inconsistent_elements"):
                    st.write("**Inconsistent Elements:**", ", ".join(voice_patterns["inconsistent_elements"]))
                if voice_patterns.get("missing_brand_elements"):
                    st.write("**Missing Brand Elements:**", ", ".join(voice_patterns["missing_brand_elements"]))

            st.success("✅ Voice audit complete!")
            return True, result_data
        else:
            st.error("Failed to save voice audit results")
            return False, {}

    except Exception as e:
        st.error(f"Voice audit failed: {str(e)}")
        return False, {}


def run_audience_definer_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data):
    """
    Audience Definer - Deep Research Workflow Step 4
    Synthesizes all previous data to build comprehensive audience persona
    """
    try:
        # Data validation
        if not brand_data:
            st.error("Brand data is required for audience definition. Please complete Brand Builder first.")
            return False, {}
        
        if not content_data:
            st.error("Content data is required for audience definition. Please complete Content Collector first.")
            return False, {}
        
        if not voice_data:
            st.error("Voice audit data is required for audience definition. Please complete Voice Auditor first.")
            return False, {}
        # Build brand context from Brand Builder data
        brand_context = f"""
**BRAND FOUNDATION:**
- Company: {client_name}
- Industry: {brand_data.get('industry', 'Unknown')}
- Mission: {brand_data.get('brand_mission', 'Not specified')}
- Values: {brand_data.get('brand_values', 'Not specified')}
- Personality Traits: {brand_data.get('brand_personality', brand_data.get('brand_personality_traits', 'Not specified'))}
- Current Target Audience: {brand_data.get('current_target_audience', 'Not specified')}
- Ideal Target Audience: {brand_data.get('ideal_target_audience', 'Not specified')}
- Desired Emotional Impact: {brand_data.get('desired_emotional_impact', 'Not specified')}
- Value Proposition: {brand_data.get('value_proposition', 'Not specified')}"""

        # Build content insights from Content Collector
        content_insights = "**CONTENT STRATEGY INSIGHTS:**\n"
        if content_data and 'content_samples' in content_data:
            preferred_channels = []
            content_types = []
            for sample in content_data['content_samples']:
                channel = sample.get('channel', 'Unknown')
                content_type = sample.get('content_type', 'Unknown')
                
                if channel not in preferred_channels:
                    preferred_channels.append(channel)
                if content_type not in content_types:
                    content_types.append(content_type)
            
            content_insights += f"- Recommended Channels: {', '.join(preferred_channels)}\n"
            content_insights += f"- Content Types: {', '.join(content_types)}\n"
            content_insights += f"- Total Content Samples Identified: {len(content_data['content_samples'])}\n"
            
            # Add strategic insights
            for sample in content_data['content_samples'][:3]:  # Top 3 strategic insights
                content_insights += f"- {sample.get('channel', 'Unknown')}: {sample.get('strategic_notes', 'No notes')}\n"
        else:
            content_insights += "No specific content strategy data available"

        # Build voice insights from Voice Auditor
        voice_insights = "**VOICE ANALYSIS INSIGHTS:**\n"
        if voice_data:
            audit_summary = voice_data.get('voice_audit_summary', {})
            voice_patterns = voice_data.get('voice_patterns', {})
            
            if audit_summary:
                voice_insights += f"- Overall Consistency: {audit_summary.get('overall_consistency', 'Not assessed')}\n"
                if audit_summary.get('strongest_aspects'):
                    voice_insights += f"- Strongest Voice Aspects: {', '.join(audit_summary['strongest_aspects'])}\n"
                if audit_summary.get('areas_for_improvement'):
                    voice_insights += f"- Areas for Improvement: {', '.join(audit_summary['areas_for_improvement'])}\n"
            
            if voice_patterns:
                if voice_patterns.get('consistent_elements'):
                    voice_insights += f"- Consistent Voice Elements: {', '.join(voice_patterns['consistent_elements'])}\n"
                if voice_patterns.get('missing_brand_elements'):
                    voice_insights += f"- Missing Brand Elements: {', '.join(voice_patterns['missing_brand_elements'])}\n"
        else:
            voice_insights += "No voice analysis data available"

        # Industry context
        industry_context = f"""
**INDUSTRY CONTEXT:**
- Industry: {brand_data.get('industry', 'General')}
- Consider industry-specific communication norms, professional challenges, and decision-making patterns
- Account for typical roles, responsibilities, and success metrics in this industry
- Incorporate industry-specific language, tools, and competitive landscape awareness"""

        # Get the prompt using the wrapper system
        prompt, temperature = prompt_wrapper.get_audience_definer_prompt(
            brand_context=brand_context,
            content_insights=content_insights,
            voice_insights=voice_insights,
            industry_context=industry_context
        )

        # Define comprehensive schema for API validation
        api_schema = {
            "type": "object",
            "properties": {
                "persona_identity": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "title": {"type": "string"},
                        "company_type": {"type": "string"},
                        "experience_level": {"type": "string"}
                    },
                    "required": ["name", "title", "company_type", "experience_level"]
                },
                "detailed_demographics": {
                    "type": "object",
                    "properties": {
                        "age_range": {"type": "string"},
                        "income_level": {"type": "string"},
                        "location": {"type": "string"},
                        "education": {"type": "string"},
                        "family_status": {"type": "string"}
                    }
                },
                "industry_context": {
                    "type": "object",
                    "properties": {
                        "daily_challenges": {"type": "array", "items": {"type": "string"}},
                        "decision_making_process": {"type": "string"},
                        "success_metrics": {"type": "string"},
                        "industry_language": {"type": "string"},
                        "competitive_landscape": {"type": "string"}
                    }
                },
                "communication_preferences": {
                    "type": "object",
                    "properties": {
                        "preferred_voice_style": {"type": "string"},
                        "content_consumption_habits": {"type": "string"},
                        "trust_building_factors": {"type": "string"},
                        "engagement_patterns": {"type": "string"},
                        "information_processing": {"type": "string"}
                    }
                },
                "brand_relationship": {
                    "type": "object",
                    "properties": {
                        "current_awareness": {"type": "string"},
                        "ideal_interaction": {"type": "string"},
                        "conversion_barriers": {"type": "string"},
                        "value_drivers": {"type": "string"},
                        "relationship_expectations": {"type": "string"}
                    }
                }
            },
            "required": ["persona_identity", "detailed_demographics", "industry_context", "communication_preferences", "brand_relationship"]
        }

        # Call the AI
        response = universal_framework.call_gemini_api(prompt, response_schema=api_schema, temperature=temperature)
        result_data = json.loads(response)

        # Save to workflow
        success = db_manager.save_deep_research_step(client_page_id, "audience_definer", result_data)

        if success:
            # Display comprehensive persona results
            st.subheader("👤 Comprehensive Audience Persona")
            
            # Persona Identity
            persona_identity = result_data.get("persona_identity", {})
            if persona_identity:
                st.write(f"## Meet {persona_identity.get('name', 'Your Ideal Customer')}")
                st.write(f"**Role:** {persona_identity.get('title', 'Unknown')} at {persona_identity.get('company_type', 'Unknown Company')}")
                st.write(f"**Experience:** {persona_identity.get('experience_level', 'Unknown')}")

            # Demographics
            demographics = result_data.get("detailed_demographics", {})
            if demographics:
                st.write("### Demographics")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Age:** {demographics.get('age_range', 'Not specified')}")
                    st.write(f"**Income:** {demographics.get('income_level', 'Not specified')}")
                    st.write(f"**Location:** {demographics.get('location', 'Not specified')}")
                with col2:
                    st.write(f"**Education:** {demographics.get('education', 'Not specified')}")
                    st.write(f"**Family Status:** {demographics.get('family_status', 'Not specified')}")

            # Industry Context
            industry_ctx = result_data.get("industry_context", {})
            if industry_ctx:
                st.write("### Professional Context")
                if industry_ctx.get("daily_challenges"):
                    st.write("**Daily Challenges:**")
                    for challenge in industry_ctx["daily_challenges"]:
                        st.write(f"• {challenge}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if industry_ctx.get("decision_making_process"):
                        st.write(f"**Decision Making:** {industry_ctx['decision_making_process']}")
                    if industry_ctx.get("success_metrics"):
                        st.write(f"**Success Metrics:** {industry_ctx['success_metrics']}")
                with col2:
                    if industry_ctx.get("industry_language"):
                        st.write(f"**Communication Style:** {industry_ctx['industry_language']}")

            # Communication Preferences
            comm_prefs = result_data.get("communication_preferences", {})
            if comm_prefs:
                st.write("### Communication Preferences")
                for key, value in comm_prefs.items():
                    if value:
                        formatted_key = key.replace('_', ' ').title()
                        st.write(f"**{formatted_key}:** {value}")

            # Brand Relationship
            brand_rel = result_data.get("brand_relationship", {})
            if brand_rel:
                st.write("### Brand Relationship")
                for key, value in brand_rel.items():
                    if value:
                        formatted_key = key.replace('_', ' ').title()
                        st.write(f"**{formatted_key}:** {value}")

            st.success("✅ Comprehensive audience persona complete!")
            return True, result_data
        else:
            st.error("Failed to save audience persona results")
            return False, {}

    except Exception as e:
        st.error(f"Audience persona development failed: {str(e)}")
        return False, {}


def run_voice_traits_builder_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data, audience_data):
    """
    Voice Traits Builder - Deep Research Workflow Step 5
    Engineers persona-optimized voice traits with Do/Don't guidance
    """
    try:
        # Data validation
        if not audience_data:
            st.error("Audience data is required for voice traits building. Please complete Audience Definer first.")
            return False, {}
        
        if not voice_data:
            st.error("Voice audit data is required for voice traits building. Please complete Voice Auditor first.")
            return False, {}
        
        if not brand_data:
            st.error("Brand data is required for voice traits building. Please complete Brand Builder first.")
            return False, {}
        # Build comprehensive persona profile
        persona_profile = "**COMPREHENSIVE PERSONA PROFILE:**\n"
        if audience_data:
            persona_identity = audience_data.get("persona_identity", {})
            demographics = audience_data.get("detailed_demographics", {})
            industry_ctx = audience_data.get("industry_context", {})
            comm_prefs = audience_data.get("communication_preferences", {})
            brand_rel = audience_data.get("brand_relationship", {})
            
            persona_profile += f"**Identity:** {persona_identity.get('name', 'Target Customer')} - {persona_identity.get('title', 'Unknown Role')} at {persona_identity.get('company_type', 'Unknown Company')}\n"
            persona_profile += f"**Demographics:** {demographics.get('age_range', 'Unknown age')}, {demographics.get('income_level', 'Unknown income')}, {demographics.get('location', 'Unknown location')}\n"
            
            if industry_ctx.get('daily_challenges'):
                persona_profile += f"**Daily Challenges:** {', '.join(industry_ctx['daily_challenges'])}\n"
            if industry_ctx.get('decision_making_process'):
                persona_profile += f"**Decision Making:** {industry_ctx['decision_making_process']}\n"
            
            if comm_prefs.get('preferred_voice_style'):
                persona_profile += f"**Preferred Communication:** {comm_prefs['preferred_voice_style']}\n"
            if comm_prefs.get('trust_building_factors'):
                persona_profile += f"**Trust Factors:** {comm_prefs['trust_building_factors']}\n"
            
            if brand_rel.get('conversion_barriers'):
                persona_profile += f"**Conversion Barriers:** {brand_rel['conversion_barriers']}\n"
            if brand_rel.get('value_drivers'):
                persona_profile += f"**Value Drivers:** {brand_rel['value_drivers']}\n"
        else:
            persona_profile += "No detailed persona data available - using basic audience information"

        # Build voice analysis summary
        voice_analysis = "**VOICE ANALYSIS FINDINGS:**\n"
        if voice_data:
            audit_summary = voice_data.get('voice_audit_summary', {})
            voice_patterns = voice_data.get('voice_patterns', {})
            
            if audit_summary.get('overall_consistency'):
                voice_analysis += f"**Overall Consistency:** {audit_summary['overall_consistency']}\n"
            if audit_summary.get('strongest_aspects'):
                voice_analysis += f"**Strongest Aspects:** {', '.join(audit_summary['strongest_aspects'])}\n"
            if audit_summary.get('areas_for_improvement'):
                voice_analysis += f"**Areas for Improvement:** {', '.join(audit_summary['areas_for_improvement'])}\n"
            
            if voice_patterns.get('consistent_elements'):
                voice_analysis += f"**Consistent Elements:** {', '.join(voice_patterns['consistent_elements'])}\n"
            if voice_patterns.get('missing_brand_elements'):
                voice_analysis += f"**Missing Brand Elements:** {', '.join(voice_patterns['missing_brand_elements'])}\n"
        else:
            voice_analysis += "No voice analysis data available"

        # Build brand foundation
        brand_foundation = f"""**BRAND FOUNDATION:**
- Company: {client_name}
- Industry: {brand_data.get('industry', 'Unknown')}
- Mission: {brand_data.get('brand_mission', 'Not specified')}
- Values: {brand_data.get('brand_values', 'Not specified')}
- Personality Traits: {brand_data.get('brand_personality', brand_data.get('brand_personality_traits', 'Not specified'))}
- Desired Emotional Impact: {brand_data.get('desired_emotional_impact', 'Not specified')}
- Value Proposition: {brand_data.get('value_proposition', 'Not specified')}"""

        # Industry context
        industry_context = f"""**INDUSTRY CONTEXT:**
- Industry: {brand_data.get('industry', 'General')}
- Competitive differentiation focus on standing out while maintaining industry credibility
- Communication norms and expectations specific to this industry
- Professional language and decision-making patterns typical for this sector"""

        # Get the prompt using the wrapper system
        prompt, temperature = prompt_wrapper.get_voice_traits_builder_prompt(
            persona_profile=persona_profile,
            voice_analysis=voice_analysis,
            brand_foundation=brand_foundation,
            industry_context=industry_context
        )

        # Define comprehensive schema for API validation
        api_schema = {
            "type": "object",
            "properties": {
                "voice_traits_summary": {
                    "type": "object",
                    "properties": {
                        "strategy_overview": {"type": "string"},
                        "persona_connection": {"type": "string"},
                        "differentiation_approach": {"type": "string"}
                    },
                    "required": ["strategy_overview", "persona_connection", "differentiation_approach"]
                },
                "core_voice_traits": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "trait_name": {"type": "string"},
                            "definition": {"type": "string"},
                            "do_examples": {"type": "array", "items": {"type": "string"}},
                            "dont_examples": {"type": "array", "items": {"type": "string"}},
                            "persona_connection": {"type": "string"},
                            "business_impact": {"type": "string"}
                        },
                        "required": ["trait_name", "definition", "do_examples", "dont_examples", "persona_connection"]
                    }
                },
                "implementation_notes": {
                    "type": "object",
                    "properties": {
                        "trait_prioritization": {"type": "string"},
                        "consistency_guidelines": {"type": "string"},
                        "adaptation_notes": {"type": "string"}
                    }
                }
            },
            "required": ["voice_traits_summary", "core_voice_traits", "implementation_notes"]
        }

        # Call the AI
        response = universal_framework.call_gemini_api(prompt, response_schema=api_schema, temperature=temperature)
        result_data = json.loads(response)

        # Save to workflow
        success = db_manager.save_deep_research_step(client_page_id, "voice_traits_builder", result_data)

        if success:
            # Display comprehensive voice traits results
            st.subheader("🎯 Persona-Optimized Voice Traits")
            
            # Strategy Summary
            traits_summary = result_data.get("voice_traits_summary", {})
            if traits_summary:
                st.write("### Strategic Approach")
                st.write(f"**Strategy:** {traits_summary.get('strategy_overview', 'No overview available')}")
                st.write(f"**Persona Connection:** {traits_summary.get('persona_connection', 'No connection notes')}")
                st.write(f"**Differentiation:** {traits_summary.get('differentiation_approach', 'No differentiation notes')}")

            # Core Voice Traits
            core_traits = result_data.get("core_voice_traits", [])
            if core_traits:
                st.write("### Core Voice Traits")
                
                for i, trait in enumerate(core_traits, 1):
                    with st.expander(f"Trait {i}: {trait.get('trait_name', 'Unknown Trait')}"):
                        st.write(f"**Definition:** {trait.get('definition', 'No definition')}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**✅ DO:**")
                            for do_example in trait.get('do_examples', []):
                                st.write(f"• {do_example}")
                        
                        with col2:
                            st.write("**❌ DON'T:**")
                            for dont_example in trait.get('dont_examples', []):
                                st.write(f"• {dont_example}")
                        
                        if trait.get('persona_connection'):
                            st.write(f"**Why This Works:** {trait['persona_connection']}")
                        
                        if trait.get('business_impact'):
                            st.write(f"**Business Impact:** {trait['business_impact']}")

            # Implementation Notes
            implementation = result_data.get("implementation_notes", {})
            if implementation:
                st.write("### Implementation Guidelines")
                if implementation.get("trait_prioritization"):
                    st.write(f"**Trait Prioritization:** {implementation['trait_prioritization']}")
                if implementation.get("consistency_guidelines"):
                    st.write(f"**Consistency Guidelines:** {implementation['consistency_guidelines']}")
                if implementation.get("adaptation_notes"):
                    st.write(f"**Adaptation Notes:** {implementation['adaptation_notes']}")

            st.success("✅ Persona-optimized voice traits complete!")
            return True, result_data
        else:
            st.error("Failed to save voice traits results")
            return False, {}

    except Exception as e:
        st.error(f"Voice traits builder failed: {str(e)}")
        return False, {}


def run_gap_analyzer_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data, audience_data, voice_traits_data):
    """
    Gap Analyzer - Deep Research Workflow Step 6
    Comprehensive competitive intelligence and strategic positioning analysis
    """
    try:
        # Data validation
        if not voice_traits_data or not voice_traits_data.get("core_voice_traits"):
            st.error("Voice traits data is required for gap analysis. Please complete Voice Traits Builder first.")
            return False, {}
        
        if not audience_data:
            st.error("Audience data is required for gap analysis. Please complete Audience Definer first.")
            return False, {}
        
        if not brand_data:
            st.error("Brand data is required for gap analysis. Please complete Brand Builder first.")
            return False, {}
        
        # Build client context for competitive analysis
        client_context = f"""
**CLIENT PROFILE:**
- Company: {client_name}
- Industry: {brand_data.get('industry', 'Unknown')}
- Mission: {brand_data.get('brand_mission', 'Not specified')}
- Values: {brand_data.get('brand_values', 'Not specified')}
- Value Proposition: {brand_data.get('value_proposition', 'Not specified')}
- Products/Services: {brand_data.get('product_service_description', brand_data.get('company_description', 'Not specified'))}"""

        # Build industry and target market context
        industry_context = f"Industry: {brand_data.get('industry', 'General')} - Focus on companies in this sector and related markets"
        
        target_market = "Target Market: "
        if audience_data:
            persona_identity = audience_data.get("persona_identity", {})
            demographics = audience_data.get("detailed_demographics", {})
            target_market += f"{persona_identity.get('title', 'Unknown role')} at {persona_identity.get('company_type', 'Unknown companies')}, "
            target_market += f"{demographics.get('age_range', 'Unknown age')}, {demographics.get('location', 'Unknown location')}"
        else:
            target_market += brand_data.get('ideal_target_audience', brand_data.get('current_target_audience', 'Not specified'))

        # STAGE 1: Competitor Discovery
        st.write("🔍 **Stage 1:** Discovering strategic competitors...")
        
        discovery_prompt, discovery_temp = prompt_wrapper.get_competitor_discovery_prompt(
            client_context=client_context,
            industry_context=industry_context,
            target_market=target_market
        )
        
        discovery_schema = {
            "type": "object",
            "properties": {
                "competitor_discovery": {
                    "type": "object",
                    "properties": {
                        "initial_research": {"type": "string"},
                        "selection_criteria": {"type": "string"},
                        "market_insights": {"type": "string"}
                    }
                },
                "final_competitors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "website": {"type": "string"},
                            "rationale": {"type": "string"}
                        },
                        "required": ["name", "website", "rationale"]
                    }
                }
            },
            "required": ["competitor_discovery", "final_competitors"]
        }
        
        discovery_response = universal_framework.call_gemini_api(discovery_prompt, response_schema=discovery_schema, temperature=discovery_temp)
        discovery_data = json.loads(discovery_response)
        
        competitors = discovery_data.get("final_competitors", [])
        st.success(f"✅ **Stage 1 Complete:** Found {len(competitors)} strategic competitors")
        
        # Display discovered competitors
        for i, comp in enumerate(competitors, 1):
            st.write(f"{i}. **{comp.get('name', 'Unknown')}** - {comp.get('rationale', 'No rationale')}")
        
        # STAGE 2: Individual Competitor Analysis (5 parallel calls)
        st.write("📊 **Stage 2:** Analyzing each competitor...")
        
        competitor_analyses = []
        analysis_framework = f"""
**ANALYSIS FOCUS:**
- Voice and communication style comparison with {client_name}
- Target audience and positioning strategy
- Messaging themes and value propositions
- Communication strengths and weaknesses
- Differentiation opportunities for {client_name}"""
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, competitor in enumerate(competitors, 1):
            status_text.text(f"Analyzing competitor {i} of {len(competitors)}: {competitor.get('name', 'Unknown')}")
            progress_bar.progress(i / len(competitors))
            
            competitor_info = f"""
**COMPETITOR:** {competitor.get('name', 'Unknown')}
**Website:** {competitor.get('website', 'Unknown')}
**Strategic Importance:** {competitor.get('rationale', 'Unknown')}"""
            
            analysis_prompt, analysis_temp = prompt_wrapper.get_competitor_analysis_prompt(
                competitor_info=competitor_info,
                analysis_framework=analysis_framework,
                client_context=client_context
            )
            
            analysis_schema = {
                "type": "object",
                "properties": {
                    "competitor_overview": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "positioning_summary": {"type": "string"},
                            "target_audience": {"type": "string"},
                            "value_proposition": {"type": "string"}
                        }
                    },
                    "voice_analysis": {
                        "type": "object",
                        "properties": {
                            "communication_style": {"type": "string"},
                            "key_messages": {"type": "array", "items": {"type": "string"}},
                            "tone_characteristics": {"type": "string"},
                            "content_strategy": {"type": "string"}
                        }
                    },
                    "competitive_assessment": {
                        "type": "object",
                        "properties": {
                            "strengths": {"type": "array", "items": {"type": "string"}},
                            "weaknesses": {"type": "array", "items": {"type": "string"}},
                            "differentiation_opportunities": {"type": "array", "items": {"type": "string"}},
                            "market_position": {"type": "string"}
                        }
                    }
                }
            }
            
            try:
                analysis_response = universal_framework.call_gemini_api(analysis_prompt, response_schema=analysis_schema, temperature=analysis_temp)
                analysis_data = json.loads(analysis_response)
                competitor_analyses.append(analysis_data)
            except Exception as e:
                st.warning(f"Failed to analyze {competitor.get('name', 'Unknown')}: {str(e)}")
                # Continue with other competitors
        
        progress_bar.progress(1.0)
        status_text.text(f"✅ Completed analysis of {len(competitor_analyses)} competitors")
        
        # STAGE 3: Strategic Gap Analysis
        st.write("🎯 **Stage 3:** Synthesizing competitive intelligence...")
        
        # Build comprehensive analysis context
        client_analysis = f"""
**CLIENT CURRENT STATE:**
{client_context}

**CLIENT VOICE AUDIT:**
{json.dumps(voice_data, indent=2) if voice_data else 'No voice audit data'}

**CLIENT PERSONA:**
{json.dumps(audience_data, indent=2) if audience_data else 'No persona data'}"""

        competitor_profiles = json.dumps(competitor_analyses, indent=2)
        
        market_context = f"""
**MARKET CONTEXT:**
- Industry: {brand_data.get('industry', 'General')}
- Target Market: {target_market}
- Competitive Discovery Insights: {discovery_data.get('competitor_discovery', {}).get('market_insights', 'None')}"""

        voice_traits = json.dumps(voice_traits_data, indent=2) if voice_traits_data else "No voice traits defined"

        strategic_prompt, strategic_temp = prompt_wrapper.get_strategic_gap_analysis_prompt(
            client_analysis=client_analysis,
            competitor_profiles=competitor_profiles,
            market_context=market_context,
            voice_traits=voice_traits
        )
        
        strategic_schema = {
            "type": "object",
            "properties": {
                "market_landscape_analysis": {
                    "type": "object",
                    "properties": {
                        "competitive_overview": {"type": "string"},
                        "common_patterns": {"type": "string"},
                        "market_gaps": {"type": "string"},
                        "differentiation_potential": {"type": "string"}
                    }
                },
                "competitive_positioning": {
                    "type": "object",
                    "properties": {
                        "client_vs_competitors": {"type": "string"},
                        "unique_advantages": {"type": "array", "items": {"type": "string"}},
                        "competitive_disadvantages": {"type": "array", "items": {"type": "string"}},
                        "positioning_opportunities": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "voice_gap_recommendations": {
                    "type": "object",
                    "properties": {
                        "critical_voice_improvements": {"type": "array", "items": {"type": "string"}},
                        "positioning_adjustments": {"type": "array", "items": {"type": "string"}},
                        "messaging_priorities": {"type": "array", "items": {"type": "string"}},
                        "differentiation_strategy": {"type": "string"}
                    }
                },
                "implementation_strategy": {
                    "type": "object",
                    "properties": {
                        "immediate_actions": {"type": "array", "items": {"type": "string"}},
                        "medium_term_goals": {"type": "array", "items": {"type": "string"}},
                        "long_term_strategy": {"type": "string"},
                        "success_metrics": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "required": ["market_landscape_analysis", "competitive_positioning", "voice_gap_recommendations", "implementation_strategy"]
        }
        
        strategic_response = universal_framework.call_gemini_api(strategic_prompt, response_schema=strategic_schema, temperature=strategic_temp)
        strategic_data = json.loads(strategic_response)
        
        # Compile complete gap analysis data
        complete_gap_analysis = {
            "competitor_discovery": discovery_data,
            "competitor_analyses": competitor_analyses,
            "strategic_analysis": strategic_data,
            "analysis_metadata": {
                "total_competitors_analyzed": len(competitor_analyses),
                "analysis_timestamp": datetime.now().isoformat(),
                "api_calls_made": 2 + len(competitor_analyses)  # Discovery + Strategic + Individual analyses
            }
        }
        
        # Save comprehensive competitive intelligence to workflow
        success = db_manager.save_deep_research_step(client_page_id, "gap_analyzer", complete_gap_analysis)
        
        if success:
            # Display comprehensive results
            st.subheader("🎯 Strategic Market Analysis Results")
            
            # Market Landscape
            market_analysis = strategic_data.get("market_landscape_analysis", {})
            if market_analysis:
                st.write("### Market Landscape")
                st.write(f"**Competitive Overview:** {market_analysis.get('competitive_overview', 'No overview')}")
                st.write(f"**Market Gaps:** {market_analysis.get('market_gaps', 'No gaps identified')}")
            
            # Competitive Positioning
            positioning = strategic_data.get("competitive_positioning", {})
            if positioning:
                st.write("### Competitive Positioning")
                st.write(f"**Client vs. Competitors:** {positioning.get('client_vs_competitors', 'No comparison')}")
                
                if positioning.get("unique_advantages"):
                    st.write("**🎯 Unique Advantages:**")
                    for advantage in positioning["unique_advantages"]:
                        st.write(f"• {advantage}")
                
                if positioning.get("positioning_opportunities"):
                    st.write("**📈 Positioning Opportunities:**")
                    for opportunity in positioning["positioning_opportunities"]:
                        st.write(f"• {opportunity}")
            
            # Voice Gap Recommendations
            voice_gaps = strategic_data.get("voice_gap_recommendations", {})
            if voice_gaps:
                st.write("### Voice Gap Recommendations")
                
                if voice_gaps.get("critical_voice_improvements"):
                    st.write("**🔧 Critical Voice Improvements:**")
                    for improvement in voice_gaps["critical_voice_improvements"]:
                        st.write(f"• {improvement}")
                
                if voice_gaps.get("differentiation_strategy"):
                    st.write(f"**🎭 Differentiation Strategy:** {voice_gaps['differentiation_strategy']}")
            
            # Implementation Strategy
            implementation = strategic_data.get("implementation_strategy", {})
            if implementation:
                st.write("### Implementation Strategy")
                
                if implementation.get("immediate_actions"):
                    st.write("**⚡ Immediate Actions:**")
                    for action in implementation["immediate_actions"]:
                        st.write(f"• {action}")
                
                if implementation.get("long_term_strategy"):
                    st.write(f"**🎯 Long-term Strategy:** {implementation['long_term_strategy']}")

            st.success("✅ Comprehensive competitive analysis complete!")
            st.info(f"💾 **Data Preserved:** Analysis of {len(competitor_analyses)} competitors saved for future tools")
            
            return True, complete_gap_analysis
        else:
            st.error("Failed to save gap analysis results")
            return False, {}

    except Exception as e:
        st.error(f"Gap analysis failed: {str(e)}")
        return False, {}


def run_content_rewriter_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data, audience_data, voice_traits_data, gap_data):
    """
    Run Content Rewriter (Step 7) - Transform content samples using all workflow insights
    
    Two-stage process:
    Stage 1: Content Transformation Analysis - Analyze content against voice traits and insights
    Stage 2: Content Transformation - Transform content samples systematically
    
    Args:
        db_manager: NotionDatabaseManager instance
        client_page_id: Notion page ID for the client
        client_name: Name of the client
        brand_data: Brand foundation data from Brand Builder
        content_data: Content samples from Content Collector 
        voice_data: Voice analysis from Voice Auditor
        audience_data: Persona profile from Audience Definer
        voice_traits_data: Voice traits from Voice Traits Builder
        gap_data: Competitive positioning from Gap Analyzer
        
    Returns:
        Tuple of (success: bool, result_data: dict)
    """
    try:
        # Data validation
        if not gap_data or not gap_data.get("strategic_analysis"):
            st.error("Gap analysis data is required for content rewriter. Please complete Gap Analyzer first.")
            return False, {}
        
        if not voice_traits_data or not voice_traits_data.get("core_voice_traits"):
            st.error("Voice traits data is required for content rewriter. Please complete Voice Traits Builder first.")
            return False, {}
        
        if not audience_data:
            st.error("Audience data is required for content rewriter. Please complete Audience Definer first.")
            return False, {}
        
        if not content_data or not content_data.get("content_samples"):
            st.error("Content samples are required for content rewriter. Please complete Content Collector first.")
            return False, {}
        
        # Initialize prompt wrapper
        prompt_wrapper_instance = prompt_wrappers.PromptWrapper()
        
        # Stage 1: Content Transformation Analysis
        st.write("**Stage 1:** Analyzing content transformation opportunities...")
        
        # Prepare data contexts for analysis
        content_samples_str = json.dumps(content_data.get("content_samples", []), indent=2)
        voice_traits_str = json.dumps(voice_traits_data.get("core_voice_traits", []), indent=2)
        persona_insights_str = json.dumps(audience_data, indent=2)
        competitive_positioning_str = json.dumps(gap_data.get("strategic_analysis", {}), indent=2)
        
        # Get transformation analysis prompt
        analysis_prompt, analysis_temperature = prompt_wrapper_instance.get_content_transformation_analysis_prompt(
            content_samples=content_samples_str,
            voice_traits=voice_traits_str,
            persona_insights=persona_insights_str,
            competitive_positioning=competitive_positioning_str
        )
        
        # Call API for transformation analysis with retry logic
        try:
            with st.spinner("Analyzing content transformation opportunities..."):
                analysis_response = universal_framework.call_gemini_api(
                    analysis_prompt, 
                    temperature=analysis_temperature
                )
            
            # Parse analysis response
            analysis_data = json.loads(research_tools_framework.clean_json_response(analysis_response))
            st.success(f"✅ Stage 1 complete: Identified {analysis_data.get('transformation_analysis', {}).get('total_improvements_identified', 0)} improvement opportunities")
            
        except json.JSONDecodeError as e:
            st.error(f"Stage 1 failed: Invalid response format - {str(e)}")
            return False, {}
        except Exception as e:
            st.error(f"Stage 1 failed: API error - {str(e)}")
            return False, {}
        
        # Stage 2: Content Transformation
        st.write("**Stage 2:** Transforming content samples with voice traits and insights...")
        
        # Prepare transformation context
        transformation_plan_str = json.dumps(analysis_data, indent=2)
        persona_profile_str = json.dumps(audience_data, indent=2)
        competitive_insights_str = json.dumps(gap_data.get("strategic_analysis", {}), indent=2)
        
        # Get content transformation prompt
        transformation_prompt, transformation_temperature = prompt_wrapper_instance.get_content_transformation_prompt(
            transformation_plan=transformation_plan_str,
            voice_traits=voice_traits_str,
            persona_profile=persona_profile_str,
            competitive_insights=competitive_insights_str,
            content_samples=content_samples_str
        )
        
        # Call API for content transformation
        try:
            transformation_response = universal_framework.call_gemini_api(
                transformation_prompt,
                temperature=transformation_temperature
            )
            
            # Parse transformation response
            transformation_data = json.loads(research_tools_framework.clean_json_response(transformation_response))
            
            transformed_count = transformation_data.get('transformation_results', {}).get('successful_transformations', 0)
            st.success(f"✅ Stage 2 complete: Successfully transformed {transformed_count} content samples")
            
        except Exception as e:
            st.error(f"Stage 2 failed: {str(e)}")
            return False, {}
        
        # Combine results for comprehensive content rewriter output
        complete_content_rewriter = {
            "analysis": analysis_data,
            "transformations": transformation_data,
            "analysis_timestamp": datetime.now().isoformat(),
            "transformation_timestamp": datetime.now().isoformat(),
            "client_name": client_name,
            "total_samples_analyzed": len(content_data.get("content_samples", [])),
            "successful_transformations": transformed_count,
            "transformation_patterns": transformation_data.get("transformation_patterns", [])
        }
        
        # Display comprehensive results
        st.subheader("🎯 Content Rewriter Results")
        
        # Show analysis summary
        analysis_summary = analysis_data.get("transformation_analysis", {})
        st.write(f"**Analysis Summary:** {analysis_summary.get('analysis_summary', 'Content transformation opportunities identified')}")
        st.write(f"**Content Samples Analyzed:** {analysis_summary.get('content_samples_analyzed', 0)}")
        st.write(f"**Total Improvements Identified:** {analysis_summary.get('total_improvements_identified', 0)}")
        
        # Show transformation results  
        transformation_results = transformation_data.get("transformation_results", {})
        st.write(f"**Transformation Summary:** {transformation_results.get('transformation_summary', 'Content samples transformed successfully')}")
        st.write(f"**Successful Transformations:** {transformation_results.get('successful_transformations', 0)}")
        
        # Show example transformations
        transformed_content = transformation_data.get("transformed_content", [])
        if transformed_content:
            st.write("**Example Transformations:**")
            for idx, content in enumerate(transformed_content[:2]):  # Show first 2 examples
                with st.expander(f"Sample {idx + 1}: {content.get('content_type', 'Unknown Type')}"):
                    st.write(f"**Channel:** {content.get('content_channel', 'Unknown')}")
                    st.write(f"**Original:** {content.get('original_content', 'N/A')[:200]}...")
                    st.write(f"**Transformed:** {content.get('transformed_content', 'N/A')[:200]}...")
                    st.write(f"**Quality Score:** {content.get('quality_score', 'N/A')}/10")
        
        # Show transformation patterns identified
        patterns = transformation_data.get("transformation_patterns", [])
        if patterns:
            st.write("**Transformation Patterns Identified:**")
            for pattern in patterns[:3]:  # Show top 3 patterns
                st.write(f"• **{pattern.get('pattern_name', 'Unknown')}:** {pattern.get('description', 'No description')}")
        
        # Save results to Notion's Deep_Research_Workflow field
        save_success = db_manager.save_deep_research_step(
            client_page_id, 
            "content_rewriter", 
            complete_content_rewriter
        )
        
        if save_success:
            st.success("✅ Content Rewriter results saved to Notion successfully!")
            
            return True, complete_content_rewriter
        else:
            st.error("Failed to save content rewriter results")
            return False, {}

    except Exception as e:
        st.error(f"Content rewriter failed: {str(e)}")
        return False, {}


def run_guidelines_finalizer_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data, audience_data, voice_traits_data, gap_data, content_rewriter_data):
    """
    Run Guidelines Finalizer (Step 8) - Create turnkey Brand Voice Guidelines document
    
    Single comprehensive synthesis process:
    Synthesizes ALL 7 previous workflow steps into complete Brand Voice Guidelines document
    
    Args:
        db_manager: NotionDatabaseManager instance
        client_page_id: Notion page ID for the client
        client_name: Name of the client
        brand_data: Brand foundation data from Brand Builder
        content_data: Content samples from Content Collector 
        voice_data: Voice analysis from Voice Auditor
        audience_data: Persona profile from Audience Definer
        voice_traits_data: Voice traits from Voice Traits Builder
        gap_data: Competitive positioning from Gap Analyzer
        content_rewriter_data: Content transformations from Content Rewriter
        
    Returns:
        Tuple of (success: bool, result_data: dict)
    """
    try:
        # Data validation - Guidelines Finalizer requires ALL previous steps
        if not content_rewriter_data or not content_rewriter_data.get("transformations"):
            st.error("Content rewriter data is required for guidelines finalizer. Please complete Content Rewriter first.")
            return False, {}
        
        if not gap_data or not gap_data.get("strategic_analysis"):
            st.error("Gap analysis data is required for guidelines finalizer. Please complete Gap Analyzer first.")
            return False, {}
        
        if not voice_traits_data or not voice_traits_data.get("core_voice_traits"):
            st.error("Voice traits data is required for guidelines finalizer. Please complete Voice Traits Builder first.")
            return False, {}
        
        if not audience_data:
            st.error("Audience data is required for guidelines finalizer. Please complete Audience Definer first.")
            return False, {}
        
        if not brand_data:
            st.error("Brand data is required for guidelines finalizer. Please complete Brand Builder first.")
            return False, {}
        
        # Initialize prompt wrapper
        prompt_wrapper_instance = prompt_wrappers.PromptWrapper()
        
        st.write("**Synthesizing complete Brand Voice Guidelines document...**")
        
        # Prepare comprehensive data contexts for synthesis
        brand_foundation_str = json.dumps({
            "client_name": client_name,
            "brand_values": brand_data.get("brand_values", []),
            "brand_mission": brand_data.get("brand_mission", ""),
            "value_proposition": brand_data.get("value_proposition", ""),
            "brand_personality_traits": brand_data.get("brand_personality_traits", []),
            "competitive_differentiation": brand_data.get("competitive_differentiation", "")
        }, indent=2)
        
        persona_profile_str = json.dumps(audience_data, indent=2)
        voice_traits_str = json.dumps(voice_traits_data.get("core_voice_traits", []), indent=2)
        competitive_analysis_str = json.dumps(gap_data.get("strategic_analysis", {}), indent=2)
        content_examples_str = json.dumps(content_rewriter_data.get("transformations", {}).get("transformed_content", []), indent=2)
        
        # Create workflow summary
        workflow_summary = {
            "workflow_overview": f"Complete 8-step Deep Research Workflow for {client_name}",
            "step_1_brand_builder": "Foundation brand analysis and voice framework established",
            "step_2_content_collector": f"Identified {len(content_data.get('content_samples', []))} content samples across key channels",
            "step_3_voice_auditor": f"Analyzed voice consistency and identified improvement opportunities",
            "step_4_audience_definer": f"Developed detailed persona: {audience_data.get('persona_identity', {}).get('name', 'Unknown')}",
            "step_5_voice_traits_builder": f"Extracted {len(voice_traits_data.get('core_voice_traits', []))} persona-optimized voice traits",
            "step_6_gap_analyzer": f"Analyzed {len(gap_data.get('competitors', []))} competitors and developed strategic positioning",
            "step_7_content_rewriter": f"Successfully transformed {content_rewriter_data.get('successful_transformations', 0)} content samples",
            "total_api_calls": "15+ strategic AI analyses completed",
            "comprehensive_insights": "All insights synthesized for immediate implementation"
        }
        workflow_summary_str = json.dumps(workflow_summary, indent=2)
        
        # Get guidelines synthesis prompt
        guidelines_prompt, guidelines_temperature = prompt_wrapper_instance.get_brand_voice_guidelines_synthesis_prompt(
            brand_foundation=brand_foundation_str,
            persona_profile=persona_profile_str,
            voice_traits=voice_traits_str,
            competitive_analysis=competitive_analysis_str,
            content_examples=content_examples_str,
            workflow_summary=workflow_summary_str
        )
        
        # Call API for guidelines synthesis
        try:
            guidelines_response = universal_framework.call_gemini_api(
                guidelines_prompt,
                temperature=guidelines_temperature
            )
            
            # Parse guidelines response
            guidelines_data = json.loads(research_tools_framework.clean_json_response(guidelines_response))
            
            st.success("✅ Complete Brand Voice Guidelines document generated successfully!")
            
        except Exception as e:
            st.error(f"Guidelines synthesis failed: {str(e)}")
            return False, {}
        
        # Combine with metadata for comprehensive guidelines finalizer output
        complete_guidelines_finalizer = {
            "guidelines_document": guidelines_data,
            "generation_timestamp": datetime.now().isoformat(),
            "client_name": client_name,
            "workflow_completion_summary": workflow_summary,
            "document_stats": {
                "voice_traits_included": len(voice_traits_data.get("core_voice_traits", [])),
                "reference_examples_included": len(content_rewriter_data.get("transformations", {}).get("transformed_content", [])),
                "competitors_analyzed": len(gap_data.get("competitors", [])),
                "content_channels_covered": len(content_data.get("content_samples", [])),
                "total_workflow_steps": 8
            }
        }
        
        # Display comprehensive final results
        st.subheader("🎉 Brand Voice Guidelines - COMPLETE!")
        
        # Show document overview
        doc_overview = guidelines_data.get("brand_voice_guidelines", {}).get("document_overview", {})
        st.write(f"**Document Title:** {doc_overview.get('title', 'Brand Voice Guidelines')}")
        st.write(f"**Executive Summary:** {doc_overview.get('executive_summary', 'Comprehensive brand voice strategy complete')}")
        
        # Show key components summary
        brand_foundation = guidelines_data.get("brand_voice_guidelines", {}).get("brand_foundation", {})
        target_persona = guidelines_data.get("brand_voice_guidelines", {}).get("target_persona", {})
        voice_traits = guidelines_data.get("brand_voice_guidelines", {}).get("voice_traits", [])
        
        st.write("**Key Components Included:**")
        st.write(f"• **Brand Foundation:** Mission, {len(brand_foundation.get('core_values', []))} core values, positioning")
        st.write(f"• **Target Persona:** {target_persona.get('persona_name', 'Detailed persona profile')}")
        st.write(f"• **Voice Traits:** {len(voice_traits)} comprehensive traits with Do/Don't guidance")
        st.write(f"• **Channel Adaptations:** Website, social media, email marketing guidelines")
        st.write(f"• **Competitive Positioning:** Strategic differentiation and market positioning")
        st.write(f"• **Reference Examples:** {len(guidelines_data.get('brand_voice_guidelines', {}).get('reference_examples', []))} before/after content examples")
        st.write(f"• **Implementation Framework:** Step-by-step usage guide and quality checklist")
        
        # Show quick reference highlights
        quick_ref = guidelines_data.get("brand_voice_guidelines", {}).get("quick_reference", {})
        if quick_ref:
            st.write("**Quick Reference Included:**")
            st.write(f"• Voice traits summary, persona key points, emergency guidelines")
            st.write(f"• Do/Don't checklist for immediate decision-making")
        
        # Show final statistics
        st.write("**Workflow Completion Statistics:**")
        stats = complete_guidelines_finalizer["document_stats"]
        st.write(f"• **{stats['total_workflow_steps']} Complete Steps:** From foundation to final guidelines")
        st.write(f"• **{stats['voice_traits_included']} Voice Traits:** Persona-optimized with examples")
        st.write(f"• **{stats['competitors_analyzed']} Competitors Analyzed:** Strategic positioning developed")
        st.write(f"• **{stats['reference_examples_included']} Content Examples:** Before/after transformations")
        st.write(f"• **{stats['content_channels_covered']} Content Channels:** Cross-platform strategy")
        
        # Save results to Notion's Deep_Research_Workflow field
        save_success = db_manager.save_deep_research_step(
            client_page_id, 
            "guidelines_finalizer", 
            complete_guidelines_finalizer
        )
        
        if save_success:
            st.success("🎉 **WORKFLOW COMPLETE!** Brand Voice Guidelines saved to Notion successfully!")
            st.balloons()  # Celebration!
            
            # Show final call-to-action
            st.info("🚀 **Ready to take over the world!** Your comprehensive Brand Voice Guidelines are now available in Notion and ready for immediate use by writers and AI tools.")
            
            return True, complete_guidelines_finalizer
        else:
            st.error("Failed to save guidelines finalizer results")
            return False, {}

    except Exception as e:
        st.error(f"Guidelines finalizer failed: {str(e)}")
        return False, {}


def show_deep_research_workflow(db_manager, client_page_id, client_name, brand_data):
    """
    Progressive disclosure of Deep Research Workflow steps
    Only shows after Brand Builder completion
    """
    st.markdown("---")
    st.subheader("🔬 Deep Research Workflow")
    st.write("**Ready to dive deeper?** Take your brand analysis to the next level with our comprehensive 8-step research workflow.")
    
    # Show workflow overview
    with st.expander("📋 View Complete Workflow Overview"):
        st.write("""
        **8-Step Deep Research Process:**
        1. ✅ **Brand Builder** - Foundation complete!
        2. **Content Collector** - Identify key brand communications
        3. **Voice Auditor** - Analyze voice consistency 
        4. **Audience Definer** - Build detailed persona
        5. **Voice Traits Builder** - Extract actionable voice traits
        6. **Gap Analyzer** - Competitive intelligence analysis
        7. **Content Rewriter** - Transform content with insights
        8. **Guidelines Finalizer** - Complete Brand Voice Guidelines
        
        Each step builds on the previous one to create your turnkey Brand Voice Guidelines!
        """)
    
    # Workflow is always available - users can proceed with whatever info they have
    if not brand_data or not brand_data.get("client_name"):
        st.info("💡 **Tip:** The more brand information you provide above, the better your Deep Research Workflow results will be. But you can start with whatever you have!")
    
    # Check workflow status
    workflow_data = db_manager.get_deep_research_data(client_page_id)
    
    # Step 2: Content Collector
    step2_complete = db_manager.get_workflow_step_status(client_page_id, "content_collector")
    
    if not step2_complete:
        st.info("**📍 NEXT: Step 2: Content Collector** - Identify key brand communications across channels")
        
        if st.button("🚀 Start Step 2: Content Collection", key="start_content_collector"):
            with st.spinner("Analyzing brand context and identifying optimal content samples..."):
                success, _ = run_content_collector_step(db_manager, client_page_id, client_name, brand_data)
                if success:
                    st.rerun()  # Refresh to show next step
    else:
        st.success("✅ **Step 2: Content Collector** - Complete")
        
        # Show results briefly
        content_data = workflow_data.get("content_collector", {}).get("data", {})
        content_samples = content_data.get("content_samples", [])
        if content_samples:
            st.write(f"**Found {len(content_samples)} content samples** across different channels")
            
            # Show option to re-run if needed
            if st.button("🔄 Re-run Content Collection", key="rerun_content_collector"):
                with st.spinner("Re-analyzing content collection strategy..."):
                    success, _ = run_content_collector_step(db_manager, client_page_id, client_name, brand_data)
                    if success:
                        st.rerun()
        
        # Step 3: Voice Auditor
        step3_complete = db_manager.get_workflow_step_status(client_page_id, "voice_auditor")
        
        if not step3_complete:
            st.info("**Step 3: Voice Auditor** - Analyze content samples for voice consistency")
            
            if st.button("🎯 Start Voice Audit", key="start_voice_auditor"):
                with st.spinner("Analyzing brand voice patterns and consistency..."):
                    success, _ = run_voice_auditor_step(db_manager, client_page_id, client_name, brand_data, content_data)
                    if success:
                        st.rerun()  # Refresh to show next step
        else:
            st.success("✅ **Step 3: Voice Auditor** - Complete")
            
            # Show results briefly
            voice_data = workflow_data.get("voice_auditor", {}).get("data", {})
            audit_summary = voice_data.get("voice_audit_summary", {})
            if audit_summary:
                st.write(f"**Voice Consistency:** {audit_summary.get('overall_consistency', 'Analysis complete')}")
                
                # Show option to re-run if needed
                if st.button("🔄 Re-run Voice Audit", key="rerun_voice_auditor"):
                    with st.spinner("Re-analyzing voice patterns..."):
                        success, _ = run_voice_auditor_step(db_manager, client_page_id, client_name, brand_data, content_data)
                        if success:
                            st.rerun()
            
            # Step 4: Audience Definer
            step4_complete = db_manager.get_workflow_step_status(client_page_id, "audience_definer")
            
            if not step4_complete:
                st.info("**Step 4: Audience Definer** - Create comprehensive audience persona")
                
                if st.button("👤 Build Detailed Persona", key="start_audience_definer"):
                    with st.spinner("Synthesizing data sources to build comprehensive audience persona..."):
                        success, _ = run_audience_definer_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data)
                        if success:
                            st.rerun()  # Refresh to show next step
            else:
                st.success("✅ **Step 4: Audience Definer** - Complete")
                
                # Show persona summary
                audience_data = workflow_data.get("audience_definer", {}).get("data", {})
                persona_identity = audience_data.get("persona_identity", {})
                if persona_identity:
                    st.write(f"**Persona Created:** {persona_identity.get('name', 'Unknown')} - {persona_identity.get('title', 'Unknown Role')}")
                    
                    # Show option to re-run if needed
                    if st.button("🔄 Re-build Persona", key="rerun_audience_definer"):
                        with st.spinner("Rebuilding detailed audience persona..."):
                            success, _ = run_audience_definer_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data)
                            if success:
                                st.rerun()
                
                # Step 5: Voice Traits Builder
                step5_complete = db_manager.get_workflow_step_status(client_page_id, "voice_traits_builder")
                
                if not step5_complete:
                    st.info("**Step 5: Voice Traits Builder** - Extract persona-optimized voice traits")
                    
                    if st.button("🎯 Build Voice Traits", key="start_voice_traits_builder"):
                        with st.spinner("Engineering voice traits optimized for your target persona..."):
                            success, _ = run_voice_traits_builder_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data, audience_data)
                            if success:
                                st.rerun()  # Refresh to show next step
                else:
                    st.success("✅ **Step 5: Voice Traits Builder** - Complete")
                    
                    # Show voice traits summary
                    traits_data = workflow_data.get("voice_traits_builder", {}).get("data", {})
                    traits_summary = traits_data.get("voice_traits_summary", {})
                    core_traits = traits_data.get("core_voice_traits", [])
                    
                    if traits_summary and core_traits:
                        st.write(f"**Voice Strategy:** {traits_summary.get('strategy_overview', 'Voice traits extracted')}")
                        st.write(f"**{len(core_traits)} Core Traits:** {', '.join([trait.get('trait_name', 'Unknown') for trait in core_traits])}")
                        
                        # Show option to re-run if needed
                        if st.button("🔄 Re-build Voice Traits", key="rerun_voice_traits_builder"):
                            with st.spinner("Re-engineering voice traits..."):
                                success, _ = run_voice_traits_builder_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data, audience_data)
                                if success:
                                    st.rerun()
                    
                    # Step 6: Gap Analyzer
                    step6_complete = db_manager.get_workflow_step_status(client_page_id, "gap_analyzer")
                    
                    if not step6_complete:
                        st.info("**Step 6: Gap Analyzer** - Competitive intelligence and strategic positioning")
                        
                        if st.button("🎯 Start Gap Analysis", key="start_gap_analyzer"):
                            with st.spinner("Conducting competitive intelligence analysis..."):
                                success, _ = run_gap_analyzer_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data, audience_data, traits_data)
                                if success:
                                    st.rerun()  # Refresh to show next step
                    else:
                        st.success("✅ **Step 6: Gap Analyzer** - Complete")
                        
                        # Show gap analysis summary
                        gap_data = workflow_data.get("gap_analyzer", {}).get("data", {})
                        strategic_analysis = gap_data.get("strategic_analysis", {})
                        competitors = gap_data.get("competitors", [])
                        
                        if strategic_analysis and competitors:
                            st.write(f"**Strategic Positioning:** {strategic_analysis.get('positioning_summary', 'Competitive analysis complete')}")
                            st.write(f"**{len(competitors)} Competitors Analyzed:** {', '.join([comp.get('name', 'Unknown') for comp in competitors[:3]])}{'...' if len(competitors) > 3 else ''}")
                            
                            # Show option to re-run if needed
                            if st.button("🔄 Re-run Gap Analysis", key="rerun_gap_analyzer"):
                                with st.spinner("Re-analyzing competitive landscape..."):
                                    success, _ = run_gap_analyzer_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data, audience_data, traits_data)
                                    if success:
                                        st.rerun()
                        
                        # Step 7: Content Rewriter
                        step7_complete = db_manager.get_workflow_step_status(client_page_id, "content_rewriter")
                        
                        if not step7_complete:
                            st.info("**Step 7: Content Rewriter** - Transform content using voice traits and insights")
                            
                            if st.button("✨ Start Content Transformation", key="start_content_rewriter"):
                                with st.spinner("Transforming content samples with voice traits and insights..."):
                                    success, _ = run_content_rewriter_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data, audience_data, traits_data, gap_data)
                                    if success:
                                        st.rerun()  # Refresh to show next step
                        else:
                            st.success("✅ **Step 7: Content Rewriter** - Complete")
                            
                            # Show content rewriter summary
                            rewriter_data = workflow_data.get("content_rewriter", {}).get("data", {})
                            transformations = rewriter_data.get("transformations", {})
                            transformation_results = transformations.get("transformation_results", {})
                            
                            if transformation_results:
                                st.write(f"**Transformation Summary:** {transformation_results.get('transformation_summary', 'Content transformation complete')}")
                                st.write(f"**Content Samples Transformed:** {transformation_results.get('successful_transformations', 0)}")
                                
                                # Show option to re-run if needed
                                if st.button("🔄 Re-run Content Transformation", key="rerun_content_rewriter"):
                                    with st.spinner("Re-transforming content samples..."):
                                        success, _ = run_content_rewriter_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data, audience_data, traits_data, gap_data)
                                        if success:
                                            st.rerun()
                            
                            # Step 8: Guidelines Finalizer
                            step8_complete = db_manager.get_workflow_step_status(client_page_id, "guidelines_finalizer")
                            
                            if not step8_complete:
                                st.info("**Step 8: Guidelines Finalizer** - Create turnkey Brand Voice Guidelines document")
                                
                                if st.button("🎉 Create Final Guidelines", key="start_guidelines_finalizer"):
                                    with st.spinner("Synthesizing complete Brand Voice Guidelines document..."):
                                        success, _ = run_guidelines_finalizer_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data, audience_data, traits_data, gap_data, rewriter_data)
                                        if success:
                                            st.rerun()  # Refresh to show completion
                            else:
                                st.success("✅ **Step 8: Guidelines Finalizer** - COMPLETE!")
                                
                                # Show guidelines document summary
                                finalizer_data = workflow_data.get("guidelines_finalizer", {}).get("data", {})
                                guidelines_doc = finalizer_data.get("guidelines_document", {}).get("brand_voice_guidelines", {})
                                doc_overview = guidelines_doc.get("document_overview", {})
                                
                                if guidelines_doc:
                                    st.write(f"**Document:** {doc_overview.get('title', 'Brand Voice Guidelines')}")
                                    st.write(f"**Voice Traits:** {len(guidelines_doc.get('voice_traits', []))} comprehensive traits")
                                    st.write(f"**Reference Examples:** {len(guidelines_doc.get('reference_examples', []))} before/after examples")
                                    
                                    # Show final celebration
                                    st.success("🎉 **WORKFLOW COMPLETE!** Comprehensive Brand Voice Guidelines ready for immediate use!")
                                    
                                    # Show option to re-run if needed
                                    if st.button("🔄 Re-generate Guidelines", key="rerun_guidelines_finalizer"):
                                        with st.spinner("Re-generating Brand Voice Guidelines..."):
                                            success, _ = run_guidelines_finalizer_step(db_manager, client_page_id, client_name, brand_data, content_data, voice_data, audience_data, traits_data, gap_data, rewriter_data)
                                            if success:
                                                st.rerun()


def run_brand_builder():
    st.title("Brand Builder")
    st.write("Build comprehensive brand profiles and collect foundational client information")
    
    # Initialize Notion database manager
    db_manager = research_tools_framework.NotionDatabaseManager()
    
    # Client selector sidebar with option to create new clients
    client_page_id, selected_client, _ = research_tools_framework.client_selector_sidebar(
        db_manager=db_manager, 
        allow_new_client=True
    )
    
    if not client_page_id:
        st.info("Please select a client from the sidebar or create a new one to get started.")
        
        # Show instructions for new users
        with st.expander("How to use the Brand Builder"):
            st.markdown("""
            ### Getting Started
            
            The Brand Builder is the first step in developing a client's brand voice. Here's how to use it:
            
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
        
        # Single enhance button at the top - replace all the redundant buttons
        st.markdown("### 🚀 AI Enhancement (Optional)")
        st.info("**Optional:** Add your website URL and let our AI enhance your brand information automatically.")
        
        # Website URL input
        website_url = st.text_input(
            "Website URL (optional)", 
            value=default_values["website_url"],
            help="Enter your website URL for AI enhancement"
        )
        
        if st.button("✨ Enhance with AI", key="enhance_with_ai", type="primary"):
            with st.spinner("🤖 AI is enhancing your brand profile..."):
                # Use existing data as base
                current_form_data = {
                    "industry": client_profile.get("Industry", ""),
                    "product_service_description": client_profile.get("Product_Service_Description", ""),
                    "current_target_audience": client_profile.get("Current_Target_Audience", ""),
                    "ideal_target_audience": client_profile.get("Ideal_Target_Audience", ""),
                    "brand_values": client_profile.get("Brand_Values", ""),
                    "brand_mission": client_profile.get("Brand_Mission", ""),
                    "desired_emotional_impact": client_profile.get("Desired_Emotional_Impact", ""),
                    "brand_personality": client_profile.get("Brand_Personality", ""),
                    "words_tones_to_avoid": client_profile.get("Words_Tones_To_Avoid", "")
                }
                
                # Try comprehensive analysis if website provided, otherwise just brand voice analysis
                if website_url:
                    success, analysis_result, error_msg = comprehensive_client_analysis(
                        selected_client, 
                        client_profile.get("Industry", ""), 
                        website_url, 
                        current_form_data, 
                        True
                    )
                else:
                    success, analysis_result, error_msg = analyze_brand_voice(
                        selected_client, {}, current_form_data
                    )
                
                if success:
                    # Save enhanced data to Notion
                    notion_data = {
                        "Website": website_url or client_profile.get("Website", ""),
                        "Industry": analysis_result.get("industry", client_profile.get("Industry", "")),
                        "Product_Service_Description": analysis_result.get("company_description", analysis_result.get("product_service_description", client_profile.get("Product_Service_Description", ""))),
                        "Current_Target_Audience": analysis_result.get("current_target_audience", ""),
                        "Ideal_Target_Audience": analysis_result.get("ideal_target_audience", ""),
                        "Brand_Values": ', '.join(analysis_result.get("brand_values", [])) if isinstance(analysis_result.get("brand_values"), list) else analysis_result.get("brand_values", ""),
                        "Brand_Mission": analysis_result.get("brand_mission", ""),
                        "Desired_Emotional_Impact": ', '.join(analysis_result.get("desired_emotional_impact", [])) if isinstance(analysis_result.get("desired_emotional_impact"), list) else analysis_result.get("desired_emotional_impact", ""),
                        "Brand_Personality": ', '.join(analysis_result.get("brand_personality_traits", [])) if isinstance(analysis_result.get("brand_personality_traits"), list) else analysis_result.get("brand_personality", ""),
                        "Words_Tones_To_Avoid": ', '.join(analysis_result.get("words_tones_to_avoid", [])) if isinstance(analysis_result.get("words_tones_to_avoid"), list) else analysis_result.get("words_tones_to_avoid", ""),
                    }
                    
                    update_success, update_error = update_client_with_retry(db_manager, client_page_id, notion_data)
                    if update_success:
                        # Mark as complete regardless of how much data we have
                        db_manager.mark_tool_complete(client_page_id, "brand_builder")
                        st.success("✅ **AI Enhancement Complete!** Your brand profile has been enhanced.")
                        st.rerun()
                    else:
                        st.warning(f"Enhancement complete but save failed: {update_error}")
                        # Still mark as complete so user can proceed
                        db_manager.mark_tool_complete(client_page_id, "brand_builder")
                else:
                    st.warning(f"AI enhancement had issues: {error_msg}")
                    # Still mark as complete so user can proceed
                    db_manager.mark_tool_complete(client_page_id, "brand_builder")
                    st.info("Don't worry - you can still proceed to the Deep Research Workflow!")
        
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
            
            # Explain what the form does
            st.markdown("### 📋 Complete Your Brand Information")
            st.info("""
            **Fill out what you know:** Enter your brand information below. Don't worry if you don't have everything - you can:
            
            💾 **Save your form data** to preserve your work  
            ✨ **Use 'Enhance with AI' above** for automatic improvements  
            🚀 **Start the Deep Research Workflow** to build comprehensive guidelines  
            
            All fields are optional - work with what you have!
            """)
            
            submit_button = st.form_submit_button("💾 Save Form Data")
        
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
            
            # Save form data directly without AI analysis (use the "Enhance with AI" button above for that)
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
                    db_manager.mark_tool_complete(client_page_id, "brand_builder")
                    st.success("✅ **Form Data Saved!** Your brand information has been saved to Notion.")
                    
                    # Add clear call-to-action for next steps
                    st.info("🚀 **Ready for next step!** Use the 'Enhance with AI' button above for AI enhancement, or scroll down to start the Deep Research Workflow.")
                    
                    # 🚀 PROGRESSIVE WORKFLOW: Show Deep Research option after Brand Builder completion
                    show_deep_research_workflow(db_manager, client_page_id, selected_client, parsed_data)
                else:
                    st.error(f"❌ {error_msg}")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please make sure your Notion database is properly set up and refresh the page.")
    
    # ALWAYS show Deep Research Workflow - users should be able to proceed with whatever info they have
    if client_page_id and selected_client:
        # Get whatever brand data exists (could be minimal)
        basic_brand_data = {
            "client_name": selected_client,
            "industry": client_profile.get("Industry", ""),
            "product_service": client_profile.get("Product_Service_Description", ""),
            "brand_mission": client_profile.get("Brand_Mission", "")
        }
        
        # Always mark brand builder as complete so workflow is accessible
        db_manager.mark_tool_complete(client_page_id, "brand_builder")
        
        # Show the workflow regardless of completion status
        show_deep_research_workflow(db_manager, client_page_id, selected_client, basic_brand_data)

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
    run_brand_builder()