import streamlit as st
import os
import importlib
import google.generativeai as genai
import openai
from frameworks.universal_framework import outputs_to_txt_bytes

def load_all_prompts():
    """Dynamically load all prompts from social_prompts folder"""
    prompts = {}
    base_path = "prompts.copy_prompts.social_prompts"
    
    # Get all .py files in the social_prompts directory
    social_prompts_dir = "prompts/copy_prompts/social_prompts"
    
    try:
        for filename in os.listdir(social_prompts_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                platform_name = filename[:-3]  # Remove .py extension
                try:
                    module_path = f"{base_path}.{platform_name}"
                    module = importlib.import_module(module_path)
                    if hasattr(module, 'PROMPT'):
                        # Format platform name nicely (facebook_copy -> Facebook)
                        display_name = platform_name.replace('_copy', '').replace('_', ' ').title()
                        prompts[display_name] = module.PROMPT
                except ImportError as e:
                    st.error(f"Could not load {platform_name}: {e}")
    except FileNotFoundError:
        st.error(f"Directory not found: {social_prompts_dir}")
    
    return prompts

def generate_copy_for_platform(prompt_template, user_input, client_data=None):
    """Generate copy using AI"""
    # Replace the placeholder in the prompt
    final_prompt = prompt_template.replace("{USER_INPUT}", user_input)
    
    # Add client context if available
    if client_data:
        client_context = f"""
CLIENT CONTEXT:
- Client: {client_data.get('name', 'Unknown')}
- Brand Voice: {client_data.get('brand_voice', 'Professional')}
- Tone: {client_data.get('tone', 'Neutral')}
- Industry: {client_data.get('industry', 'General')}

IMPORTANT: Follow the client's brand voice and tone exactly.

"""
        final_prompt = client_context + final_prompt
    
    try:
        # Try Gemini first
        if st.secrets.get("GEMINI_API_KEY"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(final_prompt) 
            return response.text
        
        # Fallback to OpenAI
        elif st.secrets.get("OPENAI_API_KEY"):
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert social media copywriter."},
                    {"role": "user", "content": final_prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        
        else:
            return "Error: No AI API key configured"
            
    except Exception as e:
        return f"Error: {str(e)}"

def run():
    """Main function called by app.py"""
    st.header("Copy Generator")
    
    # Show selected client info
    selected_client = st.session_state.get("selected_client")
    if selected_client:
        st.success(f"🎯 Selected Client: **{selected_client['name']}**")
    
    # Input section
    col_left, col_right = st.columns([1, 3])
    
    with col_left:
        st.sidebar.info("Upload notes or scripts to generate platform-specific copy.")
        uploaded_file = st.file_uploader("Drag & Drop a file here", type=None)
        notes = st.text_area("Notes", height=200)
        
        # Generate button
        generate_clicked = st.button("🚀 Generate Copy", key="generate_copy_button")
    
    with col_right:
        st.write("") # Empty space initially
    
    # Generate copy when button is clicked
    if generate_clicked:
        if notes.strip():
            # Load prompts and generate
            prompts = load_all_prompts()
            
            if not prompts:
                st.error("No prompts found! Check your prompts/copy_prompts/social_prompts folder.")
                return
            
            # Store generated content in session state
            if "generated_outputs" not in st.session_state:
                st.session_state["generated_outputs"] = {}
            
            with st.spinner("Generating copy for all platforms..."):
                # Generate for each platform
                for platform_name, prompt_template in prompts.items():
                    generated_copy = generate_copy_for_platform(
                        prompt_template, 
                        notes, 
                        selected_client
                    )
                    st.session_state["generated_outputs"][platform_name] = generated_copy
            
            st.success("✅ Copy generated for all platforms!")
            st.rerun()  # Refresh to show results
        else:
            st.error("Please enter some notes first!")
    
    # Show generated outputs if they exist
    if "generated_outputs" in st.session_state and st.session_state["generated_outputs"]:
        st.markdown("---")
        st.subheader("Generated Copy")
        
        # Show outputs in a grid
        cols = st.columns(2)
        outputs = st.session_state["generated_outputs"]
        
        for i, (platform_name, content) in enumerate(outputs.items()):
            with cols[i % 2]:
                st.text_area(
                    f"{platform_name}",
                    value=content,
                    height=150,
                    key=f"output_{platform_name}_{id(content)}"  # Unique key to avoid conflicts
                )
        
        # Download button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            file_bytes = outputs_to_txt_bytes(outputs)
            from datetime import datetime
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"copy_generator_{now}.txt"
            
            st.download_button(
                label="💾 Download All Results",
                data=file_bytes,
                file_name=file_name,
                mime="text/plain",
                key="download_results"
            )
        
        # Clear results button
        with col3:
            if st.button("🗑️ Clear Results", key="clear_results"):
                del st.session_state["generated_outputs"]
                st.rerun()