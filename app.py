import streamlit as st
from frameworks.universal_framework import universal_ui, home_button
from frameworks.refiner_framework import run_refiner
import tools.prompt_refiner as prompt_refiner
import tools.coder_helper as coder_helper
from tools import social_copy_tool

# Home/tool selection logic (as you have it)
if "tool" not in st.session_state:
    st.session_state.tool = "home"

universal_ui()  # universal sidebar, can be empty for now
home_button()   # universal home button

if st.session_state.tool == "home":
    if st.button("Prompt Refiner"):
        st.session_state.tool = "Prompt Refiner"
        st.rerun()
    if st.button("Coder Helper"):
        st.session_state.tool = "Coder Helper"
        st.rerun()
    if st.button("Copy Generator"):
        st.session_state.tool = "Copy Generator"
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