"""
@RULE:PURPOSE: Streamlit UI components for example tool with clean separation from core logic
@RULE:RESPONSIBILITY: UI rendering, user interaction, input validation, result presentation
@RULE:IMPORTS_ALLOWED: streamlit, .tool, typing, dataclasses, datetime
@RULE:IMPORTS_FORBIDDEN: core.*, main, other tools, original framework modules, shared.* (UI should be independent)
@RULE:PUBLIC_API: create_example_ui, render_input_interface, render_results
@RULE:PRIVATE_IMPL: _render_sidebar_info, _handle_action, _display_results
@RULE:NO_CROSS_TALK: core modules, other tools, main application
@RULE:DEPENDENCY_DIRECTION: ui -> tool module only (clean UI separation)
@RULE:INTERFACE_RULE: Pure UI components with no business logic
@RULE:ONE_PURPOSE: Single responsibility is example tool user interface
@RULE:STATE_MANAGEMENT: Streamlit session state for UI persistence
@RULE:USER_EXPERIENCE: Clean, intuitive interface for example tool operations
"""

# Allowed imports - Streamlit and tool module only
# import streamlit as st
# from typing import Dict, Any, Optional
# from datetime import datetime
# from .tool import ExampleTool, ExampleResult


def create_example_ui():
    """
    Create the main example tool UI interface.
    
    This function renders the complete example tool interface including
    input areas, operation selection, results display, and action buttons.
    """
    # # Render header
    # st.header("Example Tool")
    # st.write("Demonstrating rule-based architecture with file-based prompts")
    # 
    # # Initialize tool
    # if 'example_tool' not in st.session_state:
    #     st.session_state.example_tool = ExampleTool()
    # 
    # tool = st.session_state.example_tool
    # 
    # # Render main interface
    # render_input_interface(tool)
    # 
    # # Show results if they exist
    # if "example_results" in st.session_state and st.session_state["example_results"]:
    #     render_results(st.session_state["example_results"])
    pass


def render_input_interface(tool: ExampleTool):
    """
    Render the main input interface.
    
    Args:
        tool: ExampleTool instance to use for operations
    """
    # # Input section
    # st.subheader("Input")
    # 
    # # Text input
    # input_data = st.text_area("Enter data to process:", height=150)
    # 
    # # Operation selection
    # operation = st.selectbox(
    #     "Select operation:",
    #     ["process", "analyze", "validate"]
    # )
    # 
    # # Configuration options
    # with st.expander("Advanced Configuration"):
    #     temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
    #     max_retries = st.number_input("Max Retries", 1, 10, 3)
    # 
    # # Execute button
    # if st.button("Execute Operation"):
    #     if input_data.strip():
    #         _handle_action(tool, operation, input_data, {
    #             "TEMPERATURE": temperature,
    #             "MAX_RETRIES": max_retries
    #         })
    #     else:
    #         st.error("Please enter some data to process")
    pass


def render_results(results: ExampleResult):
    """
    Render the operation results.
    
    Args:
        results: ExampleResult to display
    """
    # st.subheader("Results")
    # 
    # # Input/Output comparison
    # col1, col2 = st.columns(2)
    # 
    # with col1:
    #     st.write("**Input Data:**")
    #     st.text_area("", value=results.input_data, disabled=True, height=100)
    # 
    # with col2:
    #     st.write("**Processed Data:**")
    #     st.text_area("", value=results.processed_data, disabled=True, height=100)
    # 
    # # Quality metrics
    # st.write("**Quality Metrics:**")
    # st.metric("Quality Score", f"{results.quality_score:.1f}/100")
    # 
    # # Analysis details
    # if results.analysis:
    #     st.write("**Analysis:**")
    #     st.json(results.analysis)
    # 
    # # Suggestions
    # if results.suggestions:
    #     st.write("**Suggestions:**")
    #     for suggestion in results.suggestions:
    #         st.info(f"• {suggestion}")
    # 
    # # Action buttons
    # col1, col2 = st.columns(2)
    # with col1:
    #     if st.button("Clear Results"):
    #         del st.session_state["example_results"]
    #         st.rerun()
    # 
    # with col2:
    #     # Download results
    #     download_content = _generate_download_content(results)
    #     st.download_button(
    #         "Download Results",
    #         data=download_content,
    #         file_name=f"example_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
    #         mime="text/plain"
    #     )
    pass


def _handle_action(tool: ExampleTool, operation: str, input_data: str, config: Dict[str, Any]):
    """
    Private method to handle tool operation execution.
    
    Args:
        tool: ExampleTool instance
        operation: Operation to execute
        input_data: Input data for operation
        config: Configuration parameters
    """
    # with st.spinner(f"Executing {operation} operation..."):
    #     try:
    #         if operation == "process":
    #             result = tool.example_operation(input_data, config)
    #         else:
    #             # For other operations, use general execute method
    #             from ..base_tool import ToolInput
    #             tool_input = ToolInput(
    #                 operation=operation,
    #                 parameters={"data": input_data},
    #                 configuration=config
    #             )
    #             tool_result = tool.execute(tool_input)
    #             
    #             if tool_result.success:
    #                 result = tool_result.results.get("example_result")
    #             else:
    #                 st.error(f"Operation failed: {tool_result.errors}")
    #                 return
    #         
    #         # Store results
    #         st.session_state["example_results"] = result
    #         st.success(f"{operation.capitalize()} operation completed successfully!")
    #         st.rerun()
    #         
    #     except Exception as e:
    #         st.error(f"Operation failed: {str(e)}")
    pass


def _generate_download_content(results: ExampleResult) -> str:
    """
    Private method to generate downloadable content from results.
    
    Args:
        results: ExampleResult to convert to download format
        
    Returns:
        Formatted string content for download
    """
    # content_lines = []
    # content_lines.append("=== EXAMPLE TOOL RESULTS ===")
    # content_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # content_lines.append("")
    # 
    # content_lines.append("=== INPUT DATA ===")
    # content_lines.append(results.input_data)
    # content_lines.append("")
    # 
    # content_lines.append("=== PROCESSED DATA ===")
    # content_lines.append(results.processed_data)
    # content_lines.append("")
    # 
    # content_lines.append("=== METRICS ===")
    # content_lines.append(f"Quality Score: {results.quality_score:.1f}/100")
    # content_lines.append("")
    # 
    # if results.suggestions:
    #     content_lines.append("=== SUGGESTIONS ===")
    #     for suggestion in results.suggestions:
    #         content_lines.append(f"- {suggestion}")
    #     content_lines.append("")
    # 
    # return "\n".join(content_lines)
    pass