"""
Brand Builder - Modular Architecture

This file serves as the main entry point for the Brand Builder workflow.
Each step is implemented as an independent tool in the brand_builder/ directory.

Steps:
1. Website Extractor - Extract company data from website
2. Brand Analyzer - Analyze brand voice and strategy  
3. Content Collector - Identify content samples across channels
4. Voice Auditor - Audit voice consistency
5. Audience Definer - Define target audience personas
6. Voice Traits Builder - Build actionable voice traits
7. Gap Analyzer - Analyze competitive gaps
8. Content Rewriter - Transform content samples
9. Guidelines Finalizer - Generate final brand guidelines

Each step can be run independently for testing and debugging.
"""

# Import the modular workflow system
from tools.brand_builder import BrandBuilderWorkflow, WorkflowContext

# Import individual step tools for backward compatibility
from tools.brand_builder.step_01_website_extractor import WebsiteExtractorTool
from tools.brand_builder.step_02_brand_analyzer import BrandAnalyzerTool


def extract_website_data(client_name, website_url):
    """
    Step 1: Extract website data (backward compatibility function)
    """
    context = WorkflowContext({
        'client_name': client_name,
        'website_url': website_url
    })
    
    step = WebsiteExtractorTool()
    result = step.execute(context)
    
    return result.success, result.data, result.errors[0] if result.errors else None


def analyze_brand_voice(client_name, website_data, form_data=None):
    """
    Step 2: Analyze brand voice (backward compatibility function)
    """
    context_data = {'client_name': client_name}
    context_data.update(website_data or {})
    context_data.update(form_data or {})
    
    context = WorkflowContext(context_data)
    
    step = BrandAnalyzerTool()
    result = step.execute(context)
    
    return result.success, result.data, result.errors[0] if result.errors else None


def comprehensive_client_analysis(client_name, industry, website_url=None, form_data=None, optimize_content=True):
    """
    Two-step analysis process using modular system
    """
    context_data = {
        'client_name': client_name,
        'industry': industry
    }
    
    if website_url:
        context_data['website_url'] = website_url
    
    if form_data:
        context_data.update(form_data)
    
    context = WorkflowContext(context_data)
    workflow = BrandBuilderWorkflow()
    
    # Run steps 1-2
    if website_url:
        results = workflow.run_workflow(context, start_from=1, end_at=2)
    else:
        results = workflow.run_workflow(context, start_from=2, end_at=2)
    
    if results and results[-1].success:
        return True, context.data, None
    else:
        errors = [r.errors[0] for r in results if r.errors]
        return False, {}, '; '.join(errors) if errors else "Unknown error"


def run_brand_builder():
    """
    Main Streamlit UI function - imports from the monolithic backup for now
    TODO: Refactor this UI to use the modular system
    """
    # Import the UI from the backup file temporarily
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    # Import the massive UI function from backup
    from brand_builder_monolith_backup import run_brand_builder as run_ui
    return run_ui()


# Export the main functions for backward compatibility
__all__ = [
    'extract_website_data',
    'analyze_brand_voice', 
    'comprehensive_client_analysis',
    'run_brand_builder',
    'BrandBuilderWorkflow',
    'WorkflowContext'
]