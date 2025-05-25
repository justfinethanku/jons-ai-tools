"""
Extract Sitemap Prompts
Prompts for discovering and extracting comprehensive website sitemaps
"""

def get_page_discovery_prompt(website_url):
    """
    Prompt for AI-assisted page discovery for comprehensive site mapping
    """
    return f"""You are a web crawler assistant. Given this website URL: {website_url}

Based on the domain and typical website structures, suggest 15-20 likely pages that would exist on this website.

Include common pages like:
- About us, Team, Company
- Products, Services, Solutions
- Contact, Support, FAQ
- Privacy Policy, Terms of Service
- Careers, Jobs
- Resources, Documentation

EXCLUDE these types of pages:
- Blog posts, News articles, individual blog entries
- Date-based URLs (e.g., /2024/01/blog-post)
- Individual article or post URLs

Focus on core business pages that contain stable company information, not dynamic content.

Format as a simple list of full URLs, one per line. Only suggest URLs that are likely to exist.

Example format:
{website_url}/about
{website_url}/contact
{website_url}/services

URL LIST:"""