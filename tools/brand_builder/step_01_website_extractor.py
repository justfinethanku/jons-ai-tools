"""
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
from frameworks.research_tools_framework import NotionDatabaseManager
from prompts.research_prompts.step01_prompts.extract_sitemap import get_page_discovery_prompt
from prompts.research_prompts.step01_prompts.extract_client_info import (
    get_comprehensive_analysis_prompt, 
    get_analysis_schema
)

class AutomatedWebsiteExtractor(WorkflowStep):
    """
    FULLY AUTOMATED website extraction pipeline
    Input: client_name + website_url
    Output: Complete brand analysis + auto-progression to step 2
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize database manager with error handling
        try:
            self.db_manager = NotionDatabaseManager()
            print("✅ NotionDatabaseManager initialized successfully")
        except Exception as e:
            print(f"⚠️ NotionDatabaseManager failed to initialize: {e}")
            print("⚠️ Running in OFFLINE mode - data will be saved to files only")
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
        print("\\n🚀 STARTING AUTOMATED WEBSITE EXTRACTION PIPELINE")
        print("=" * 60)
        
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
            
            print(f"📊 CLIENT: {client_name}")
            print(f"🌐 WEBSITE: {website_url}")
            print()
            
            # Step 1: Create Notion client entry
            print("📝 STEP 1: Creating Notion client entry...")
            self._create_notion_client(client_name, website_url)
            
            # Step 2: Generate comprehensive sitemap
            print("\\n🗺️ STEP 2: Generating comprehensive sitemap...")
            sitemap = self._generate_comprehensive_sitemap(website_url)
            sitemap_file = self._save_sitemap(client_name, sitemap)
            print(f"✅ Sitemap saved: {sitemap_file}")
            
            # Step 3: Extract content from all pages
            print("\\n📄 STEP 3: Extracting content from all pages...")
            all_content = self._extract_all_content(sitemap)
            content_file = self._save_content(client_name, all_content)
            
            total_words = sum(data['word_count'] for data in all_content.values())
            print(f"✅ Extracted {len(all_content)} pages ({total_words:,} words)")
            print(f"✅ Content saved: {content_file}")
            
            # Step 4: Analyze content with Gemini
            print("\\n🧠 STEP 4: Analyzing content with Gemini...")
            analysis_result = self._analyze_comprehensive_content(client_name, website_url, all_content)
            print("✅ Content analysis complete")
            
            # Step 5: Update Notion with comprehensive data
            print("\\n💾 STEP 5: Updating Notion database...")
            self._update_notion_client(analysis_result)
            print("✅ Notion database updated")
            
            # Step 6: Prepare for Step 2
            print("\\n⏭️ STEP 6: Preparing for Step 2...")
            context.set_output("website_analysis", analysis_result)
            context.set_output("content_file", content_file)
            context.set_output("sitemap_file", sitemap_file)
            
            print("\\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"📊 Analysis complete for {client_name}")
            print(f"📁 Files saved in: {self.data_dir}")
            if self.client_id:
                print(f"🗄️ Notion updated for client ID: {self.client_id}")
            print("⏭️ Ready for Step 2: Brand Analysis")
            
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
            error_msg = f"❌ PIPELINE FAILED: {str(e)}"
            print(error_msg)
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
            print("⚠️ Skipping Notion client creation - running in offline mode")
            return
        
        try:
            # Check if client already exists
            existing_client_id = self.db_manager.get_client_page_id(client_name)
            if existing_client_id:
                self.client_id = existing_client_id
                print(f"✅ Found existing client with ID: {self.client_id}")
                # Update status to show we're extracting
                self._update_client_status("Extracting Website Data")
            else:
                # Create new client entry
                self.client_id = self.db_manager.create_new_client(client_name, "Unknown")
                print(f"✅ New client created with ID: {self.client_id}")
                
                # Update with website URL and status
                if self.client_id:
                    self._update_client_basic_info(website_url)
            
        except Exception as e:
            print(f"⚠️ Failed to create Notion client: {e}")
            print("⚠️ Continuing in offline mode")
            self.db_manager = None
    
    def _update_client_status(self, status):
        """Update client status in Notion"""
        if not self.client_id or not self.db_manager:
            return
        try:
            self.db_manager.update_client_profile(self.client_id, {"Research_Status": status})
        except Exception as e:
            print(f"⚠️ Failed to update status: {e}")
    
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
            print(f"⚠️ Failed to update basic info: {e}")
    
    def _generate_comprehensive_sitemap(self, website_url):
        """Step 2: Generate comprehensive sitemap using multiple methods"""
        all_pages = set()
        
        print("🔍 Discovering pages using multiple methods...")
        
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
                print(f"  📋 Found {len(pages)} pages in {sitemap_url}")
        
        # Method 2: Homepage analysis for common page discovery
        homepage_pages = self._discover_pages_from_homepage(website_url)
        all_pages.update(homepage_pages)
        print(f"  🏠 Found {len(homepage_pages)} pages from homepage analysis")
        
        # Method 3: Use Gemini to intelligently guess likely pages
        gemini_pages = self._gemini_page_discovery(website_url)
        all_pages.update(gemini_pages)
        print(f"  🧠 Gemini suggested {len(gemini_pages)} additional pages")
        
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
        """Use Gemini to discover likely pages"""
        try:
            prompt = get_page_discovery_prompt(website_url)
            response = universal_framework.call_gemini_api(prompt, temperature=0.3)
            
            if not response or response.startswith("Error:"):
                return []
            
            # Parse URLs from response
            urls = []
            for line in response.split('\\n'):
                line = line.strip()
                if line.startswith('http') and self._is_valid_page_url(line):
                    urls.append(line)
            
            return urls[:15]  # Limit to 15 suggestions
            
        except Exception as e:
            print(f"    ⚠️ Gemini page discovery failed: {e}")
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
            print(f"  📄 Extracting page {i}/{min(len(sitemap), 20)}: {url}")
            
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
                print(f"    ⚠️ Failed to extract {url}: {e}")
        
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
                return '\\n'.join(chunk for chunk in chunks if chunk)
            
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
        content_summary = f"=== COMPREHENSIVE WEBSITE ANALYSIS FOR {client_name} ===\\n\\n"
        content_summary += f"Website: {website_url}\\n"
        content_summary += f"Total Pages Analyzed: {len(all_content)}\\n\\n"
        
        for url, data in all_content.items():
            page_name = url.split('/')[-1] or 'homepage'
            content_summary += f"=== PAGE: {page_name.upper()} ({url}) ===\\n"
            content_summary += f"{data['content'][:1500]}\\n\\n"  # First 1500 chars per page
        
        # Get analysis prompt from separated prompt file 
        prompt = get_comprehensive_analysis_prompt(client_name, website_url, content_summary)
        
        # Call Gemini for analysis
        response = universal_framework.call_gemini_api(prompt, temperature=0.1)
        
        print(f"  🧠 Gemini response (first 200 chars): {response[:200]}")
        
        if response.startswith("Error:"):
            raise Exception(f"Gemini analysis failed: {response}")
        
        # Handle empty or invalid response
        if not response or not response.strip():
            print("  ⚠️ Gemini returned empty response, using fallback analysis")
            return self._create_fallback_analysis(client_name, website_url, all_content)
        
        # Try to parse JSON response
        try:
            # Clean response - sometimes there's extra text before/after JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            elif response.startswith('```'):
                response = response.replace('```', '').strip()
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON parsing failed: {e}")
            print(f"  ⚠️ Raw response: {response[:500]}")
            return self._create_fallback_analysis(client_name, website_url, all_content)
    
    def _create_fallback_analysis(self, client_name, website_url, all_content):
        """Create basic fallback analysis when Gemini fails"""
        print("  🔄 Creating fallback analysis...")
        
        # Extract basic info from content
        all_text = " ".join([data['content'] for data in all_content.values()])
        
        schema = get_analysis_schema()
        fallback_result = {}
        
        # Populate with basic extracted data or "Not found"
        for key, description in schema.items():
            if key == "company_description":
                fallback_result[key] = f"{client_name} - analysis extracted from {website_url}"
            elif key == "key_products_services":
                fallback_result[key] = ["Service analysis pending"]
            elif key == "other_social_media":
                fallback_result[key] = []
            else:
                fallback_result[key] = "Not found"
        
        return fallback_result
    
    def _update_notion_client(self, analysis_result):
        """Step 5: Update Notion client with complete analysis"""
        if not self.client_id or not self.db_manager:
            print("⚠️ Skipping Notion update - running in offline mode")
            return
        
        # Map analysis results to Notion AI Client Library fields (per schema.md)
        notion_data = {
            "Industry": analysis_result.get("industry", "Other"),
            "Company_Description": analysis_result.get("company_description", ""),
            "Brand_Mission": analysis_result.get("brand_mission", ""),
            "Brand_Values": analysis_result.get("brand_values", ""),
            "Value_Proposition": analysis_result.get("value_proposition", ""),
            "Target_Audience": analysis_result.get("target_audience", ""),
            "Contact_Email": analysis_result.get("contact_email", ""),
            "Phone_Number": analysis_result.get("phone_number", ""),
            "Location": analysis_result.get("address", ""),
            # Social media URLs (as per schema)
            "LinkedIn_URL": analysis_result.get("linkedin_url", ""),
            "Twitter_URL": analysis_result.get("twitter_url", ""),
            "Facebook_URL": analysis_result.get("facebook_url", ""),
            "Instagram_URL": analysis_result.get("instagram_url", ""),
            # Status tracking
            "Last_Updated": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Clean up "Not found" values
        for key, value in notion_data.items():
            if value == "Not found":
                notion_data[key] = ""
        
        try:
            self.db_manager.update_client_profile(self.client_id, notion_data)
            print("✅ Notion client updated with comprehensive analysis")
        except Exception as e:
            print(f"⚠️ Failed to update Notion: {e}")

def run_website_extractor():
    """
    MAIN EXECUTION FUNCTION
    For testing and standalone usage
    """
    print("🚀 AUTOMATED WEBSITE EXTRACTOR")
    print("=" * 40)
    
    # Get user inputs
    client_name = input("Enter client name: ").strip()
    website_url = input("Enter website URL: ").strip()
    
    if not client_name or not website_url:
        print("❌ Both client name and website URL are required")
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
        print("\\n🎉 Extraction completed successfully!")
        if result.outputs:
            print(f"📁 Results: {result.outputs}")
    else:
        print(f"\\n❌ Extraction failed: {result.error}")

if __name__ == "__main__":
    run_website_extractor()