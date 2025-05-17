import streamlit as st

# Reduce sidebar width for the refiner framework
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        min-width: 180px !important;
        max-width: 180px !important;
        width: 180px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def run_refiner(
    tool_name,
    refine_func,
    explain_func,
    meta_prompt,
    explainer_prompt,
    sidebar_info,
    rough_prompt_label="Rough Prompt",
    show_explain=True,
    output_height=160,
):
    # Optional: Tool-specific sidebar/help
    sidebar_info()

    st.header(tool_name)
    rough_prompt = st.text_area(rough_prompt_label, height=120)

    refine_clicked = st.button("Refine Prompt", key="refine_inside_tool")

    if "refined" not in st.session_state:
        st.session_state["refined"] = ""
    if "explanation" not in st.session_state:
        st.session_state["explanation"] = ""

    if refine_clicked:
        refined = refine_func(rough_prompt, meta_prompt)
        st.session_state["refined"] = refined
        st.session_state["explanation"] = ""  # Clear explanation after new refine

    if st.session_state["refined"]:
        st.markdown("#### Refined Prompt")
        # Dynamically set height: minimum 8 lines, maximum 30 lines
        refined_text = st.session_state["refined"]
        line_count = max(8, min(30, refined_text.count('\n') + 2))  # +2 for short/single-line prompts
        st.text_area(
            "",
            value=refined_text,
            height=round(line_count * 20),  # ~20px per line is Streamlit's default
            key="refined_prompt_output",
            disabled=True,
        )

        explain_clicked = st.button("Explain this", key="explain_refined_prompt")

        if explain_clicked:
            explanation = explain_func(st.session_state["refined"], explainer_prompt)
            st.session_state["explanation"] = explanation

        st.text_area(
            "Explanation",
            value=st.session_state["explanation"],
            height=120,
            key="refined_explanation",
            disabled=True,
        )
    else:
        st.markdown("#### Refined Prompt")
        st.text_area(
            "",
            value="",
            height=output_height,
            key="refined_prompt_output",
            disabled=True,
        )
        st.text_area(
            "Explanation",
            value="",
            height=120,
            key="refined_explanation",
            disabled=True,
        )