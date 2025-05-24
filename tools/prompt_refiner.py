import os
from prompts.meta_prompts.the_prompt_prompt import PROMPT as META_PROMPT
import google.generativeai as genai
import streamlit as st

def sidebar_info():
    with st.sidebar.expander("About this tool", expanded=True):
        st.write(
            "This Prompt Refiner helps you iteratively improve your prompts through multiple revisions until you get the perfect result."
        )
    with st.sidebar.expander("How to use"):
        st.write(
            "1. Enter your rough prompt\n"
            "2. Click 'Refine Prompt'\n"
            "3. Review the refined version\n"
            "4. Ask for revisions if needed\n"
            "5. Repeat until perfect!"
        )

def refine_prompt(rough_prompt, meta_prompt):
    """Initial prompt refinement"""
    genai.configure(api_key=st.secrets["google"]["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
    response = model.generate_content(f"{meta_prompt}\n\n[ {rough_prompt} ]")
    return response.text.strip()

# Custom revision prompt - much more efficient
REVISION_PROMPT = """
You are an expert prompt engineer specializing in prompt revisions.

Your task: Modify the current prompt based on the user's specific feedback, keeping what works well and improving only what they've requested.

CURRENT PROMPT:
{current_prompt}

USER'S REVISION REQUEST:
{revision_request}

INSTRUCTIONS:
- Keep the core structure and good elements
- Focus only on the specific changes requested
- Don't over-engineer - make targeted improvements
- Maintain the original intent while incorporating the feedback
- Return ONLY the revised prompt, no explanation

REVISED PROMPT:
"""

def revise_prompt(current_prompt, revision_request):
    """Revise an existing prompt based on user feedback"""
    prompt = REVISION_PROMPT.format(
        current_prompt=current_prompt,
        revision_request=revision_request
    )
    
    genai.configure(api_key=st.secrets["google"]["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")  # Use faster model for revisions
    response = model.generate_content(prompt)
    return response.text.strip()

# Remove unused functions
def explain_prompt(refined_prompt, explainer_prompt):
    """Deprecated - no longer used"""
    pass

# Keep for framework compatibility
META_PROMPT = META_PROMPT
EXPLAINER_PROMPT = None  # Not used anymore