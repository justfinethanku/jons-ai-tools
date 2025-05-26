"""
step01_website_extractor
AUTOMATED WEBSITE EXTRACTOR - CLEAN ARCHITECTURE
===============================================

This is the foundation of the Brand Builder system. It takes ONLY:
- Client name
- Website URL

And delivers:
- Complete sitemap discovery
- Comprehensive content extraction  
- Immediate Notion database creation
- Automatic progression to Step 2

NO USER INPUT REQUIRED AFTER INITIAL DATA
"""

import json
import requests
import trafilatura
import re
import os
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import shared utilities and structured logging
from frameworks.shared_utils import safe_json_parse
from frameworks.logging_manager import get_logger, LoggedOperation

# Workflow base classes
class WorkflowContext:
    """Simple context for passing data between workflow steps"""
    def __init__(self):
        self.inputs = {}
        self.outputs = {}
    
    def set_input(self, key, value):
        self.inputs[key] = value
    
    def get_input(self, key, default=None):
        return self.inputs.get(key, default)
    
    def set_output(self, key, value):
        self.outputs[key] = value
    
    def get_output(self, key, default=None):
        return self.outputs.get(key, default)

class StepResult:
    """Simple result object for workflow steps"""
    def __init__(self, success=False, data=None, errors=None, warnings=None, step_name=None):
        self.success = success
        self.data = data or {}
        self.errors = errors or []
        self.warnings = warnings or []
        self.step_name = step_name
        # Legacy compatibility
        self.outputs = data or {}
        self.error = errors[0] if errors else None

class WorkflowStep:
    """Base class for workflow steps"""
    def execute(self, context: WorkflowContext) -> StepResult:
        raise NotImplementedError("Subclasses must implement execute method")

from frameworks import universal_framework
from frameworks.database_manager import NotionDatabaseManager
from prompts.research_prompts.step01_prompts.extract_sitemap import get_page_discovery_prompt
from prompts.research_prompts.step01_prompts.extract_client_info import (
    get_comprehensive_analysis_prompt,
    get_analysis_schema_optimized as get_analysis_schema
 )
class AutomatedWebsiteExtractor(WorkflowStep):
    """
    FULLY AUTOMATED website extraction pipeline
    Input: client_name + website_url
    Output: Complete brand analysis + auto-progression to step 2
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize logger
        self.logger = get_logger("website_extractor")
        
        # Initialize database manager with error handling
        try:
            self.db_manager = NotionDatabaseManager()
            self.logger.log_operation_success("initialize_database_manager")
        except Exception as e:
            self.logger.log_operation_failure("initialize_database_manager", str(e))
            self.logger.warning("Running in OFFLINE mode - data will be saved to files only")
            self.db_manager = None
        
        # Set up data directories
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        os.makedirs(os.path.join(self.data_dir, 'sitemaps'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'content'), exist_ok=True)
        
        # Track client for potential offline mode
        self.client_id = None
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """
        MAIN PIPELINE: Execute the complete automated extraction workflow
        """
        self.logger.info("Starting automated website extraction pipeline")
        
        try:
            # Get required inputs
            client_name = context.get_input("client_name")
            website_url = context.get_input("website_url")
            
            if not client_name or not website_url:
                return StepResult(
                    success=False,
                    data={},
                    errors=["Missing required inputs: client_name and website_url"],
                    warnings=[],
                    step_name="website_extractor"
                )
            
            self.logger.info("Starting extraction", client_name=client_name, website_url=website_url)
            
            # Step 1: Create Notion client entry
            with LoggedOperation("create_notion_client", logger=self.logger, client_name=client_name):
                self._create_notion_client(client_name, website_url)
            
            # Step 2: Generate comprehensive sitemap
            with LoggedOperation("generate_sitemap", logger=self.logger, website_url=website_url):
                sitemap = self._generate_comprehensive_sitemap(website_url)
                sitemap = self._filter_sitemap_urls(sitemap)
                sitemap_file = self._save_sitemap(client_name, sitemap)
                self.logger.info("Sitemap saved", file_path=sitemap_file, page_count=len(sitemap))
            
            # Step 3: Extract content from all pages
            with LoggedOperation("extract_all_content", logger=self.logger, client_name=client_name):
                all_content = self._extract_all_content(sitemap)
                content_file = self._save_content(client_name, all_content)
                
                total_words = sum(data['word_count'] for data in all_content.values())
                self.logger.info("Content extracted", 
                               page_count=len(all_content), 
                               total_words=total_words,
                               content_file=content_file)
            
            # Step 4: Analyze content with Gemini
            with LoggedOperation("analyze_content", logger=self.logger, client_name=client_name):
                analysis_result = self._analyze_comprehensive_content(client_name, website_url, all_content)
                self.logger.info("Content analysis complete")
            
            # Step 5: Update Notion with comprehensive data
            with LoggedOperation("update_notion", logger=self.logger, client_id=self.client_id):
                self._update_notion_client(analysis_result)
                self.logger.info("Notion database updated")
            
            # Step 6: Prepare for Step 2
            self.logger.info("Preparing for Step 2")
            context.set_output("client_id", self.client_id)
            context.set_output("website_analysis", analysis_result)
            context.set_output("content_file", content_file)
            context.set_output("sitemap_file", sitemap_file)
            
            self.logger.log_operation_success("website_extraction_pipeline",
                                            client_name=client_name,
                                            client_id=self.client_id)
            
            # Handoff to Step 2: Brand Analyzer
            if self.client_id:
                self.logger.info("Handing off to Step 2: Brand Analyzer")
                from .step_02_brand_analyzer import BrandAnalyzer
                step2 = BrandAnalyzer()
                step2_result = step2.execute(context)
                if not step2_result.success:
                    self.logger.error(f"Step 2 failed: {step2_result.errors}")
            
            return StepResult(
                success=True,
                data={
                    "analysis": analysis_result,
                    "content_file": content_file,
                    "sitemap_file": sitemap_file,
                    "client_id": self.client_id
                },
                errors=[],
                warnings=[],
                step_name="website_extractor"
            )
            
        except Exception as e:
            error_msg = f"Pipeline failed: {str(e)}"
            self.logger.log_operation_failure("website_extraction_pipeline", error_msg)
            return StepResult(
                success=False,
                data={},
                errors=[error_msg],
                warnings=[],
                step_name="website_extractor"
            )
    
    def _create_notion_client(self, client_name, website_url):
        """Step 1: Create initial Notion client entry"""
        if not self.db_manager:
            self.logger.warning("Skipping Notion client creation - running in offline mode")
            return
        
        try:
            # Check if client already exists
            existing_client_id = self.db_manager.get_client_page_id(client_name)
            if existing_client_id:
                self.client_id = existing_client_id
                self.logger.info("Found existing client", client_id=self.client_id)
                # Update status to show we're extracting
                self._update_client_status("Extracting Website Data")
            else:
                # Create new client entry
                self.client_id = self.db_manager.create_new_client(client_name, "Unknown")
                self.logger.log_operation_success("create_new_client", 
                                                client_id=self.client_id,
                                                client_name=client_name)
                
                # Update with website URL and status
                if self.client_id:
                    self._update_client_basic_info(website_url)
            
        except Exception as e:
            self.logger.log_operation_failure("create_notion_client", str(e))
            self.logger.warning("Continuing in offline mode")
            self.db_manager = None
    
    def _update_client_status(self, status):
        """Update client status in Notion"""
        if not self.client_id or not self.db_manager:
            return
        try:
            self.db_manager.update_client_profile(self.client_id, {"Research_Status": status})
        except Exception as e:
            self.logger.warning("Failed to update client status", error=str(e))
    
    def _update_client_basic_info(self, website_url):
        """Update basic client info in Notion AI Client Library"""
        if not self.client_id or not self.db_manager:
            return
        try:
            # Update with Website URL (matches schema.md field name)
            self.db_manager.update_client_profile(self.client_id, {
                "Website": website_url,
                "Last_Updated": datetime.now().strftime("%Y-%m-%d")
            })
        except Exception as e:
            self.logger.warning("Failed to update basic info", error=str(e))
    
    def _generate_comprehensive_sitemap(self, website_url):
        """Step 2: Generate comprehensive sitemap using multiple methods"""
        all_pages = set()
        
        self.logger.info("Discovering pages using multiple methods")
        
        # Method 1: Try to find sitemap.xml files
        sitemap_urls = [
            f"{website_url}/sitemap.xml",
            f"{website_url}/sitemap_index.xml",
            f"{website_url}/sitemaps.xml"
        ]
        
        for sitemap_url in sitemap_urls:
            pages = self._extract_from_sitemap_xml(sitemap_url)
            all_pages.update(pages)
            if pages:
                self.logger.info("Found pages in sitemap", 
                               sitemap_url=sitemap_url, 
                               page_count=len(pages))
        
        # Method 2: Homepage analysis for common page discovery
        homepage_pages = self._discover_pages_from_homepage(website_url)
        all_pages.update(homepage_pages)
        self.logger.info("Found pages from homepage", page_count=len(homepage_pages))
        
        # Method 3: Use AI to intelligently guess likely pages
        ai_pages = self._gemini_page_discovery(website_url)
        all_pages.update(ai_pages)
        self.logger.info("AI suggested pages", page_count=len(ai_pages))
        
        # Convert to list and ensure homepage is first
        pages_list = list(all_pages)
        if website_url in pages_list:
            pages_list.remove(website_url)
        pages_list.insert(0, website_url)
        
        return pages_list
    
    def _extract_from_sitemap_xml(self, sitemap_url):
        """Extract URLs from sitemap.xml"""
        try:
            response = requests.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                urls = [loc.text for loc in soup.find_all('loc')]
                return [url for url in urls if self._is_valid_page_url(url)]
        except:
            pass
        return []
    
    def _discover_pages_from_homepage(self, website_url):
        """Discover pages by analyzing homepage links"""
        try:
            response = requests.get(website_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                base_domain = urlparse(website_url).netloc
                
                pages = set()
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(website_url, href)
                    
                    # Only include pages from same domain  
                    if urlparse(full_url).netloc == base_domain and self._is_valid_page_url(full_url):
                        pages.add(full_url)
                
                return list(pages)
        except:
            pass
        return []
    
    def _gemini_page_discovery(self, website_url):
        """Use AI to discover likely     pages"""
        try:
            prompt = get_page_discovery_prompt(website_url)
            response = universal_framework.call_openai_api(
                prompt, 
                model="gpt-4.1-2025-04-14"
            )
            
            if not response or response.startswith("Error:"):
                return []
            
            # Parse URLs from response
            urls = []
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('http') and self._is_valid_page_url(line):
                    urls.append(line)
            
            return urls[:15]  # Limit to 15 suggestions
            
        except Exception as e:
            self.logger.warning("Gemini page discovery failed", error=str(e))
            return []
    
    def _is_valid_page_url(self, url):
        """Check if URL is valid for content extraction"""
        if not url or not url.startswith('http'):
            return False
        
        # Skip file downloads, images, etc.
        skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.doc', '.docx']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip social media and external domains we don't want
        skip_domains = ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com']
        if any(domain in url.lower() for domain in skip_domains):
            return False
        
        return True
    
    def _filter_sitemap_urls(self, urls):
        """Exclude junk URLs before content extraction."""
        bad_patterns = [
            'blog', 'tag', 'category', 'news', 'article',
            'resource', 'author', 'page', '?page=', '&p='
        ]
        filtered = []
        for url in urls:
            if any(pattern in url.lower() for pattern in bad_patterns):
                continue
            filtered.append(url)
        return filtered
    
    def _save_sitemap(self, client_name, sitemap):
        """Save sitemap to file"""
        filename = f"{client_name.replace(' ', '_').lower()}_sitemap.json"
        filepath = os.path.join(self.data_dir, 'sitemaps', filename)
        
        sitemap_data = {
            'client_name': client_name,
            'generated_at': datetime.now().isoformat(),
            'total_pages': len(sitemap),
            'pages': sitemap
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sitemap_data, f, indent=2)
        
        return filepath
    
    def _extract_all_content(self, sitemap):
        """Step 3: Extract content from all pages in sitemap"""
        all_content = {}
        
        for i, url in enumerate(sitemap[:20], 1):  # Limit to first 20 pages for performance
            self.logger.info("Extracting page", 
                           page_number=i, 
                           total_pages=min(len(sitemap), 20),
                           url=url)
            
            try:
                content = self._extract_content_from_url(url)
                if content and not content.startswith("Error"):
                    # Limit content length per page
                    if len(content) > 3000:
                        content = content[:3000] + "...[truncated]"
                    
                    all_content[url] = {
                        'content': content,
                        'extracted_at': datetime.now().isoformat(),
                        'word_count': len(content.split())
                    }
                
                # Small delay to be respectful
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.warning("Failed to extract page", url=url, error=str(e))
        
        return all_content
    
    def _extract_content_from_url(self, url):
        """Extract clean text content from URL"""
        try:
            # Use trafilatura for best results
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                extracted = trafilatura.extract(
                    downloaded,
                    include_comments=False,
                    include_tables=True,
                    include_links=True
                )
                if extracted:
                    return extracted
            
            # Fallback to requests + BeautifulSoup
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Get text
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                return '\n'.join(chunk for chunk in chunks if chunk)
            
        except Exception as e:
            return f"Error extracting {url}: {str(e)}"
        
        return ""
    
    def _save_content(self, client_name, all_content):
        """Save all extracted content to file"""
        filename = f"{client_name.replace(' ', '_').lower()}_content.json"
        filepath = os.path.join(self.data_dir, 'content', filename)
        
        content_data = {
            'client_name': client_name,
            'extracted_at': datetime.now().isoformat(),
            'total_pages': len(all_content),
            'content': all_content
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2)
        
        return filepath
    
    def _analyze_comprehensive_content(self, client_name, website_url, all_content):
        """Step 4: Analyze all content with Gemini for comprehensive insights"""
        
        # Build comprehensive content input
        content_summary = f"=== COMPREHENSIVE WEBSITE ANALYSIS FOR {client_name} ===\n\n"
        content_summary += f"Website: {website_url}\n"
        content_summary += f"Total Pages Analyzed: {len(all_content)}\n\n"
        
        for url, data in all_content.items():
            page_name = url.split('/')[-1] or 'homepage'
            content_summary += f"=== PAGE: {page_name.upper()} ({url}) ===\n"
            content_summary += f"{data['content']}\n\n"  # First 1500 chars per page
        
        # Get analysis prompt from separated prompt file 
        prompt = get_comprehensive_analysis_prompt(client_name, website_url, content_summary)
        
        # Call OpenAI for analysis
        response = universal_framework.call_openai_api(
            prompt, 
            model="gpt-4.1-2025-04-14"
        )
        
        self.logger.debug("OpenAI response preview", response_preview=response[:200])
        
        if response.startswith("Error:"):
            raise Exception(f"OpenAI analysis failed: {response}")
        
        # Handle empty or invalid response
        if not response or not response.strip():
            self.logger.warning("OpenAI returned empty response, using fallback analysis")
            return self._create_fallback_analysis(client_name, website_url, all_content)
        
        # Try to parse JSON response using shared utility
        success, parsed_result = safe_json_parse(response)
        if success:
            return parsed_result
        else:
            self.logger.warning("JSON parsing failed, using fallback analysis")
            return self._create_fallback_analysis(client_name, website_url, all_content)
    
    def _create_fallback_analysis(self, client_name, website_url, all_content):
        """Create basic fallback analysis when Gemini fails"""
        self.logger.info("Creating fallback analysis")
        
        # Extract basic info from content
        # all_text = " ".join([data['content'] for data in all_content.values()])
        
        schema = get_analysis_schema()
        fallback_result = {}
        
        # Populate with basic extracted data or "Not found"
        for key, _ in schema.items():
            if key == "company_description":
                fallback_result[key] = f"{client_name} - analysis extracted from {website_url}"
            elif key == "key_products_services":
                fallback_result[key] = ["Service analysis pending"]
            elif key == "other_social_media":
                fallback_result[key] = []
            else:
                fallback_result[key] = "Not found"
        
        return fallback_result
    
    def _format_for_notion(self, value):
        """Helper function to convert complex data types to strings for Notion"""
        if value == "Not found" or value is None:
            return ""
        
        # Handle lists of dictionaries
        if isinstance(value, list):
            if not value:
                return ""
            
            # Check if it's a list of dicts (like brand_values or key_products_services)
            if all(isinstance(item, dict) for item in value):
                formatted_items = []
                for item in value:
                    if 'value_name' in item and 'description' in item:
                        # Brand values format
                        formatted_items.append(f"• {item['value_name']}: {item['description']}")
                    elif 'service_name' in item and 'description' in item:
                        # Services format
                        formatted_items.append(f"• {item['service_name']}: {item['description']}")
                    elif 'platform_name' in item and 'url' in item:
                        # Social media format
                        formatted_items.append(f"• {item['platform_name']}: {item['url']}")
                    else:
                        # Generic dict format
                        formatted_items.append(f"• {json.dumps(item)}")
                return "\n".join(formatted_items)
            else:
                # Simple list of strings
                return ", ".join(str(item) for item in value)
        
        # Handle dictionaries
        elif isinstance(value, dict):
            formatted_parts = []
            
            # Special handling for target_audience
            if 'primary' in value or 'secondary' in value:
                if value.get('primary'):
                    formatted_parts.append(f"Primary: {value['primary']}")
                if value.get('secondary'):
                    formatted_parts.append(f"Secondary: {value['secondary']}")
                if value.get('pain_points_addressed'):
                    pain_points = ", ".join(value['pain_points_addressed'])
                    formatted_parts.append(f"Pain Points: {pain_points}")
                return "\n".join(formatted_parts)
            
            # Special handling for company_size_indicators
            elif 'employee_count' in value or 'office_locations' in value:
                if value.get('employee_count'):
                    formatted_parts.append(f"Employees: {value['employee_count']}")
                if value.get('office_locations'):
                    locations = ", ".join(value['office_locations']) if isinstance(value['office_locations'], list) else value['office_locations']
                    formatted_parts.append(f"Locations: {locations}")
                if value.get('years_in_business'):
                    formatted_parts.append(f"Years in Business: {value['years_in_business']}")
                return "\n".join(formatted_parts)
            
            # Special handling for key_messaging_themes
            elif 'tagline_slogan' in value or 'recurring_phrases_keywords' in value:
                if value.get('tagline_slogan'):
                    formatted_parts.append(f"Tagline: {value['tagline_slogan']}")
                if value.get('recurring_phrases_keywords'):
                    keywords = ", ".join(value['recurring_phrases_keywords']) if isinstance(value['recurring_phrases_keywords'], list) else value['recurring_phrases_keywords']
                    formatted_parts.append(f"Keywords: {keywords}")
                if value.get('unique_terminology_or_brand_names'):
                    terms = ", ".join(value['unique_terminology_or_brand_names']) if isinstance(value['unique_terminology_or_brand_names'], list) else value['unique_terminology_or_brand_names']
                    formatted_parts.append(f"Unique Terms: {terms}")
                return "\n".join(formatted_parts)
            
            # Special handling for communication_style
            elif 'formality_level' in value or 'technical_level' in value:
                if value.get('formality_level'):
                    formatted_parts.append(f"Formality: {value['formality_level']}")
                if value.get('technical_level'):
                    formatted_parts.append(f"Technical Level: {value['technical_level']}")
                if value.get('overall_tone'):
                    tones = ", ".join(value['overall_tone']) if isinstance(value['overall_tone'], list) else value['overall_tone']
                    formatted_parts.append(f"Tone: {tones}")
                return "\n".join(formatted_parts)
            
            # Generic dict handling
            else:
                for k, v in value.items():
                    if isinstance(v, list):
                        v = ", ".join(str(item) for item in v)
                    formatted_parts.append(f"{k}: {v}")
                return "\n".join(formatted_parts)
        
        # Return as string for simple types
        else:
            return str(value)
    
    def _update_notion_client(self, analysis_result):
        """Step 5: Update Notion client with complete analysis"""
        if not self.client_id or not self.db_manager:
            self.logger.warning("Skipping Notion update - running in offline mode")
            return
        
        # Map analysis results to Notion AI Client Library fields with proper formatting
        notion_data = {
            # Basic Information
            "Industry": self._format_for_notion(analysis_result.get("industry", "Other")),
            "Company_Description": self._format_for_notion(analysis_result.get("company_description", "")),
            
            # Brand Identity  
            "Brand_Mission": self._format_for_notion(analysis_result.get("brand_mission", "")),
            "Brand_Values": self._format_for_notion(analysis_result.get("brand_values", [])),
            "Value_Proposition": self._format_for_notion(analysis_result.get("value_proposition", "")),
            "Brand_Personality": self._format_for_notion(analysis_result.get("brand_personality_traits", [])),
            
            # Products/Services
            "Product_Service_Description": self._format_for_notion(analysis_result.get("key_products_services", [])),
            
            # Target Audience
            "Target_Audience": self._format_for_notion(analysis_result.get("target_audience", {})),
            
            # Communication
            "Communication_Tone": self._format_for_notion(analysis_result.get("communication_style", {})),
            "Desired_Emotional_Impact": self._format_for_notion(
                analysis_result.get("communication_style", {}).get("overall_tone", [])
            ),
            
            # Contact Information
            "Contact_Email": self._format_for_notion(analysis_result.get("contact_email", "")),
            "Phone_Number": self._format_for_notion(analysis_result.get("phone_number", "")),
            "Location": self._format_for_notion(analysis_result.get("address", "")),
            
            # Social Media
            "LinkedIn_URL": self._format_for_notion(analysis_result.get("linkedin_url", "")),
            "Twitter_URL": self._format_for_notion(analysis_result.get("twitter_url", "")),
            "Facebook_URL": self._format_for_notion(analysis_result.get("facebook_url", "")),
            "Instagram_URL": self._format_for_notion(analysis_result.get("instagram_url", "")),
            "Other_Social_Media": self._format_for_notion(analysis_result.get("other_social_media", [])),
            
            # Company Details
            "Company_Size": self._format_for_notion(
                analysis_result.get("company_size_indicators", {}).get("employee_count", "")
            ),
            
            # Status tracking
            "Research_Status": "Website Data Extracted",
            "Last_Updated": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Add additional fields from analysis that might be useful
        if analysis_result.get("youtube_url"):
            notion_data["Other_Social_Media"] += f"\n• YouTube: {analysis_result['youtube_url']}"
        
        if analysis_result.get("key_messaging_themes"):
            # Store in Deep_Research_Workflow as JSON for later use
            notion_data["Deep_Research_Workflow"] = json.dumps({
                "website_extraction": {
                    "key_messaging_themes": analysis_result.get("key_messaging_themes", {}),
                    "awards_recognition": analysis_result.get("awards_recognition_affiliations", []),
                    "testimonial_themes": analysis_result.get("testimonial_themes_or_keywords", []),
                    "differentiators": analysis_result.get("key_differentiators_claimed", []),
                    "company_size_indicators": analysis_result.get("company_size_indicators", {}),
                    "extraction_date": datetime.now().isoformat()
                }
            })
        
        try:
            print(f"\n=== NOTION UPDATE DEBUG ===")
            print(f"Client ID: {self.client_id}")
            print(f"Analysis result keys: {list(analysis_result.keys())}")
            print(f"Notion data keys: {list(notion_data.keys())}")
            print(f"\n=== FORMATTED NOTION DATA ===")
            for key, value in notion_data.items():
                print(f"{key}: {value[:100]}..." if len(str(value)) > 100 else f"{key}: {value}")
            
            success = self.db_manager.update_client_profile(
                self.client_id,
                notion_data
            )
            
            print(f"\nUpdate result: {success}")
            
            if success:
                print("✓ Client profile updated in Notion with all extracted data")
                self.logger.log_operation_success("update_notion_client", client_id=self.client_id)
            else:
                print("✗ Failed to update client profile")
                self.logger.log_operation_failure("update_notion_client", "Update returned False")
                
        except Exception as e:
            print(f"✗ Error updating Notion: {str(e)}")
            import traceback
            traceback.print_exc()
            self.logger.log_operation_failure("update_notion_client", str(e))

def run_website_extractor():
    """
    MAIN EXECUTION FUNCTION
    For testing and standalone usage
    """
    logger = get_logger("website_extractor_cli")
    logger.info("Starting automated website extractor CLI")
    
    # Get user inputs
    client_name = input("Enter client name: ").strip()
    website_url = input("Enter website URL: ").strip()
    
    if not client_name or not website_url:
        logger.error("Both client name and website URL are required")
        return
    
    # Ensure URL has protocol
    if not website_url.startswith('http'):
        website_url = f"https://{website_url}"
    
    # Create context and run extraction
    context = WorkflowContext()
    context.set_input("client_name", client_name)
    context.set_input("website_url", website_url)
    
    extractor = AutomatedWebsiteExtractor()
    result = extractor.execute(context)
    
    if result.success:
        logger.log_operation_success("extraction_completed", 
                                   client_name=client_name,
                                   outputs=result.outputs)
    else:
        logger.log_operation_failure("extraction_failed", result.error)

if __name__ == "__main__":
    run_website_extractor()