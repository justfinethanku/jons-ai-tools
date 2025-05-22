# frameworks/universal_framework.py
import streamlit as st
import io
import os
import json
from notion_client_manager import NotionClientManager

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Initialize Notion manager
@st.cache_resource
def get_notion_manager():
    return NotionClientManager()

def client_selection_sidebar():
    """Add client selection to sidebar"""
    st.sidebar.title("🎯 Client Selection")
    
    notion_manager = get_notion_manager()
    
    if notion_manager.is_connected():
        clients = notion_manager.get_clients()
        
        if clients:
            client_names = ["None"] + [f"{c['name']}" for c in clients]
            selected_client_name = st.sidebar.selectbox(
                "Select client for personalized content:",
                client_names,
                key="client_selector"
            )
            
            # Store selected client in session state
            if selected_client_name != "None":
                selected_client = next(
                    (c for c in clients if c["name"] == selected_client_name), 
                    None
                )
                st.session_state["selected_client"] = selected_client
                
                # Show client info
                with st.sidebar.expander("📋 Client Details"):
                    st.write(f"**Brand Voice:** {selected_client['brand_voice']}")
                    st.write(f"**Tone:** {selected_client['tone']}")
                    st.write(f"**Industry:** {selected_client['industry']}")
                    if selected_client.get('keywords'):
                        st.write(f"**Keywords:** {', '.join(selected_client['keywords'])}")
            else:
                st.session_state["selected_client"] = None
        else:
            st.sidebar.warning("No clients found in your Notion database.")
            st.sidebar.info("Add clients to your AI Library database to get started.")
    else:
        st.sidebar.error("❌ Notion not connected")
        st.sidebar.info("Check your .streamlit/secrets.toml file")

def enhance_prompt_with_client_context(prompt_template, client_data):
    """Enhance a prompt template with client-specific context"""
    if not client_data:
        return prompt_template
    
    # Add client context to the prompt
    client_context = f"""
# CLIENT CONTEXT
- Client: {client_data.get('name', 'Unknown')}
- Brand Voice: {client_data.get('brand_voice', 'Professional')}
- Tone: {client_data.get('tone', 'Neutral')}
- Industry: {client_data.get('industry', 'General')}
- Target Audience: {client_data.get('target_audience', 'General public')}
"""
    
    if client_data.get('keywords'):
        client_context += f"- Keywords to include: {', '.join(client_data['keywords'])}\n"
    
    if client_data.get('custom_prompts'):
        client_context += f"- Custom Instructions: {client_data['custom_prompts']}\n"
    
    client_context += """
# IMPORTANT INSTRUCTIONS
- Write specifically for the target audience in the specified industry
- Match the brand voice and tone exactly
- Naturally incorporate the keywords when relevant
- Follow any custom instructions provided
- Maintain consistency with the client's brand identity

"""
    
    # Insert client context after the Role section
    if "# Role" in prompt_template:
        parts = prompt_template.split("# Role", 1)
        enhanced_prompt = parts[0] + "# Role" + parts[1].split("\n", 1)[0] + "\n\n" + client_context + "\n".join(parts[1].split("\n")[1:])
    else:
        enhanced_prompt = client_context + prompt_template
    
    return enhanced_prompt

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
    """Universal elements for all tools"""
    # Add client selection to all tools
    client_selection_sidebar()

def call_openai_api(prompt, model="gpt-4", temperature=0.2):
    """
    Call the OpenAI API
    
    Args:
        prompt (str): The prompt to send to OpenAI
        model (str, optional): The model to use. Defaults to "gpt-4".
        temperature (float, optional): Controls randomness in generation. Defaults to 0.2.
        
    Returns:
        str: The response from OpenAI
    """
    import openai
    
    # Configure the client
    openai.api_key = st.secrets["openai"]["API_KEY"]
    
    try:
        # Make the API call
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        
        # Return the generated text
        return response.choices[0].message.content
    
    except Exception as e:
        st.error(f"OpenAI API error: {str(e)}")
        return f"Error calling OpenAI API: {str(e)}"

def call_gemini_api(prompt, response_schema=None, temperature=0.2):
    """
    Call Gemini API with support for structured output using responseSchema
    
    Args:
        prompt (str): The prompt to send to Gemini
        response_schema (dict, optional): Schema for structured output
        temperature (float, optional): Controls randomness in generation
        
    Returns:
        str: The response from Gemini
    """
    import google.generativeai as genai
    import json
    from google.api_core import exceptions
    
    # Configure the Gemini API client
    genai.configure(api_key=st.secrets["google"]["GEMINI_API_KEY"])
    
    # Create generation config
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
    }
    
    # Add response schema if provided
    if response_schema:
        generation_config["response_schema"] = response_schema
        generation_config["response_mime_type"] = "application/json"
    
    try:
        # Create the model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config
        )
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Handle structured response
        if response_schema and hasattr(response, 'candidates') and response.candidates:
            # Extract JSON response
            try:
                # Some versions of the API return the response differently
                if hasattr(response.candidates[0], 'content') and hasattr(response.candidates[0].content, 'parts'):
                    json_text = response.candidates[0].content.parts[0].text
                    return json_text
                else:
                    return response.text
            except Exception as e:
                st.error(f"Error parsing structured response: {str(e)}")
                return response.text
        else:
            # Return unstructured response
            return response.text
    
    except exceptions.GoogleAPIError as e:
        st.error(f"Gemini API error: {str(e)}")
        return f"Error calling Gemini API: {str(e)}"
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return f"Error: {str(e)}"