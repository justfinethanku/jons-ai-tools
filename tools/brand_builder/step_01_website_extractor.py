"""
Step 1: Website Extractor Tool

Extracts basic company information and contact details from website 
using enhanced multi-content approach. This is the first step in the 
Brand Builder workflow.

Can be run independently for testing:
    python -m tools.brand_builder.step_01_website_extractor --website https://example.com --client "Test Client"
"""

import json
import requests
import trafilatura
import re
from bs4 import BeautifulSoup
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.brand_builder import WorkflowStep, WorkflowContext, StepResult
from frameworks import universal_framework
from frameworks.prompt_wrappers import prompt_wrapper


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
                    extracted_text += "\\n\\n=== EXTRACTED CONTACT INFORMATION ===\\n" + "\\n".join(contact_patterns)
                
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
            text = '\\n'.join(chunk for chunk in chunks if chunk)
            
            # Extract contact information patterns from text
            contact_info = []
            
            # Find email patterns in text
            email_pattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
            emails = re.findall(email_pattern, text)
            for email in set(emails):  # Remove duplicates
                contact_info.append(f"Email pattern found: {email}")
            
            # Find phone patterns
            phone_patterns = [
                r'\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b',  # XXX-XXX-XXXX or XXX.XXX.XXXX
                r'\\(\\d{3}\\)\\s*\\d{3}[-.]?\\d{4}',    # (XXX) XXX-XXXX
                r'\\+1[-\\s]?\\d{3}[-\\s]?\\d{3}[-\\s]?\\d{4}'  # +1-XXX-XXX-XXXX
            ]
            for pattern in phone_patterns:
                phones = re.findall(pattern, text)
                for phone in set(phones):  # Remove duplicates
                    contact_info.append(f"Phone pattern found: {phone}")
            
            # Find social media URLs in text
            social_patterns = [
                r'https?://(?:www\\.)?linkedin\\.com/[^\\s]+',
                r'https?://(?:www\\.)?twitter\\.com/[^\\s]+', 
                r'https?://(?:www\\.)?facebook\\.com/[^\\s]+',
                r'https?://(?:www\\.)?instagram\\.com/[^\\s]+',
                r'https?://(?:www\\.)?youtube\\.com/[^\\s]+'
            ]
            for pattern in social_patterns:
                social_urls = re.findall(pattern, text)
                for url in set(social_urls):
                    contact_info.append(f"Social media URL found: {url}")
            
            if contact_info:
                text += "\\n\\n=== EXTRACTED CONTACT INFORMATION ===\\n" + "\\n".join(contact_info)
            
            return text
        else:
            return f"Error: HTTP {response.status_code}"
            
    except Exception as e:
        return f"Error extracting content: {str(e)}"


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


class WebsiteExtractorTool(WorkflowStep):
    """
    Step 1: Extract basic company information and contact details from website
    """
    
    def get_required_inputs(self):
        return ['client_name', 'website_url']
    
    def get_output_fields(self):
        return [
            'industry', 'company_description', 'key_products_services',
            'contact_email', 'phone_number', 'address',
            'linkedin_url', 'twitter_url', 'facebook_url', 'instagram_url', 'youtube_url',
            'other_social_media', 'target_markets', 'company_size_indicators', 'geographical_presence'
        ]
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """Execute website extraction"""
        client_name = context.get('client_name')
        website_url = context.get('website_url')
        
        try:
            # Extract targeted content from multiple pages
            content_sections = extract_targeted_content(website_url)
            
            if not content_sections:
                return StepResult(
                    success=False,
                    data={},
                    errors=["Could not extract content from website"],
                    warnings=[],
                    step_name=self.name
                )
            
            # Build multi-content input structure
            content_input = "=== WEBSITE CONTENT ANALYSIS ===\\n\\n"
            
            for section, content in content_sections.items():
                if content:
                    # Clean content for each section
                    clean_content = content.replace('"', "'").replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' ')
                    content_input += f"=== {section.upper()} PAGE ===\\n{clean_content}\\n\\n"
            
            # Define extraction schema
            schema = {
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
            }
            
            # Get prompt and temperature from modular system
            prompt, temperature = prompt_wrapper.get_website_extraction_prompt(
                client_name=client_name,
                website_url=website_url,
                content_input=content_input,
                schema=schema
            )
            
            # Create JSON schema for API validation
            api_schema = {
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
            
            # Call API
            response = universal_framework.call_gemini_api(prompt, response_schema=api_schema, temperature=temperature)
            
            # Check for API error responses before JSON parsing
            if response.startswith("Error:"):
                return StepResult(
                    success=False,
                    data={},
                    errors=[f"API call failed: {response}"],
                    warnings=[],
                    step_name=self.name
                )
            
            result_data = json.loads(response)
            
            return StepResult(
                success=True,
                data=result_data,
                errors=[],
                warnings=[],
                step_name=self.name
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                data={},
                errors=[f"Website extraction failed: {str(e)}"],
                warnings=[],
                step_name=self.name
            )


def main():
    """CLI interface for testing step independently"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract website data for Brand Builder')
    parser.add_argument('--website', required=True, help='Website URL to extract from')
    parser.add_argument('--client', required=True, help='Client name')
    parser.add_argument('--output', help='Output file for results (JSON)')
    
    args = parser.parse_args()
    
    # Create context
    context = WorkflowContext({
        'client_name': args.client,
        'website_url': args.website
    })
    
    # Run step
    step = WebsiteExtractorTool()
    result = step.execute(context)
    
    # Output results
    if result.success:
        print("✅ Website extraction successful!")
        print(f"📊 Extracted {len(result.data)} fields")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result.data, f, indent=2)
            print(f"💾 Results saved to {args.output}")
        else:
            print("📋 Results:")
            for key, value in result.data.items():
                print(f"  {key}: {value}")
    else:
        print("❌ Website extraction failed!")
        for error in result.errors:
            print(f"  Error: {error}")


if __name__ == "__main__":
    main()