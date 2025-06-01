"""
@RULE:PURPOSE: Unified refiner framework for rule-based tool execution
@RULE:DEPENDENCIES: unified_tool_manager, shared_utils, logging_manager
@RULE:INTERFACE: run_refiner
@RULE:NO_CROSS_TALK: individual tool implementations
"""
import streamlit as st
from frameworks.unified_tool_manager import get_unified_tool_manager, execute_unified_tool_function
from frameworks.logging_manager import get_logger

logger = get_logger("refiner_framework")

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
    refine_func=None,  # Now optional - will use unified system if None
    meta_prompt=None,  # Now optional - will load from config if None
    sidebar_info=None, # Now optional - will load from config if None
    rough_prompt_label="Rough Prompt",
    output_height=160,
):
    logger.log_operation_start("run_refiner", tool=tool_name)
    
    # Get unified tool manager and load tool if needed
    tool_manager = get_unified_tool_manager()
    
    # Try to get tool instance from unified system
    tool_instance = tool_manager.get_tool(tool_name.lower().replace(' ', '_'))
    if not tool_instance:
        # If tool not found, try to load all tools
        tool_manager.load_all_tools()
        tool_instance = tool_manager.get_tool(tool_name.lower().replace(' ', '_'))
    
    # Get tool configuration if available
    tool_config = None
    if tool_instance:
        tool_config = tool_instance['config']
        logger.info("Using unified tool configuration", tool=tool_name)
    else:
        logger.warning("Tool not found in unified system, using legacy mode", tool=tool_name)

    # Load sidebar info from config or use provided function
    if tool_config:
        config_rules = tool_config.config_rules
        
        # Display sidebar info from configuration
        with st.sidebar.expander("About this tool", expanded=True):
            sidebar_text = config_rules.get('SIDEBAR_INFO', f'Tool: {tool_name}')
            st.write(sidebar_text)
        
        with st.sidebar.expander("How to use"):
            help_text = config_rules.get('HELP_TEXT', f'1. Enter your prompt\n2. Click refine\n3. Review results')
            st.write(help_text)
        
        # Use config values for UI
        input_height = config_rules.get('INPUT_HEIGHT', 120)
        output_height = config_rules.get('OUTPUT_HEIGHT', output_height)
        button_text = config_rules.get('BUTTON_TEXT', 'Refine Prompt')
        
    else:
        # Fallback to provided sidebar function
        if sidebar_info:
            sidebar_info()
        input_height = 120
        button_text = 'Refine Prompt'

    st.header(tool_name)
    rough_prompt = st.text_area(rough_prompt_label, height=input_height)

    refine_clicked = st.button(button_text, key="refine_inside_tool")

    # Initialize session state for prompt history
    if "refined" not in st.session_state:
        st.session_state["refined"] = ""
    if "revision_history" not in st.session_state:
        st.session_state["revision_history"] = []
    if "clear_revision_input" not in st.session_state:
        st.session_state["clear_revision_input"] = False

    # Handle initial refinement
    if refine_clicked and rough_prompt.strip():
        if tool_instance:
            # Use unified tool system
            refined = execute_unified_tool_function(tool_name.lower().replace(' ', '_'), 'refine', rough_prompt)
        else:
            # Fallback to legacy function
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
            if tool_instance and tool_config.config_rules.get('ENABLE_REVISIONS', True):
                # Use unified tool system
                revised = execute_unified_tool_function(
                    tool_name.lower().replace(' ', '_'), 
                    'revise', 
                    st.session_state["refined"], 
                    revision_request
                )
            else:
                # Fallback to legacy revision system
                import tools.prompt_refiner as prompt_refiner
                revised = prompt_refiner.revise_prompt(st.session_state["refined"], revision_request)
            
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