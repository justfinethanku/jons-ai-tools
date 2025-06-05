import os
from prompts.meta_prompts.the_prompt_prompt import PROMPT as META_PROMPT
from frameworks.universal_framework import call_gemini_api
from frameworks.tool_config import get_tool_config
import streamlit as st

# Load tool configuration
tool_config = get_tool_config("prompt_refiner")

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
    """Initial prompt refinement with centralized configuration"""
    # Use centralized configuration instead of hardcoded values
    refiner_rules = {
        'MODEL_PREFERENCE': tool_config.get('MODEL_PREFERENCE', 'gemini-2.5-pro-preview-05-06'),
        'TEMPERATURE': tool_config.get('TEMPERATURE', 0.3),
        'MAX_RETRIES': tool_config.get('MAX_RETRIES', 3),
        'TOP_P': tool_config.get('TOP_P', 0.9),
        'TOP_K': tool_config.get('TOP_K', 40),
        'MAX_OUTPUT_TOKENS': tool_config.get('MAX_OUTPUT_TOKENS', 8192)
    }
    
    final_prompt = f"{meta_prompt}\n\n[ {rough_prompt} ]"
    response = call_gemini_api(final_prompt, context_rules=refiner_rules)
    return response.strip() if response and not response.startswith('Error:') else response

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
    """Revise an existing prompt based on user feedback with centralized configuration"""
    # Use centralized configuration with revision-specific overrides
    revision_rules = {
        'MODEL_PREFERENCE': tool_config.get('MODEL_PREFERENCE', 'gemini-2.5-pro-preview-05-06'),
        'TEMPERATURE': tool_config.get('REVISION_TEMPERATURE', 0.5),
        'MAX_RETRIES': tool_config.get('REVISION_MAX_RETRIES', 2),
        'TOP_P': tool_config.get('REVISION_TOP_P', 0.95),
        'TOP_K': tool_config.get('REVISION_TOP_K', 50),
        'MAX_OUTPUT_TOKENS': tool_config.get('MAX_OUTPUT_TOKENS', 8192)
    }
    
    prompt = REVISION_PROMPT.format(
        current_prompt=current_prompt,
        revision_request=revision_request
    )
    
    response = call_gemini_api(prompt, context_rules=revision_rules)
    return response.strip() if response and not response.startswith('Error:') else response

# Remove unused functions
def explain_prompt(refined_prompt, explainer_prompt):
    """Deprecated - no longer used"""
    pass

# Keep for framework compatibility
META_PROMPT = META_PROMPT
EXPLAINER_PROMPT = None  # Not used anymore