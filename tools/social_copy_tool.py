# tools/social_copy_tool.py
import streamlit as st
import os
import importlib
import google.generativeai as genai
import openai

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
            model = genai.GenerativeModel('gemini-pro')
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
    from frameworks.copy_generator_framework import run_copy_generator
    
    # Load all available prompts
    prompts = load_all_prompts()
    platform_names = list(prompts.keys())
    
    # Use your framework, but dynamically pass platform names
    uploaded_file, notes = run_copy_generator(
        tool_name="Copy Generator",
        right_box_labels=platform_names,
        sidebar_info=lambda: st.sidebar.info("Upload notes or scripts to generate platform-specific copy.")
    )
    
    # Show selected client info
    selected_client = st.session_state.get("selected_client")
    if selected_client:
        st.success(f"🎯 Selected Client: **{selected_client['name']}**")
    
    # Generate button
    if st.button("🚀 Generate Copy", key="generate_all_copy"):
        if notes.strip():
            with st.spinner("Generating copy for all platforms..."):
                # Generate for each platform and update the text areas
                for platform_name in platform_names:
                    if platform_name in prompts:
                        generated_copy = generate_copy_for_platform(
                            prompts[platform_name], 
                            notes, 
                            selected_client
                        )
                        # Update the session state so the text areas show the generated content
                        st.session_state[f"copy_gen_{platform_name}"] = generated_copy
            
            st.success("✅ Copy generated for all platforms!")
            st.rerun()  # Refresh to show the generated content
        else:
            st.error("Please enter some notes first!")