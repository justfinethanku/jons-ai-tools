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
    explain_func,  # Keep for compatibility but ignore
    meta_prompt,
    explainer_prompt,  # Keep for compatibility but ignore
    sidebar_info,
    rough_prompt_label="Rough Prompt",
    show_explain=False,  # Not used anymore
    output_height=160,
):
    # Optional: Tool-specific sidebar/help
    sidebar_info()

    st.header(tool_name)
    rough_prompt = st.text_area(rough_prompt_label, height=120)

    refine_clicked = st.button("Refine Prompt", key="refine_inside_tool")

    # Initialize session state for prompt history
    if "refined" not in st.session_state:
        st.session_state["refined"] = ""
    if "revision_history" not in st.session_state:
        st.session_state["revision_history"] = []
    if "clear_revision_input" not in st.session_state:
        st.session_state["clear_revision_input"] = False

    # Handle initial refinement
    if refine_clicked and rough_prompt.strip():
        refined = refine_func(rough_prompt, meta_prompt)
        st.session_state["refined"] = refined
        st.session_state["revision_history"] = [refined]  # Start fresh history

    # Show refined prompt if it exists
    if st.session_state["refined"]:
        st.markdown("#### Refined Prompt")
        
        # Calculate dynamic height based on content
        refined_text = st.session_state["refined"]
        line_count = max(8, min(30, refined_text.count('\n') + 2))
        
        st.text_area(
            "",
            value=refined_text,
            height=round(line_count * 20),
            key="refined_prompt_output",
            disabled=True,
        )

        # Revision request section
        st.markdown("#### Request Revisions")
        
        # Clear the input if we just processed a revision
        if st.session_state.get("clear_revision_input"):
            revision_request = ""
            st.session_state["clear_revision_input"] = False
        else:
            revision_request = ""
        
        revision_request = st.text_area(
            "What would you like to change about this prompt?",
            value=revision_request,
            placeholder="e.g., 'Make it more specific', 'Add examples', 'Change the tone to be more casual', 'Include constraints about output format'",
            height=80,
            key="revision_request_input"
        )

        col1, col2 = st.columns([1, 1])
        
        with col1:
            revise_clicked = st.button("🔄 Revise Prompt", key="revise_prompt_button")
        
        with col2:
            if len(st.session_state.get("revision_history", [])) > 1:
                undo_clicked = st.button("↩️ Undo Last Change", key="undo_revision_button")
            else:
                undo_clicked = False

        # Handle revision
        if revise_clicked and revision_request.strip():
            # Import the revise function
            from tools.prompt_refiner import revise_prompt
            
            revised = revise_prompt(st.session_state["refined"], revision_request)
            st.session_state["refined"] = revised
            st.session_state["revision_history"].append(revised)
            
            # Set flag to clear input on next run
            st.session_state["clear_revision_input"] = True 
            st.rerun()

        # Handle undo
        if undo_clicked:
            if len(st.session_state["revision_history"]) > 1:
                st.session_state["revision_history"].pop()  # Remove last revision
                st.session_state["refined"] = st.session_state["revision_history"][-1]  # Go back to previous
                st.rerun()

        # Show revision count
        if len(st.session_state.get("revision_history", [])) > 1:
            st.caption(f"Revision #{len(st.session_state['revision_history']) - 1}")

    else:
        st.markdown("#### Refined Prompt")
        st.text_area(
            "",
            value="",
            height=output_height,
            key="refined_prompt_output_empty",
            disabled=True,
        )
        st.markdown("#### Request Revisions")
        st.text_area(
            "What would you like to change about this prompt?",
            value="",
            height=80,
            key="revision_request_empty",
            disabled=True,
        )