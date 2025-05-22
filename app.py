import streamlit as st
from frameworks.universal_framework import universal_ui, home_button
from frameworks.refiner_framework import run_refiner
import tools.prompt_refiner as prompt_refiner
import tools.coder_helper as coder_helper
from tools import social_copy_tool
from tools import context_gatherer  # Add this import

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
        # Add the Context Gatherer button
        if st.button("Context Gatherer"):
            st.session_state.tool = "Context Gatherer"
            st.rerun()

if st.session_state.tool == "Prompt Refiner":
    run_refiner(
        tool_name="Prompt Refiner",
        refine_func=prompt_refiner.refine_prompt,
        explain_func=prompt_refiner.explain_prompt,
        meta_prompt=prompt_refiner.META_PROMPT,
        explainer_prompt=prompt_refiner.EXPLAINER_PROMPT,
        sidebar_info=prompt_refiner.sidebar_info,
    )

if st.session_state.tool == "Coder Helper":
    run_refiner(
        tool_name="Coder Helper",
        refine_func=coder_helper.refine_prompt,
        explain_func=coder_helper.explain_prompt,
        meta_prompt=coder_helper.META_PROMPT,
        explainer_prompt=coder_helper.EXPLAINER_PROMPT,
        sidebar_info=coder_helper.sidebar_info,
    )

if st.session_state.tool == "Copy Generator":
    social_copy_tool.run()

# Add the Context Gatherer tool
if st.session_state.tool == "Context Gatherer":
    context_gatherer.run_context_gatherer()