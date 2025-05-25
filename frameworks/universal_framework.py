# frameworks/universal_framework.py
import streamlit as st
import io
import os
import json
import traceback
import logging
from typing import Dict, Any, Optional, Union
from notion_client_manager import NotionClientManager
from frameworks.shared_utilities import safe_json_parse, sanitize_text_for_notion

# Configure logging for better error tracking
logging.basicConfig(level=logging.WARNING)

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Initialize Notion manager with error handling
@st.cache_resource
def get_notion_manager():
    """Get Notion manager with error boundary."""
    try:
        return NotionClientManager()
    except Exception as e:
        logging.error(f"Failed to initialize NotionClientManager: {str(e)}")
        st.error(f"❌ Failed to initialize Notion connection: {str(e)}")
        return None

def client_selection_sidebar():
    """Add client selection to sidebar"""
    st.sidebar.title("🎯 Client Selection")
    
    try:
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
    except Exception as e:
        st.sidebar.error(f"❌ Notion connection error: {str(e)}")
        st.sidebar.info("Check your .streamlit/secrets.toml file")

def enhance_prompt_with_client_context(prompt_template: str, client_data: Optional[Dict[str, Any]]) -> str:
    """Enhance a prompt template with client-specific context.
    
    Args:
        prompt_template: The base prompt template
        client_data: Dictionary containing client information
        
    Returns:
        Enhanced prompt with client context
    """
    try:
        if not client_data or not prompt_template:
            return prompt_template or ""
        
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
    except Exception as e:
        logging.error(f"Error enhancing prompt with client context: {str(e)}")
        st.warning(f"⚠️ Could not apply client context: {str(e)}")
        return prompt_template

def outputs_to_txt_bytes(outputs_dict: Dict[str, str]) -> bytes:
    """Convert outputs dictionary to text bytes with error handling.
    
    Args:
        outputs_dict: Dictionary of output title-content pairs
        
    Returns:
        UTF-8 encoded bytes of formatted text
    """
    try:
        if not outputs_dict:
            return b"No outputs available\n"
        
        output = io.StringIO()
        for title, content in outputs_dict.items():
            safe_title = sanitize_text_for_notion(str(title))
            safe_content = sanitize_text_for_notion(str(content))
            output.write(f"{safe_title}\n")
            output.write("=" * len(safe_title) + "\n")
            output.write(f"{safe_content}\n\n")
        return output.getvalue().encode("utf-8")
    except Exception as e:
        logging.error(f"Error converting outputs to bytes: {str(e)}")
        error_msg = f"Error generating output file: {str(e)}\n"
        return error_msg.encode("utf-8")

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

def call_openai_api(prompt: str, model: str = "gpt-4", temperature: float = 0.2) -> str:
    """
    Call the OpenAI API with comprehensive error handling.
    
    Args:
        prompt: The prompt to send to OpenAI
        model: The model to use. Defaults to "gpt-4".
        temperature: Controls randomness in generation. Defaults to 0.2.
        
    Returns:
        The response from OpenAI or error message
    """
    try:
        import openai
        
        # Validate inputs
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        
        # Configure the client with error handling
        try:
            api_key = st.secrets["openai"]["API_KEY"]
            if not api_key:
                raise ValueError("OpenAI API key not found in secrets")
            openai.api_key = api_key
        except KeyError:
            raise ValueError("OpenAI configuration not found in secrets.toml")
        
        # Make the API call with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                )
                
                # Validate response
                if not response.choices or not response.choices[0].message.content:
                    raise ValueError("Empty response from OpenAI")
                
                return response.choices[0].message.content
                
            except openai.error.RateLimitError:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
            except openai.error.APIError as e:
                logging.error(f"OpenAI API error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                raise
    
    except Exception as e:
        error_msg = f"OpenAI API error: {str(e)}"
        logging.error(error_msg)
        st.error(error_msg)
        return f"Error: Unable to get response from OpenAI. Please try again."

def call_gemini_api(prompt: str, response_schema: Optional[Dict] = None, temperature: float = 0.2) -> str:
    """
    Call Gemini API with comprehensive error handling and structured output support.
    
    Args:
        prompt: The prompt to send to Gemini
        response_schema: Schema for structured output
        temperature: Controls randomness in generation
        
    Returns:
        The response from Gemini or error message
    """
    try:
        import google.generativeai as genai
        import json
        from google.api_core import exceptions
        
        # Validate inputs
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        
        # Configure the Gemini API client with error handling
        try:
            api_key = st.secrets["google"]["GEMINI_API_KEY"]
            if not api_key:
                raise ValueError("Gemini API key not found in secrets")
            genai.configure(api_key=api_key)
        except KeyError:
            raise ValueError("Google configuration not found in secrets.toml")
        
        # Create generation config
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 4096,
        }
        
        # Add response schema if provided
        if response_schema:
            generation_config["response_schema"] = response_schema
            generation_config["response_mime_type"] = "application/json"
        
        # Create the model with error handling
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash-preview-05-20",
                generation_config=generation_config
            )
        except Exception as e:
            raise ValueError(f"Failed to create Gemini model: {str(e)}")
        
        # Generate content with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                
                # Validate response
                if not response or not hasattr(response, 'text'):
                    raise ValueError("Empty or invalid response from Gemini")
                
                # Handle structured response
                if response_schema and hasattr(response, 'candidates') and response.candidates:
                    try:
                        if hasattr(response.candidates[0], 'content') and hasattr(response.candidates[0].content, 'parts'):
                            json_text = response.candidates[0].content.parts[0].text
                            # Validate JSON if schema provided
                            if json_text:
                                success, parsed = safe_json_parse(json_text)
                                if success:
                                    return json_text
                            return json_text
                        else:
                            return response.text
                    except Exception as e:
                        logging.warning(f"Error parsing structured response: {str(e)}")
                        return response.text
                else:
                    # Return unstructured response
                    return response.text
                    
            except exceptions.ResourceExhausted:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
            except exceptions.GoogleAPIError as e:
                logging.error(f"Gemini API error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                raise
    
    except Exception as e:
        error_msg = f"Gemini API error: {str(e)}"
        logging.error(error_msg)
        st.error(error_msg)
        return f"Error: Unable to get response from Gemini. Please try again."