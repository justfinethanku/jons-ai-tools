from prompts.meta_prompts.code_prompt import PROMPT as META_PROMPT
from prompts.meta_prompts.explainer import PROMPT as EXPLAINER_PROMPT
from frameworks.universal_framework import call_gemini_api
from frameworks.tool_config import get_tool_config
import streamlit as st

# Load tool configuration
tool_config = get_tool_config("coder_helper")

def sidebar_info():
    with st.sidebar.expander("About this tool", expanded=True):
        st.write(
            "This Prompt Refiner helps you improve your initial prompt by making it clearer, more specific, or better structured."
        )
    with st.sidebar.expander("How to use"):
        st.write(
            "- Enter your rough prompt.\n"
            "- Click 'Refine Prompt'.\n"
            "- Optionally, click 'Explain this' for an explanation."
        )

def refine_prompt(rough_prompt, meta_prompt):
    """Code-focused prompt refinement with centralized configuration"""
    # Use centralized configuration with code-specific optimizations
    coder_rules = {
        'MODEL_PREFERENCE': tool_config.get('MODEL_PREFERENCE', 'gemini-2.5-pro-preview-05-06'),
        'TEMPERATURE': tool_config.get('TEMPERATURE', 0.2),
        'MAX_RETRIES': tool_config.get('MAX_RETRIES', 3),
        'TOP_P': tool_config.get('TOP_P', 0.85),
        'TOP_K': tool_config.get('TOP_K', 30)
    }
    
    final_prompt = f"{meta_prompt}\n\n[ {rough_prompt} ]"
    response = call_gemini_api(final_prompt, context_rules=coder_rules)
    return response.strip() if response and not response.startswith('Error:') else response

def explain_prompt(refined_prompt, explainer_prompt):
    """Explain prompts with centralized configuration"""
    # Use centralized configuration for explanation generation
    explainer_rules = {
        'MODEL_PREFERENCE': tool_config.get('MODEL_PREFERENCE', 'gemini-2.5-pro-preview-05-06'),
        'TEMPERATURE': tool_config.get('EXPLAINER_TEMPERATURE', 0.4),
        'MAX_RETRIES': tool_config.get('EXPLAINER_MAX_RETRIES', 2),
        'TOP_P': tool_config.get('EXPLAINER_TOP_P', 0.9),
        'TOP_K': tool_config.get('EXPLAINER_TOP_K', 40)
    }
    
    final_prompt = explainer_prompt.replace("[Insert prompt to be analyzed here]", refined_prompt)
    response = call_gemini_api(final_prompt, context_rules=explainer_rules)
    return response.strip() if response and not response.startswith('Error:') else response

# (No run() function here—let the framework handle that)
META_PROMPT = META_PROMPT
EXPLAINER_PROMPT = EXPLAINER_PROMPT