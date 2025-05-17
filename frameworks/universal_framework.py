# frameworks/universal_framework.py
# frameworks/universal_framework.py

import streamlit as st
import io
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
#alright, let's see if this works

def outputs_to_txt_bytes(outputs_dict):
    output = io.StringIO()
    for title, content in outputs_dict.items():
        output.write(f"{title}\n")
        output.write("=" * len(title) + "\n")
        output.write(f"{content}\n\n")
    return output.getvalue().encode("utf-8")

def home_button(outputs_dict=None, key_prefix="", tool_name=None):
    if st.session_state.get("tool", "home") != "home":
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🏠 ", key=f"{key_prefix}_home_button"):
                st.session_state.tool = "home"
                st.rerun()
        with col2:
            if outputs_dict:
                file_bytes = outputs_to_txt_bytes(outputs_dict)
                from datetime import datetime
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_base = tool_name if tool_name else st.session_state.get("tool", "llm_outputs")
                file_name = f"{file_base}_{now}.txt"
                st.download_button(
                    label="💾 Save Outputs",
                    data=file_bytes,
                    file_name=file_name,
                    mime="text/plain",
                    key=f"{key_prefix}_save_outputs_download"
                )

def universal_ui():
    # Universal elements for all tools go here.
    # Add sidebar, global banners, or branding here in the future.
    pass 