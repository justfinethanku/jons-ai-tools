import streamlit as st
from frameworks.copy_generator_framework import run_copy_generator
from prompts.copy_prompts.social_prompts.facebook_copy import PROMPT as FACEBOOK_PROMPT
#this references the facebook prompt which is called PROMPT there but Facebook Prompt here
#Basically anytime you see--- x as z ---it means it's changing the name for whatever reason
import google.generativeai as genai
import os
import importlib.util
from frameworks.universal_framework import home_button

PROMPT_DIR = "prompts/copy_prompts/social_prompts"
platform_prompts={}

for filename in os.listdir(PROMPT_DIR):
    if filename.endswith("copy.py") or filename == "generic_social_copy.py":
        #check to see what the deal is with generic social copy
        if filename == "generic_social_copy.py":
            platform_name = "generic"
        else: 
            platform_name = filename.replace("_copy.py", "").replace("_", " ").title()
        filepath = os.path.join(PROMPT_DIR, filename)
        spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        prompt = getattr(mod, "PROMPT", None)
        if prompt:
            platform_prompts[platform_name] = prompt

def sidebar_info():
    pass
#not putting anything into the sidebar right now, this is just a placeholder or some thing like that, 
#"pass" tells it to get over it and move on to the next bullshit thing you want to accomplish
import streamlit as st
import google.generativeai as genai
import os

# ... (your dynamic prompt loading code here) ...

def run():
    st.header("Copy Generator")
    col_left, col_right = st.columns([1, 3])
   

    with col_left:
        uploaded_file = st.file_uploader("Drag & Drop a file here", type=None, label_visibility="visible")
        notes = st.text_area("Your notes (optional):", height=140)
        generate = st.button("Generate Copy")

    results = {platform: "" for platform in platform_prompts}

    if generate:
        file_text = ""
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            try:
                file_text = file_bytes.decode("utf-8")
            except Exception:
                file_text = file_bytes.decode("latin-1")

        if file_text and notes: 
            input_text = file_text + "\n\n" + notes
        elif file_text:
            input_text = file_text
        elif notes:
            input_text = notes 
        else:
            input_text = ""

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash")
        with st.spinner("Generating social copy for all platforms..."):
            for platform, prompt in platform_prompts.items():
                if "{USER_INPUT}" in prompt:
                    combined_prompt = prompt.replace("{USER_INPUT}", input_text)
                elif "{user_input}" in prompt:
                    combined_prompt = prompt.replace("{user_input}", input_text)
                else:
                    combined_prompt = f"{prompt}\n\n{input_text}"

                try:
                    response = model.generate_content(combined_prompt)
                    results[platform] = response.text.strip()
                except Exception as e:
                    results[platform] = f"Error: {e}"
    #this should pass the results of the outputs to the save outputs button
    home_button(outputs_dict=results, key_prefix="copy_tool")

    with col_right:
        for platform in platform_prompts:
            st.text_area(platform, value=results[platform], height=120, key=f"copy_gen_{platform}")