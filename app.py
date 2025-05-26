import streamlit as st
from frameworks.universal_framework import universal_ui, home_button
from frameworks.refiner_framework import run_refiner
import tools.prompt_refiner as prompt_refiner
import tools.coder_helper as coder_helper
from tools import social_copy_tool

def run_brand_builder():
    """Streamlit UI for Brand Builder"""
    st.title("Brand Builder")
    st.subheader("Automated 9-Step Brand Research Pipeline")
    
    st.write("Enter the client name and website URL to begin the automated brand analysis.")
    
    # Import the actual brand builder components
    from tools.brand_builder.step_01_website_extractor import AutomatedWebsiteExtractor, WorkflowContext
    
    # Input form
    with st.form("website_extractor"):
        client_name = st.text_input("Client Name", placeholder="Enter client name")
        website_url = st.text_input("Website URL", placeholder="https://example.com")
        
        submitted = st.form_submit_button("🚀 Start Brand Analysis")
        
        if submitted:
            if not client_name or not website_url:
                st.error("Please provide both client name and website URL")
            else:
                # Ensure URL has protocol
                if not website_url.startswith('http'):
                    website_url = f"https://{website_url}"
                
                # Create context and run extraction
                context = WorkflowContext()
                context.set_input("client_name", client_name)
                context.set_input("website_url", website_url)
                
                # Run the extraction
                with st.spinner("🔍 Analyzing website and building brand profile..."):
                    extractor = AutomatedWebsiteExtractor()
                    result = extractor.execute(context)
                
                # Show results
                if result.success:
                    st.success("✅ Brand analysis completed!")
                    
                    # Display results
                    st.subheader("📊 Analysis Results")
                    
                    if result.data.get("analysis"):
                        st.write("### Brand Analysis")
                        st.json(result.data["analysis"])
                    
                    if result.data.get("content_file"):
                        st.write(f"📁 **Content File:** `{result.data['content_file']}`")
                    
                    if result.data.get("sitemap_file"):
                        st.write(f"🗺️ **Sitemap File:** `{result.data['sitemap_file']}`")
                    
                    if result.data.get("client_id"):
                        st.write(f"🗄️ **Notion Client ID:** `{result.data['client_id']}`")
                    
                    st.balloons()
                else:
                    st.error("❌ Analysis failed:")
                    for error in result.errors:
                        st.error(f"  • {error}")

# Initialize session state
if "tool" not in st.session_state:
    st.session_state.tool = "home"

# Let universal_ui handle client selection
universal_ui()
home_button()

if st.session_state.tool == "home":
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Prompt Refiner"):
            st.session_state.tool = "Prompt Refiner"
            st.rerun()
        if st.button("Coder Helper"):
            st.session_state.tool = "Coder Helper"
            st.rerun()
    with col2:
        if st.button("Copy Generator"):
            st.session_state.tool = "Copy Generator"
            st.rerun()
        # Add the Brand Builder button
        if st.button("Brand Builder"):
            st.session_state.tool = "Brand Builder"
            st.rerun()

if st.session_state.tool == "Prompt Refiner":
    run_refiner(
        tool_name="Prompt Refiner",
        refine_func=prompt_refiner.refine_prompt,
        meta_prompt=prompt_refiner.META_PROMPT,
        sidebar_info=prompt_refiner.sidebar_info,
    )

if st.session_state.tool == "Coder Helper":
    run_refiner(
        tool_name="Coder Helper",
        refine_func=coder_helper.refine_prompt,
        meta_prompt=coder_helper.META_PROMPT,
        sidebar_info=coder_helper.sidebar_info,
    )

if st.session_state.tool == "Copy Generator":
    social_copy_tool.run()

# Add the Brand Builder tool
if st.session_state.tool == "Brand Builder":
    run_brand_builder()