import os
from prompts.meta_prompts.code_prompt import PROMPT as META_PROMPT
from prompts.meta_prompts.explainer import PROMPT as EXPLAINER_PROMPT
import google.generativeai as genai
import streamlit as st

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
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"{meta_prompt}\n\n[ {rough_prompt} ]")
    return response.text.strip()

def explain_prompt(refined_prompt, explainer_prompt):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(explainer_prompt.replace("[Insert prompt to be analyzed here]", refined_prompt))
    return response.text.strip()

# (No run() function here—let the framework handle that)
META_PROMPT = META_PROMPT
EXPLAINER_PROMPT = EXPLAINER_PROMPT