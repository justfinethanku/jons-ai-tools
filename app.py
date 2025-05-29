import streamlit as st
from frameworks.universal_framework import home_button
from frameworks.refiner_framework import run_refiner
import tools.prompt_refiner as prompt_refiner
import tools.coder_helper as coder_helper
from tools import social_copy_tool
import time

# Initialize session state
if "tool" not in st.session_state:
    st.session_state.tool = "home"

# Easter egg: Secret counter
if "secret_clicks" not in st.session_state:
    st.session_state.secret_clicks = 0

# Check if we need to show the copy generator warning
if st.session_state.get("show_copy_warning", False):
    warning_placeholder = st.empty()
    warning_placeholder.markdown("""
        <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
                    background: #000; z-index: 9999; display: flex; align-items: center; 
                    justify-content: center; overflow: hidden;">
            <div style="background: repeating-linear-gradient(0deg, #ff0000, #ff0000 2px, #000 2px, #000 4px);
                        padding: 80px; border: 8px solid #ff0; animation: borderFlash 0.1s infinite;">
                <h1 style="font-family: 'Impact', sans-serif; color: #ff0; font-size: 120px; 
                           text-align: center; margin: 0; text-transform: uppercase;
                           animation: glitchText 0.2s infinite; text-shadow: 2px 2px #f0f, -2px -2px #0ff;">
                    WARNING!
                </h1>
                <div style="background: #ff0000; padding: 20px; margin: 20px 0; 
                            animation: redFlash 0.3s infinite;">
                    <p style="font-family: 'Courier New', monospace; color: #fff; font-size: 36px; 
                              text-align: center; margin: 0; font-weight: bold;">
                        USE THIS TOOL AT YOUR OWN RISK
                    </p>
                </div>
                <p style="font-family: 'Arial Black', sans-serif; color: #0f0; font-size: 48px; 
                          text-align: center; animation: shake 0.1s infinite;
                          text-shadow: 0 0 20px #0f0;">
                    JON CODED IT AND DOESN'T KNOW<br>WHAT THE FUCK HE IS DOING
                </p>
                <div style="text-align: center; margin-top: 40px;">
                    <span style="font-family: monospace; color: #ff0; font-size: 24px; 
                                animation: blink 0.2s infinite;">
                        ⚠️ SYSTEM MALFUNCTION PROBABLE ⚠️
                    </span>
                </div>
                <div style="position: absolute; top: 20px; left: 20px; color: #0ff; 
                            font-family: monospace; animation: flicker 0.1s infinite;">
                    ERROR CODE: 0xDEADBEEF
                </div>
                <div style="position: absolute; bottom: 20px; right: 20px; color: #f0f; 
                            font-family: monospace; animation: flicker 0.15s infinite;">
                    KERNEL PANIC IMMINENT
                </div>
            </div>
        </div>
        <style>
            @keyframes glitchText {
                0% { transform: translate(0); }
                20% { transform: translate(-2px, 2px); }
                40% { transform: translate(-2px, -2px); }
                60% { transform: translate(2px, 2px); }
                80% { transform: translate(2px, -2px); }
                100% { transform: translate(0); }
            }
            @keyframes borderFlash {
                0%, 49% { border-color: #ff0; }
                50%, 100% { border-color: #f00; }
            }
            @keyframes redFlash {
                0%, 49% { background: #ff0000; }
                50%, 100% { background: #660000; }
            }
            @keyframes shake {
                0% { transform: translateX(0); }
                25% { transform: translateX(-10px); }
                50% { transform: translateX(10px); }
                75% { transform: translateX(-5px); }
                100% { transform: translateX(0); }
            }
            @keyframes blink {
                0%, 49% { opacity: 1; }
                50%, 100% { opacity: 0; }
            }
            @keyframes flicker {
                0%, 90% { opacity: 1; }
                91%, 100% { opacity: 0.3; }
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Wait 5 seconds
    time.sleep(5)
    
    # Clear the warning and set tool to Copy Generator
    warning_placeholder.empty()
    st.session_state["show_copy_warning"] = False
    st.session_state.tool = "Copy Generator"
    st.rerun()

# Client selection removed
home_button()

if st.session_state.tool == "home":
    # Make the buttons STUPIDLY MASSIVE - override ALL Streamlit defaults
    st.markdown("""
        <style>
        /* Target ALL button elements more aggressively */
        .stButton > button {
            font-size: 96px !important;
            height: 20vh !important;
            min-height: 180px !important;
            width: 20vh !important;
            min-width: 180px !important;
            font-weight: 900 !important;
            border: 8px solid #0ff !important;
            border-radius: 30px !important;
            text-transform: uppercase !important;
            letter-spacing: 5px !important;
            transition: all 0.3s !important;
            background: linear-gradient(45deg, #1a1a1a, #2d2d2d) !important;
            color: #0ff !important;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.8) !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
            padding: 20px !important;
            white-space: pre-line !important;
            line-height: 1.0 !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
        }
        .stButton > button:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 0 50px rgba(0, 255, 255, 1) !important;
            border-color: #fff !important;
            background: linear-gradient(45deg, #2d2d2d, #1a1a1a) !important;
        }
        /* Make sure the button container is also square */
        .stButton {
            height: 20vh !important;
            min-height: 180px !important;
            width: 20vh !important;
            min-width: 180px !important;
            margin: 0 auto !important;
        }
        /* Space between columns */
        div[data-testid="column"] {
            padding: 20px !important;
        }
        /* Override any default button styling */
        button[kind="primary"], button[kind="secondary"] {
            font-size: 96px !important;
            height: 20vh !important;
            min-height: 180px !important;
            width: 20vh !important;
            min-width: 180px !important;
        }
        /* Style for subtitle text */
        .button-subtitle {
            font-size: 18px !important;
            font-weight: normal !important;
            letter-spacing: 2px !important;
            opacity: 0.8 !important;
            margin-top: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Giant title
    st.markdown("""
        <h1 style="text-align: center; font-size: 64px; color: #fff; 
                   font-family: Impact, sans-serif; text-shadow: 4px 4px 8px rgba(0,0,0,0.8);
                   margin-bottom: 50px;">
            a work in progress
        </h1>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button("PROMPT\nREFINER\n\nCURRENTLY ONLINE", key="prompt_refiner_btn", help="Refine your prompts"):
            st.session_state.tool = "Prompt Refiner"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("CODER\nHELPER\n\nCURRENTLY ONLINE", key="coder_helper_btn", help="Get coding assistance"):
            st.session_state.tool = "Coder Helper"
            st.rerun()
    with col2:
        if st.button("COPY\nGENERATOR\n\nCURRENTLY ONLINE", key="copy_generator_btn", help="Generate social media copy"):
            st.session_state["show_copy_warning"] = True
            st.rerun()

if st.session_state.tool == "Prompt Refiner":
    run_refiner(
        tool_name="Prompt Refiner",
        refine_func=prompt_refiner.refine_prompt,
        meta_prompt=prompt_refiner.META_PROMPT,
        sidebar_info=prompt_refiner.sidebar_info,
    )

if st.session_state.tool == "Coder Helper":
    run_refiner(
        tool_name="Coder Helper",
        refine_func=coder_helper.refine_prompt,
        meta_prompt=coder_helper.META_PROMPT,
        sidebar_info=coder_helper.sidebar_info,
    )

if st.session_state.tool == "Copy Generator":
    social_copy_tool.run()

# Easter egg: Secret button
st.markdown("---")
col1, col2, col3 = st.columns([5, 1, 5])
with col2:
    if st.button(".", key="secret_button", help="???"):
        st.session_state.secret_clicks += 1
        
        if st.session_state.secret_clicks == 5:
            st.balloons()
            st.markdown("""
                <div style="text-align: center; padding: 20px;">
                    <h1 style="color: #ff00ff; animation: rainbow 2s infinite;">
                        🎉 YOU FOUND THE SECRET! 🎉
                    </h1>
                    <p style="font-size: 24px; color: #00ff00;">
                        Jon's code is held together by<br>
                        duct tape, prayers, and this button.
                    </p>
                    <p style="font-size: 18px; color: #00ffff;">
                        Achievement Unlocked: Button Masher!
                    </p>
                </div>
                <style>
                    @keyframes rainbow {
                        0% { color: #ff0000; }
                        17% { color: #ff8800; }
                        33% { color: #ffff00; }
                        50% { color: #00ff00; }
                        67% { color: #0088ff; }
                        83% { color: #8800ff; }
                        100% { color: #ff0000; }
                    }
                </style>
            """, unsafe_allow_html=True)
            st.session_state.secret_clicks = 0