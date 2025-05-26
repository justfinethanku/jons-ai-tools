def get_page_discovery_prompt(website_url):
    """
    Optimized prompt for AI-assisted page discovery for comprehensive site mapping,
    designed for llm, with few-shot examples.
    """
    return f"""
You are an AI assistant.

Task:
Find the sitemap for this website: {website_url}

1. Extract a list of all important URLs from the sitemap.
2. Do NOT include any URL that contains the word "blog" (case-insensitive).
3. Return the final list as a JSON array of strings.
   Example: ["https://example.com/about", "https://example.com/contact"]

Return ONLY the list—no explanations or extra text.
"""