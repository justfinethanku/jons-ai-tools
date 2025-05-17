# frameworks/universal_framework.py
# frameworks/universal_framework.py

import streamlit as st
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
#alright, let's see if this works

# Universal home button function
def home_button():
    if st.session_state.get("tool", "home") != "home":
        if st.button("🏠 ", key="home_button"):
            st.session_state.tool = "home"
            st.rerun()

def universal_ui():
    # Universal elements for all tools go here.
    # Add sidebar, global banners, or branding here in the future.
    pass  