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
    Main Streamlit UI function using the modular workflow system
    """
    import streamlit as st
    from frameworks import research_tools_framework
    
    st.title("Brand Builder")
    st.write("Build comprehensive brand profiles using modular workflow system")
    
    # Initialize database manager
    try:
        db_manager = research_tools_framework.NotionDatabaseManager()
    except Exception as e:
        st.error("🔧 **Configuration Required**")
        st.error("Please configure your Notion API credentials.")
        st.stop()
        return
    
    # Client selector sidebar
    client_page_id, selected_client, status = research_tools_framework.client_selector_sidebar(
        db_manager=db_manager, 
        allow_new_client=True
    )
    
    if not client_page_id:
        st.info("Please select a client from the sidebar or create a new one to get started.")
        return
    
    # Get client profile
    client_profile = db_manager.get_client_profile(client_page_id)
    
    st.subheader(f"Working on: {selected_client}")
    
    # Show two options: Individual steps or Full workflow
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 🔧 Individual Steps (for debugging)")
        
        if st.button("Run Step 1: Website Extractor"):
            website_url = st.text_input("Website URL:", value=client_profile.get("Website", ""))
            if website_url:
                step_tool = WebsiteExtractorTool()
                context = WorkflowContext({'client_name': selected_client, 'website_url': website_url})
                result = step_tool.execute(context)
                
                if result.success:
                    st.success("✅ Step 1 completed!")
                    st.json(result.data)
                    # Save to Notion
                    db_manager.update_client_profile(client_page_id, result.data)
                else:
                    st.error("❌ Step 1 failed!")
                    for error in result.errors:
                        st.error(error)
        
        if st.button("Run Step 2: Brand Analyzer"):
            step_tool = BrandAnalyzerTool()
            context_data = {'client_name': selected_client}
            context_data.update(client_profile)
            context = WorkflowContext(context_data)
            result = step_tool.execute(context)
            
            if result.success:
                st.success("✅ Step 2 completed!")
                st.json(result.data)
                # Save to Notion
                notion_data = {
                    "Current_Target_Audience": result.data.get("current_target_audience", ""),
                    "Ideal_Target_Audience": result.data.get("ideal_target_audience", ""),
                    "Brand_Values": ', '.join(result.data.get("brand_values", [])) if isinstance(result.data.get("brand_values"), list) else result.data.get("brand_values", ""),
                    "Brand_Mission": result.data.get("brand_mission", ""),
                }
                db_manager.update_client_profile(client_page_id, notion_data)
            else:
                st.error("❌ Step 2 failed!")
                for error in result.errors:
                    st.error(error)
    
    with col2:
        st.write("### 🚀 Full Workflow")
        
        if st.button("Run Complete Brand Builder Workflow"):
            # Create workflow context from client profile
            context_data = {'client_name': selected_client}
            context_data.update(client_profile)
            if client_profile.get("Website"):
                context_data['website_url'] = client_profile["Website"]
            
            context = WorkflowContext(context_data)
            workflow = BrandBuilderWorkflow()
            
            # Run the workflow
            with st.spinner("Running Brand Builder workflow..."):
                results = workflow.run_workflow(context, start_from=1, end_at=9)
            
            # Show results
            success_count = sum(1 for r in results if r.success)
            st.write(f"Completed {success_count}/{len(results)} steps")
            
            for i, result in enumerate(results, 1):
                if result.success:
                    st.success(f"✅ Step {i}: {result.step_name}")
                else:
                    st.error(f"❌ Step {i}: {result.step_name}")
                    for error in result.errors:
                        st.error(f"  {error}")
            
            if success_count > 0:
                st.success("Workflow completed! Data saved to Notion.")
                # Save final context to Notion
                notion_data = {}
                for key, value in context.data.items():
                    if isinstance(value, list):
                        notion_data[key] = ', '.join(value)
                    elif isinstance(value, str):
                        notion_data[key] = value
                
                db_manager.update_client_profile(client_page_id, notion_data)


# Export the main functions for backward compatibility
__all__ = [
    'extract_website_data',
    'analyze_brand_voice', 
    'comprehensive_client_analysis',
    'run_brand_builder',
    'BrandBuilderWorkflow',
    'WorkflowContext'
]